"""
Daily-probe tests for the monitor: alarm firing, auto-disambiguation on all
three rerun outcomes, sentinel handling, echo-change verdict, verdict
schema, and exit codes. No network: requests.post is a scripted fake
(monitor_testkit); any stray call or exhausted script fails loudly.

Pins:
  1. CLEAN: no alarm item over its band; exit 0; sentinel movement is
     reported descriptively and fires nothing (sentinel never a sole
     trigger: no disambiguation calls are spent on it).
  2. EVENT: breached item whose rerun matches the probe and not the
     baseline; exit 1; re-baseline is recommended on stderr, never done.
  3. TRANSIENT: rerun matches the baseline; exit 0.
  4. UNSTABLE: rerun matches neither; exit 1.
  5. ECHO_CHANGE: an id change halts that model's probe immediately and is
     its own verdict; exit 1.
  6. ERROR: a missing baseline is an ERROR verdict; mixed with an EVENT on
     another model the run exits 2 (ERROR dominates). A missing credential
     fails closed with zero requests and still lands one ERROR line per
     model.
  7. Verdict lines carry the pinned schema: date, model, model_id_echo,
     verdict, breached items with observed vs band, sentinel summary,
     calls made, run ids; every verdict is from the pinned enum.

Run: python probe/tests/test_monitor_probe.py   (plain asserts, exit 1 on
failure; also collectable by pytest).
"""
import os
import sys
import shutil
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from monitor_testkit import (  # noqa: E402
    ECHO, EnvGuard, Patched, ScriptedPost, make_item, make_model, monitor,
    providers, read_jsonl,
)

LINE_FIELDS = ("date", "model", "model_id_echo", "verdict", "breached",
               "sentinels", "unparsed", "calls", "run_ids")


def build_baseline(mid, scripts, items, baselines, rows):
    """Qualify a baseline for one test model through the real baseline
    command, with scripted answers."""
    with Patched(ScriptedPost(scripts)):
        code = monitor.run_baseline([make_model(mid)], items=items,
                                    baselines_dir=baselines, rows_dir=rows)
    assert code == 0, "baseline build for %s failed (%d)" % (mid, code)


