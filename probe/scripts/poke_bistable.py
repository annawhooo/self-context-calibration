"""Poke the run-level lockstep effect: two sensitive items, sonnet,
K=10 per wave, six waves spaced eight minutes apart, one launch.

Run from the repo root in a terminal where ANTHROPIC_API_KEY is set:
  python probe\\scripts\\poke_bistable.py [waves] [interval_seconds]

Appends rows (plus wave index) to convergence/results/poke_bistable.jsonl
and prints a per-wave summary. Reuses the collection call path verbatim
(collect_row), so request shaping and parsing are byte-identical to
collection.
"""
import sys
import os
import json
import time
import collections

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from convergence.collect import collect_row  # noqa: E402
from items.items import ITEMS  # noqa: E402

ITEM_IDS = ["eq_alert_vuln_gating_v2", "eq_alert_fraud_scoring_v2"]
MODEL_ID = "claude-sonnet-4-6"
K = 10
OUT = os.path.join(ROOT, "convergence", "results", "poke_bistable.jsonl")


def main():
    waves = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    interval = int(sys.argv[2]) if len(sys.argv) > 2 else 480

    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        print("ANTHROPIC_API_KEY is not set. Launch from a terminal "
              "with the key in the environment; no request was issued.")
        sys.exit(1)

    with open(os.path.join(ROOT, "convergence", "models.json"),
              encoding="utf-8") as f:
        roster = json.load(f)["models"]
    m = next(x for x in roster if x["model"] == MODEL_ID)
    items = [it for it in ITEMS if it["id"] in ITEM_IDS]
    if len(items) != len(ITEM_IDS):
        print("item ids not found in bank:", ITEM_IDS)
        sys.exit(1)

    run_id = "poke_" + time.strftime("%Y-%m-%dT%H-%M-%S", time.gmtime())
    print(f"{run_id}: {waves} waves, {interval}s apart, "
          f"{len(items)} items x K={K} on {MODEL_ID}")

    for w in range(waves):
        wave_start = time.strftime("%H:%M:%S", time.localtime())
        for it in items:
            texts, parsed = [], collections.Counter()
            with open(OUT, "a", encoding="utf-8") as f:
                for k in range(K):
                    row, _echo = collect_row(m, "A", it, k, key, run_id)
                    row["wave"] = w
                    f.write(json.dumps(row) + "\n")
                    parsed[row.get("parsed")] += 1
                    texts.append(row.get("raw_text", ""))
            lens = sorted(len(t) for t in texts)
            fmt = "terse" if lens[len(lens) // 2] < 50 else "verbose"
            print(f"  wave {w} {wave_start} {it['id']:28s} "
                  f"{dict(parsed)}  distinct {len(set(texts)):2d}  "
                  f"{fmt}  lens {lens[0]}..{lens[-1]}", flush=True)
        if w < waves - 1:
            time.sleep(interval)
    print("rows appended to", OUT)


if __name__ == "__main__":
    main()
