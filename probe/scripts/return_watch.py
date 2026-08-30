"""Daily return watch for re-baselined items, offline and exact.

Applies the return criterion pinned in
probe/REBASELINE_DECISION_2026-08-23.md to the committed record: for
every item carrying a superseded reference, every probe day after
the re-baseline is classified against EACH superseded reference. A
RETURN day is TVD at or below that reference's p99 band AND the
day's modal answer equal to that reference's modal (ties count as
not-returned, mirroring the step-change rule's home definition). A
return before the INTERCEPT freeze revises the step-change
classification to slow alternation in a new dated note; this script
is the mechanical check, run ad hoc or after each daily push. Reads
only committed inputs (baseline files, derived daily counts); no
network, no state, nothing written.

  python probe/scripts/return_watch.py
"""
import os
import sys
import json
import glob

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
MONITOR = os.path.join(REPO, "probe", "monitor")
OPTIONS = ("A", "B", "C", "D")


def tvd(a, b):
    na = sum(a.values()) or 1
    nb = sum(b.values()) or 1
    return 0.5 * sum(abs(a.get(o, 0) / na - b.get(o, 0) / nb)
                     for o in OPTIONS)


def modal(counts):
    if not counts:
        return None
    top = max(counts.values())
    leaders = [o for o in OPTIONS if counts.get(o, 0) == top]
    return leaders[0] if len(leaders) == 1 else None


def is_return(counts, superseded_rec):
    """The pinned criterion: within the superseded reference's p99
    band AND modal match; a tie for modal is not a return."""
    ref = superseded_rec["baseline_counts"]
    return (tvd(counts, ref) <= superseded_rec["band"]["p99"]
            and modal(counts) == modal(ref))


def main():
    daily = {}
    counts_path = os.path.join(MONITOR, "derived", "daily_counts.jsonl")
    with open(counts_path, encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if r["phase"] == "monitor_probe":
                daily[(r["date"], r["model"], r["item_id"])] = r["counts"]

    watched = 0
    for path in sorted(glob.glob(os.path.join(MONITOR, "baselines",
                                              "*.json"))):
        b = json.load(open(path, encoding="utf-8"))
        for iid, rec in b["items"].items():
            for old in rec.get("superseded", []):
                watched += 1
                ref = old["baseline_counts"]
                print("%s / %s: superseded reference %s (band %.2f, "
                      "modal %s), valid through %s" % (
                          b["model"], iid, ref, old["band"]["p99"],
                          modal(ref), old["valid_through"]))
                days = sorted(d for (d, m, i) in daily
                              if m == b["model"] and i == iid
                              and d > old["valid_through"])
                if not days:
                    print("  no post-rebaseline probe days in the "
                          "committed counts yet")
                far = 0.0
                for d in days:
                    c = daily[(d, b["model"], iid)]
                    t = tvd(c, ref)
                    flag = "RETURN" if is_return(c, old) else "away"
                    if t > far:
                        far = t
                        # a new maximum departure from the superseded
                        # reference; no threshold, extremes only
                        # (RULINGS_2026-08-30.md, return-watch scope)
                        flag += "  FARTHEST-YET"
                    print("  %s  %s  tvd_vs_superseded=%.2f  %s" % (
                        d, "/".join(str(c.get(o, 0)) for o in OPTIONS),
                        t, flag))
    if not watched:
        print("no superseded references in any baseline file; "
              "nothing to watch")


if __name__ == "__main__":
    main()
