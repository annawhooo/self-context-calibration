"""
Baseline qualification tests for the monitor. No network: requests.post is
a scripted fake (monitor_testkit); any stray call or exhausted script fails
loudly.

Pins:
  1. Two-run qualification: an in-band item qualifies for the alarm set
     with run1+run2 pooled as the baseline distribution and no third run.
  2. All three third-run outcomes for an out-of-band item, in the handoff's
     bullet order:
       - third matches run2, not run1 -> drift event straddled calibration;
         baseline is the post-event state (run2+run3), event recorded.
       - third matches run1 -> transient; pooled baseline, item qualified.
       - matches neither -> item classed sentinel.
  3. The baseline file is a qualification record: distributions, bands,
     item classes, seeds, dates, run ids, and the echoed model id are all
     present; only the third-run items cost a third run (call arithmetic).
  4. Echo tripwire during a baseline run: the run halts, no baseline is
     written, exit 1.
  5. Parse collapse (an item with zero parsed samples) is an error: no
     baseline written, exit 2.

Run: python probe/tests/test_monitor_baseline.py   (plain asserts, exit 1
on failure; also collectable by pytest).
"""
import os
import sys
import json
import shutil
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from monitor_testkit import (  # noqa: E402
    ECHO, Patched, ScriptedPost, make_item, make_model, monitor, read_jsonl,
)