def run():
    fails = []

    def check(name, cond, got=None):
        if cond:
            print("  PASS: %s" % name)
        else:
            print("  FAIL: %s | got %r" % (name, got))
            fails.append(name)

    tmp = tempfile.mkdtemp(prefix="monitor_probe_test_")
    baselines = os.path.join(tmp, "baselines")
    rows = os.path.join(tmp, "rows")

    def probe(mid, scripts, items, verdicts_name, echo_seq=None):
        verdicts_path = os.path.join(tmp, verdicts_name)
        post = ScriptedPost(scripts, echo_seq=echo_seq)
        with Patched(post):
            code = monitor.run_probe([make_model(mid)], items=items,
                                     baselines_dir=baselines, rows_dir=rows,
                                     verdicts_path=verdicts_path)
        return code, read_jsonl(verdicts_path), post

    try:
        print("=== CLEAN, and sentinel never a sole trigger ===")
        items = [make_item("it_alarm"), make_item("it_wild")]
        build_baseline("m-clean",
                       {"it_alarm": ["A"] * 20,
                        "it_wild": ["A"] * 10 + ["B"] * 10 + ["C"] * 10},
                       items, baselines, rows)
        # Probe: the alarm item sits on its baseline; the sentinel goes
        # somewhere entirely new. Only 10 letters per item are scripted, so
        # any disambiguation attempt would exhaust the script loudly.
        code, lines, post = probe("m-clean",
                                  {"it_alarm": ["A"] * 10,
                                   "it_wild": ["D"] * 10},
                                  items, "verdicts_clean.jsonl")
        check("CLEAN exits 0", code == 0, code)
        line = lines[-1]
        check("verdict CLEAN despite sentinel movement",
              line["verdict"] == "CLEAN", line["verdict"])
        check("sentinel movement fired no disambiguation (20 calls, no "
              "rerun run id)", len(post.calls) == 20
              and sorted(line["run_ids"]) == ["probe"],
              (len(post.calls), line["run_ids"]))
        check("sentinel reported descriptively with observed vs band",
              line["sentinels"]["it_wild"]["observed_tvd"] > 0
              and "p99" in line["sentinels"]["it_wild"], line["sentinels"])
        check("no breached items on a clean day", line["breached"] == [])

        print("=== EVENT: rerun matches the probe, not the baseline ===")
        items = [make_item("it_alarm")]
        build_baseline("m-event", {"it_alarm": ["A"] * 20}, items,
                       baselines, rows)
        code, lines, post = probe("m-event",
                                  {"it_alarm": ["B"] * 10 + ["B"] * 10},
                                  items, "verdicts_event.jsonl")
        check("EVENT exits 1", code == 1, code)
        line = lines[-1]
        check("verdict EVENT", line["verdict"] == "EVENT", line["verdict"])
        b = line["breached"][0]
        check("breached item names observed vs band",
              b["item_id"] == "it_alarm" and b["observed_tvd"] == 1.0
              and 0 < b["p99"] < 1.0, b)
        check("item verdict EVENT with both rerun distances recorded",
              b["item_verdict"] == "EVENT"
              and b["rerun_tvd_vs_probe"] == 0.0
              and b["rerun_tvd_vs_baseline"] == 1.0, b)
        check("disambiguation spent exactly one extra bank pass "
              "(10 + 10 calls)", len(post.calls) == 20
              and line["calls"] == 20, (len(post.calls), line["calls"]))
        check("rerun run id recorded",
              sorted(line["run_ids"]) == ["probe", "rerun"],
              line["run_ids"])

        print("=== TRANSIENT: rerun matches the baseline ===")
        build_baseline("m-transient", {"it_alarm": ["A"] * 20}, items,
                       baselines, rows)
        code, lines, post = probe("m-transient",
                                  {"it_alarm": ["B"] * 10 + ["A"] * 10},
                                  items, "verdicts_transient.jsonl")
        check("TRANSIENT exits 0", code == 0, code)
        line = lines[-1]
        check("verdict TRANSIENT, logged, no alarm",
              line["verdict"] == "TRANSIENT"
              and line["breached"][0]["item_verdict"] == "TRANSIENT",
              line)

        print("=== UNSTABLE: rerun matches neither ===")
        build_baseline("m-unstable", {"it_alarm": ["A"] * 20}, items,
                       baselines, rows)
        code, lines, post = probe("m-unstable",
                                  {"it_alarm": ["B"] * 10 + ["C"] * 10},
                                  items, "verdicts_unstable.jsonl")
        check("UNSTABLE exits 1", code == 1, code)
        line = lines[-1]
        check("verdict UNSTABLE, item flagged for sentinel review",
              line["verdict"] == "UNSTABLE"
              and line["breached"][0]["item_verdict"] == "UNSTABLE", line)

        print("=== ECHO_CHANGE: its own verdict, immediate halt ===")
        build_baseline("m-echo", {"it_alarm": ["A"] * 20}, items,
                       baselines, rows)
        code, lines, post = probe("m-echo", {"it_alarm": ["A"] * 10},
                                  items, "verdicts_echo.jsonl",
                                  echo_seq=[ECHO] * 3 + ["echo-new"])
        check("ECHO_CHANGE exits 1", code == 1, code)
        line = lines[-1]
        check("verdict ECHO_CHANGE", line["verdict"] == "ECHO_CHANGE",
              line["verdict"])
        check("probe halted immediately (4 calls)",
              len(post.calls) == 4 and line["calls"] == 4,
              (len(post.calls), line["calls"]))
        check("echo change names reference and divergent ids",
              line["echo_change"]["reference"] == ECHO
              and line["echo_change"]["divergent"] == "echo-new",
              line.get("echo_change"))

        print("=== ERROR: missing baseline; ERROR dominates mixed exits ===")
        verdicts_path = os.path.join(tmp, "verdicts_mixed.jsonl")
        post = ScriptedPost({"it_alarm": ["B"] * 10 + ["B"] * 10})
        with Patched(post):
            code = monitor.run_probe(
                [make_model("m-event"), make_model("m-nobaseline")],
                items=items, baselines_dir=baselines, rows_dir=rows,
                verdicts_path=verdicts_path)
        lines = read_jsonl(verdicts_path)
        check("mixed EVENT + ERROR exits 2", code == 2, code)
        check("one line per model",
              [ln["model"] for ln in lines]
              == ["m-event", "m-nobaseline"], lines)
        check("missing baseline is an ERROR verdict naming the fix",
              lines[1]["verdict"] == "ERROR"
              and "baseline" in lines[1]["error"], lines[1])

        print("=== ERROR: missing credential, fail closed, zero requests ===")
        verdicts_path = os.path.join(tmp, "verdicts_cred.jsonl")
        bomb = ScriptedPost({})
        orig = providers.requests.post
        providers.requests.post = bomb
        try:
            with EnvGuard(remove=["ANTHROPIC_API_KEY"]):
                code = monitor.run_probe([make_model("m-event")],
                                         items=items,
                                         baselines_dir=baselines,
                                         rows_dir=rows,
                                         verdicts_path=verdicts_path)
        finally:
            providers.requests.post = orig
        lines = read_jsonl(verdicts_path)
        check("missing credential exits 2", code == 2, code)
        check("zero requests issued", bomb.calls == [], len(bomb.calls))
        check("ERROR line names the variable, calls 0",
              lines[0]["verdict"] == "ERROR"
              and "ANTHROPIC_API_KEY" in lines[0]["error"]
              and lines[0]["calls"] == 0, lines[0])

        print("=== verdict schema ===")
        all_lines = []
        for name in ("verdicts_clean.jsonl", "verdicts_event.jsonl",
                     "verdicts_transient.jsonl", "verdicts_unstable.jsonl",
                     "verdicts_echo.jsonl", "verdicts_mixed.jsonl",
                     "verdicts_cred.jsonl"):
            all_lines.extend(read_jsonl(os.path.join(tmp, name)))
        check("every line carries the pinned fields",
              all(all(f in ln for f in LINE_FIELDS) for ln in all_lines),
              [sorted(ln) for ln in all_lines if
               not all(f in ln for f in LINE_FIELDS)])
        check("every verdict is from the pinned enum",
              all(ln["verdict"] in monitor.VERDICTS for ln in all_lines),
              sorted({ln["verdict"] for ln in all_lines}))
        check("every non-error line echoes the served model id",
              all(ln["model_id_echo"] == ECHO for ln in all_lines
                  if ln["verdict"] not in ("ERROR",)),
              [ln["model_id_echo"] for ln in all_lines])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    print("FAILURES: %d %s" % (len(fails), fails if fails else "- ALL PASS"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(run())


def test_monitor_probe():  # pytest entry point
    assert run() == 0
