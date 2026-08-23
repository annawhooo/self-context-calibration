"""
Pins for the verdict gate in probe/scripts/export_daily_counts.py.
No network; runs against a synthetic rows/ and verdicts.jsonl in a
temp directory with the module's path constants patched.

Pins:
  1. Rows for a (date, model) with a verdict line export normally.
  2. Rows for a (date, model) with NO verdict line are excluded, so a
     mid-probe export cannot publish half-sampled items; the skip is
     reported on stdout, never silent.
  3. An ERROR verdict still counts as a finished model-day: its rows
     (if any existed) would export. The gate keys on line presence,
     not verdict value.
  4. Determinism: two runs over unchanged inputs produce identical
     bytes.

Run: python probe/tests/test_export_gating.py   (plain asserts, exit 1
on failure; also collectable by pytest).
"""
import os
import io
import sys
import json
import tempfile
import importlib.util
import contextlib

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.normpath(os.path.join(
    HERE, os.pardir, "scripts", "export_daily_counts.py"))
spec = importlib.util.spec_from_file_location("export_daily_counts",
                                              SCRIPT)
export = importlib.util.module_from_spec(spec)
spec.loader.exec_module(export)


def row(model, item, parsed):
    return json.dumps({"model": model, "item_id": item,
                       "phase": "monitor_probe", "parsed": parsed})


def verdict(date, model, v="CLEAN"):
    return json.dumps({"date": date, "model": model, "verdict": v})


def run_export(tmp, rows_by_date, verdict_lines):
    rows_dir = os.path.join(tmp, "rows")
    os.makedirs(rows_dir, exist_ok=True)
    for date, lines in rows_by_date.items():
        with open(os.path.join(rows_dir, "probe_%s.jsonl" % date),
                  "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
    with open(os.path.join(tmp, "verdicts.jsonl"), "w",
              encoding="utf-8") as fh:
        fh.write("\n".join(verdict_lines) + "\n")
    export.ROWS = rows_dir
    export.VERDICTS = os.path.join(tmp, "verdicts.jsonl")
    export.OUT = os.path.join(tmp, "daily_counts.jsonl")
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        export.main()
    with open(export.OUT, encoding="utf-8") as fh:
        out_rows = [json.loads(l) for l in fh]
    return out_rows, stdout.getvalue()


def main():
    with tempfile.TemporaryDirectory() as tmp:
        rows = {"2026-08-23": (
            [row("done-model", "item_a", "A")] * 10
            + [row("running-model", "item_a", "B")] * 4
            + [row("error-model", "item_a", "C")] * 2)}
        verdicts = [verdict("2026-08-23", "done-model"),
                    verdict("2026-08-23", "error-model", "ERROR")]
        out, log = run_export(tmp, rows, verdicts)

        models = {r["model"] for r in out}
        assert "done-model" in models                        # pin 1
        assert "running-model" not in models                 # pin 2
        assert "skipped 4 rows for 2026-08-23 running-model" in log
        assert "error-model" in models                       # pin 3
        done = [r for r in out if r["model"] == "done-model"]
        assert done[0]["counts"] == {"A": 10} and done[0]["n"] == 10

        out2, _ = run_export(tmp, rows, verdicts)            # pin 4
        assert out == out2
    print("all export gating pins hold")


if __name__ == "__main__":
    main()
