"""Numbers the paper takes from the raw per-call rows.

The raw rows (probe/monitor/rows/, gitignored because they embed
full model replies) are not part of the public artifact. Every
number this script prints is therefore reproducible from the
operator's retained rows only, and the paper says so where it uses
one. Reads rows from ROWS_DIR (default probe/monitor/rows under the
repo) through the PAPER_DATA_THROUGH date.

Printed: row counts by phase; per-model constancy of the serving
covariates the rows carry (echoed model id, reasoning flag, host,
temperature); the item-level probe-to-rerun gap (last probe sample
of a breached item to the first rerun sample of the same item, the
persistence an EVENT actually certifies); and the response-format
observation on the sonnet vulnerability-gating and fraud-scoring
items (response length by parsed answer).

  ROWS_DIR=<path> PAPER_DATA_THROUGH=2026-09-26 \\
      python paper/figures/raw_row_census.py
"""
import collections
import datetime as dt
import glob
import json
import os
import statistics

import figdata as fd

ROWS = os.environ.get("ROWS_DIR",
                      os.path.join(fd.REPO, "probe", "monitor", "rows"))
FORMAT_ITEMS = ("eq_alert_vuln_gating_v2", "eq_alert_fraud_scoring_v2")


def rows():
    for path in sorted(glob.glob(os.path.join(ROWS, "*.jsonl"))):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                r = json.loads(line)
                if r["ts"][:10] <= fd.DATA_THROUGH:
                    yield r


def main():
    print("rows dir %s, through %s" % (ROWS, fd.DATA_THROUGH))
    phase = collections.Counter()
    cov = collections.defaultdict(lambda: collections.defaultdict(
        collections.Counter))
    first_div = {}
    by_item = collections.defaultdict(list)
    fmt = collections.defaultdict(list)
    n = 0
    for r in rows():
        n += 1
        phase[r["phase"]] += 1
        m = r["model"]
        for key in ("model_id_exact", "reasoning_detected", "host",
                    "temperature_sent"):
            cov[m][key][repr(r.get(key))] += 1
        if r.get("model_id_exact") != m and m not in first_div:
            first_div[m] = (r["ts"][:10], r.get("model_id_exact"))
        if r["phase"] in ("monitor_probe", "monitor_rerun"):
            by_item[(r["ts"][:10], m, r["item_id"])].append(
                (r["phase"], r["ts"]))
        if m == "claude-sonnet-4-6" and r["item_id"] in FORMAT_ITEMS:
            fmt[r["item_id"]].append((r["parsed"], len(r["raw_text"])))
    print("rows total %d  by phase %s" % (n, dict(sorted(phase.items()))))

    print("\ncovariate constancy per model (distinct values, counts)")
    for m in fd.MODELS:
        for key, cnt in cov[m].items():
            flag = "" if len(cnt) == 1 else "  <-- MOVED"
            print("  %-13s %-18s %s%s" % (fd.SHORT[m], key, dict(cnt),
                                          flag))
    for m, (d, e) in first_div.items():
        print("  first divergent echo: %s on %s echoed %r"
              % (fd.SHORT[m], d, e))

    print("\nitem-level probe-to-rerun gap (minutes), breached items")
    gaps = []
    for (d, m, i), evs in by_item.items():
        probe = [t for p, t in evs if p == "monitor_probe"]
        rerun = [t for p, t in evs if p == "monitor_rerun"]
        if probe and rerun:
            t0 = dt.datetime.fromisoformat(max(probe))
            t1 = dt.datetime.fromisoformat(min(rerun))
            gaps.append((t1 - t0).total_seconds() / 60.0)
    gaps.sort()
    print("  n=%d  min %.2f  median %.2f  max %.2f"
          % (len(gaps), gaps[0], statistics.median(gaps), gaps[-1]))

    print("\nresponse format by parsed answer, sonnet")
    for item, obs in fmt.items():
        print("  %s: %d rows" % (fd.item_short(item), len(obs)))
        by = collections.defaultdict(list)
        for p, ln in obs:
            by[str(p)].append(ln)
        for p in sorted(by):
            ls = by[p]
            print("    parsed %-4s n=%3d  len min %4d  median %4d  max %4d"
                  % (p, len(ls), min(ls), statistics.median(ls),
                     max(ls)))
        if item == "eq_alert_vuln_gating_v2":
            terse = sum(1 for p, ln in obs if p == "A" and ln <= 20)
            verbose = sum(1 for p, ln in obs if p == "D" and ln > 20)
            print("    lockstep (A terse <=20 chars, or D verbose): "
                  "%d of %d" % (terse + verbose, len(obs)))


if __name__ == "__main__":
    main()
