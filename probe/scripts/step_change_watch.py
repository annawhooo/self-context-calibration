"""Standing step-change watch for pinned per-thread rules.

Applies the rules pinned in STEP_CHANGE_DECISION_RULES_2026-08-31.md
to the committed record: for each thread in RULES, every observed
monitor_probe day on or after that rule's count_from date is
classified HOME or AWAY against the thread's frozen baseline, using
the same definitions as the 2026-08-16 haiku rule (HOME requires TVD
at or below the stored band AND the day's unique modal equal to the
baseline modal; ties are not home; missing days count as neither and
never reset). A CANDIDACY line prints on the day a thread's count of
consecutive observed AWAY days reaches its pinned threshold. The
script is analysis-side: it reads only committed inputs, decides
nothing, and writes nothing.

It also prints each rule's null context, computed by exact
enumeration over all K=10 multinomial draws from the baseline
proportions: the probability a fair redraw of the baseline keeps the
unique baseline modal, the probability it lands HOME, and the
probability of a full threshold-length run of null AWAY days. These
are the numbers the rule note cites for why short away runs on
weak-modal-margin items mean nothing.

  python probe/scripts/step_change_watch.py
  python probe/scripts/step_change_watch.py --null MODEL ITEM_ID

The --null form prints the enumeration for any slot's current
baseline and each of its superseded references, so every context
number is reproducible for items outside RULES too.
"""
import os
import sys
import json
import argparse
from math import comb

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
MONITOR = os.path.join(REPO, "probe", "monitor")
OPTIONS = ("A", "B", "C", "D")

NOTE = "STEP_CHANGE_DECISION_RULES_2026-08-31.md"

RULES = [
    {"model": "gpt-5.6-terra", "item_id": "eq_alert_fraud_scoring",
     "threshold": 12, "count_from": "2026-09-01"},
    {"model": "gpt-5.6-terra", "item_id": "eq_access_offboarding",
     "threshold": 8, "count_from": "2026-09-01"},
]


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


def is_home(counts, rec):
    """The pinned definition: TVD at or below the stored band AND
    unique modal equal to the baseline modal; a tie is not home."""
    ref = rec["baseline_counts"]
    return (tvd(counts, ref) <= rec["band"]["p99"]
            and modal(counts) == modal(ref))


def evaluate(days, rec, threshold, count_from):
    """Apply the pinned counting semantics to a sorted list of
    (date, counts) observed days. Days before count_from never
    count; dates absent from the list are neither and do not reset
    (consecutiveness is over observed days); a HOME day resets the
    count to zero. Returns (date, counts, tvd, modal, home, count,
    fired) per countable day, fired=True exactly when the count
    reaches threshold."""
    ref = rec["baseline_counts"]
    out = []
    count = 0
    for d, c in days:
        if d < count_from:
            continue
        home = is_home(c, rec)
        count = 0 if home else count + 1
        out.append((d, c, tvd(c, ref), modal(c), home, count,
                    (not home) and count == threshold))
    return out


def null_context(rec, k=10):
    """Exact enumeration over all K=k multinomial draws from the
    baseline proportions, no change assumed: returns (P(the draw's
    unique modal equals the baseline modal), P(the draw is a HOME
    day)). Uses the same float tvd and stored band as the daily
    comparison, per FLOAT_POLICY_2026-08-30.md."""
    ref = rec["baseline_counts"]
    tot = sum(ref.values())
    bm = modal(ref)
    p = [ref.get(o, 0) / tot for o in OPTIONS]
    p_modal = 0.0
    p_home = 0.0
    for a in range(k + 1):
        for b in range(k + 1 - a):
            for c in range(k + 1 - a - b):
                d = k - a - b - c
                v = dict(zip(OPTIONS, (a, b, c, d)))
                if modal(v) != bm:
                    continue
                w = (comb(k, a) * comb(k - a, b) * comb(k - a - b, c)
                     * p[0] ** a * p[1] ** b * p[2] ** c * p[3] ** d)
                p_modal += w
                if is_home(v, rec):
                    p_home += w
    return p_modal, p_home


def load_daily():
    daily = {}
    path = os.path.join(MONITOR, "derived", "daily_counts.jsonl")
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if r["phase"] == "monitor_probe":
                daily[(r["model"], r["item_id"], r["date"])] = r["counts"]
    return daily


def load_baseline(model):
    path = os.path.join(MONITOR, "baselines", "%s.json" % model)
    return json.load(open(path, encoding="utf-8"))


def print_context(label, rec):
    p_modal, p_home = null_context(rec)
    ref = rec["baseline_counts"]
    print("%s: baseline %s (modal %s, band %.2f)" % (
        label, ref, modal(ref), rec["band"]["p99"]))
    print("  null redraw: P(unique baseline modal) = %.3f, "
          "P(HOME day) = %.3f" % (p_modal, p_home))
    return p_home


def watch():
    daily = load_daily()
    for rule in RULES:
        b = load_baseline(rule["model"])
        rec = b["items"][rule["item_id"]]
        print("%s / %s  (%s)" % (rule["model"], rule["item_id"], NOTE))
        p_home = print_context("  rule", rec)
        print("  threshold %d consecutive observed AWAY days from %s; "
              "P(full null away run) = %.1e" % (
                  rule["threshold"], rule["count_from"],
                  (1.0 - p_home) ** rule["threshold"]))
        days = sorted((d, c) for (m, i, d), c in daily.items()
                      if m == rule["model"] and i == rule["item_id"])
        table = evaluate(days, rec, rule["threshold"],
                         rule["count_from"])
        if not table:
            print("  no countable days on or after %s in the "
                  "committed counts yet" % rule["count_from"])
        for d, c, t, m, home, count, fired in table:
            line = "  %s  %s  tvd=%.2f  modal=%s  %s  count=%d" % (
                d, "/".join(str(c.get(o, 0)) for o in OPTIONS), t,
                m, "HOME" if home else "AWAY", count)
            if fired:
                line += "  CANDIDACY (threshold reached)"
            print(line)
        print()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--null", nargs=2, metavar=("MODEL", "ITEM_ID"),
                    help="print the null enumeration for one slot's "
                         "current baseline and each superseded "
                         "reference, then exit")
    args = ap.parse_args(argv)
    if args.null:
        model, iid = args.null
        rec = load_baseline(model)["items"][iid]
        print_context("%s / %s current" % (model, iid), rec)
        for old in rec.get("superseded", []):
            print_context("%s / %s superseded (through %s)" % (
                model, iid, old["valid_through"]), old)
        return
    watch()


if __name__ == "__main__":
    main()
