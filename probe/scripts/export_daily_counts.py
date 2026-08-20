"""Export per-slot daily answer counts from the raw monitor rows.

The raw rows under probe/monitor/rows/ are gitignored because they embed
full model replies. This script derives the committable part: for every
(date, model, item, phase) the A/B/C/D answer counts and the unparsed
count. No response text, no timestamps beyond the date, nothing else
from the rows. The output, probe/monitor/derived/daily_counts.jsonl, is
the public dataset that makes the monitor's statistics regenerable
without publishing model output.

One line per (date, model, phase, item), sorted on exactly that key so
reruns produce byte-identical output for unchanged inputs. Covers the
monitor_probe and monitor_rerun phases of probe_*.jsonl; the baseline
runs are already committed per item inside baselines/<model>.json.

Run from the repo root:
  python probe/scripts/export_daily_counts.py
Verify determinism by running twice and comparing bytes.
"""
import os
import json
import glob
import collections

HERE = os.path.dirname(os.path.abspath(__file__))
MONITOR = os.path.normpath(os.path.join(HERE, os.pardir, "monitor"))
ROWS = os.path.join(MONITOR, "rows")
OUT = os.path.join(MONITOR, "derived", "daily_counts.jsonl")
OPTIONS = ("A", "B", "C", "D")
PHASES = ("monitor_probe", "monitor_rerun")


def main():
    counts = {}
    for path in sorted(glob.glob(os.path.join(ROWS, "probe_*.jsonl"))):
        date = os.path.basename(path)[len("probe_"):-len(".jsonl")]
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                r = json.loads(line)
                phase = r.get("phase")
                if phase not in PHASES:
                    continue
                key = (date, r["model"], phase, r["item_id"])
                rec = counts.setdefault(
                    key, {o: 0 for o in OPTIONS} | {"unparsed": 0})
                p = r.get("parsed")
                if p in OPTIONS:
                    rec[p] += 1
                else:
                    rec["unparsed"] += 1

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        for key in sorted(counts):
            date, model, phase, item = key
            rec = counts[key]
            row = {"date": date, "model": model, "phase": phase,
                   "item_id": item,
                   "counts": {o: rec[o] for o in OPTIONS if rec[o]},
                   "n": sum(rec[o] for o in OPTIONS),
                   "unparsed": rec["unparsed"]}
            fh.write(json.dumps(row, sort_keys=True) + "\n")
    print("wrote %d slot-day lines to %s" % (
        len(counts), os.path.relpath(OUT)))


if __name__ == "__main__":
    main()