def run():
    fails = []

    def check(name, cond, got=None):
        if cond:
            print("  PASS: %s" % name)
        else:
            print("  FAIL: %s | got %r" % (name, got))
            fails.append(name)

    tmp = tempfile.mkdtemp(prefix="monitor_baseline_test_")
    baselines = os.path.join(tmp, "baselines")
    rows = os.path.join(tmp, "rows")
    try:
        print("=== qualification: in-band, and all three third-run outcomes ===")
        model = make_model("m-base")
        items = [make_item(i) for i in
                 ("it_stable", "it_drift", "it_transient", "it_wild")]
        # run1 pops the first 10 letters per item, run2 the next 10, run3
        # (out-of-band items only) the last 10.
        post = ScriptedPost({
            "it_stable": ["A"] * 20,                          # in band
            "it_drift": ["A"] * 10 + ["B"] * 10 + ["B"] * 10,  # 3rd = run2
            "it_transient": ["A"] * 10 + ["B"] * 10 + ["A"] * 10,  # 3rd = run1
            "it_wild": ["A"] * 10 + ["B"] * 10 + ["C"] * 10,   # 3rd = neither
        })
        with Patched(post):
            code = monitor.run_baseline([model], items=items,
                                        baselines_dir=baselines,
                                        rows_dir=rows)
        check("baseline exits 0", code == 0, code)
        check("third run costs only the three out-of-band items "
              "(4*10 + 4*10 + 3*10 = 110 calls)", len(post.calls) == 110,
              len(post.calls))

        path = monitor.baseline_path("m-base", baselines)
        check("baseline file written", os.path.exists(path), path)
        with open(path, encoding="utf-8") as f:
            b = json.load(f)

        rec = b["items"]["it_stable"]
        check("in-band item classed alarm", rec["class"] == "alarm", rec)
        check("in-band baseline is run1+run2 pooled",
              rec["baseline_counts"] == {"A": 20} and rec["n"] == 20,
              rec["baseline_counts"])
        check("in-band item ran no third run",
              rec["qualification"]["third_run"] is None)
        check("in-band observed run-pair TVD is 0",
              rec["qualification"]["observed_run_pair_tvd"] == 0.0)

        rec = b["items"]["it_drift"]
        third = rec["qualification"]["third_run"]
        check("drift item: third matches run2, not run1",
              third["outcome"] == "drift_during_calibration", third)
        check("drift item stays in the alarm set", rec["class"] == "alarm")
        check("drift baseline is the post-event state (run2+run3)",
              rec["baseline_counts"] == {"B": 20}, rec["baseline_counts"])
        check("drift event logged in the baseline file",
              len(b["events"]) == 1
              and b["events"][0]["item_id"] == "it_drift", b["events"])

        rec = b["items"]["it_transient"]
        third = rec["qualification"]["third_run"]
        check("transient item: third matches run1",
              third["outcome"] == "transient", third)
        check("transient item qualified with pooled baseline",
              rec["class"] == "alarm"
              and rec["baseline_counts"] == {"A": 20, "B": 10}
              and rec["n"] == 30, rec["baseline_counts"])

        rec = b["items"]["it_wild"]
        third = rec["qualification"]["third_run"]
        check("matches-neither item classed sentinel",
              rec["class"] == "sentinel" and third["outcome"] == "sentinel",
              (rec["class"], third))
        check("sentinel still carries a pooled distribution and band",
              rec["baseline_counts"] == {"A": 10, "B": 10, "C": 10}
              and "p99" in rec["band"], rec)

        print("=== the baseline file is a qualification record ===")
        for field in ("model", "provider", "arm", "k", "sims", "smooth",
                      "seed_base", "seed_rule", "date", "run_ids",
                      "model_id_echo", "events", "items"):
            check("baseline field %s present" % field, field in b,
                  sorted(b))
        check("echoed model id recorded", b["model_id_echo"] == ECHO,
              b["model_id_echo"])
        check("run ids recorded for all three runs",
              sorted(b["run_ids"]) == ["run1", "run2", "run3"],
              b["run_ids"])
        check("k pinned at 10", b["k"] == 10, b["k"])
        rec = b["items"]["it_drift"]
        check("qualification seed recorded per item",
              rec["qualification"]["seed"]
              == monitor.item_seed("m-base", "it_drift"),
              rec["qualification"]["seed"])
        check("run2 band seed recorded on the third-run record",
              rec["qualification"]["third_run"]["run2_seed"]
              == monitor.item_seed("m-base", "it_drift", "run2"))
        check("monitoring band seed recorded per item",
              rec["band"]["seed"]
              == monitor.item_seed("m-base", "it_drift", "band"))
        check("bands present per item",
              all("p95" in r["band"] and "p99" in r["band"]
                  and "p95" in r["qualification"] and "p99" in r["qualification"]
                  for r in b["items"].values()))
        rows_files = os.listdir(rows)
        check("raw rows written under rows/ (one baseline file)",
              len(rows_files) == 1, rows_files)
        rows_data = read_jsonl(os.path.join(rows, rows_files[0]))
        check("110 durable rows on disk", len(rows_data) == 110,
              len(rows_data))
        phases = {r["phase"] for r in rows_data}
        check("rows carry the three baseline phases",
              phases == {"monitor_baseline_run1", "monitor_baseline_run2",
                         "monitor_baseline_run3"}, phases)

        print("=== echo tripwire during baseline: halt, nothing written ===")
        shutil.rmtree(baselines, ignore_errors=True)
        model = make_model("m-echo")
        post = ScriptedPost({"it_stable": ["A"] * 20},
                            echo_seq=[ECHO] * 5 + ["echo-changed"])
        with Patched(post):
            code = monitor.run_baseline([model],
                                        items=[make_item("it_stable")],
                                        baselines_dir=baselines,
                                        rows_dir=rows)
        check("echo change exits 1", code == 1, code)
        check("halt is immediate (6 calls)", len(post.calls) == 6,
              len(post.calls))
        check("no baseline written after the halt",
              not os.path.exists(monitor.baseline_path("m-echo", baselines)))

        print("=== parse collapse during baseline: error, exit 2 ===")
        model = make_model("m-collapse")
        post = ScriptedPost({"it_stable": ["Z"] * 20})  # never parseable
        with Patched(post):
            code = monitor.run_baseline([model],
                                        items=[make_item("it_stable")],
                                        baselines_dir=baselines,
                                        rows_dir=rows)
        check("parse collapse exits 2", code == 2, code)
        check("no baseline written on parse collapse",
              not os.path.exists(monitor.baseline_path("m-collapse",
                                                       baselines)))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    print("FAILURES: %d %s" % (len(fails), fails if fails else "- ALL PASS"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(run())


def test_monitor_baseline():  # pytest entry point
    assert run() == 0
