"""Count for the gpt disclosure_timing wait rule, offline and exact.

Applies probe/STEP_CHANGE_DECISION_RULE_2026-10-18.md to the committed
record. HOME is TVD at or below 0.40 against the 2026-08-02 reference
AND unique modal A; a tie is not home. A missing day or an ERROR day
(per verdicts.jsonl) is neither and is skipped. Clause 1: each
observed AWAY day from 2026-10-17 adds one. Clause 3: two consecutive
observed HOME days reset the count to zero; a single HOME day between
AWAY days adds nothing and resets nothing. Clause 2: a THRESHOLD line
prints on the day the count reaches 18, and counting stops there
(clause 4). TVD is exact (fractions), per FLOAT_POLICY_2026-08-30.md.

The script is analysis-side: it reads only committed inputs, decides
nothing, and writes nothing. The rebaseline run and its dated note
belong to the operator's process under the rule.

  python probe/scripts/wait_rule_count.py
"""
import os
import json
import datetime
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
MONITOR = os.path.join(REPO, "probe", "monitor")
OPTIONS = ("A", "B", "C", "D")

MODEL = "gpt-5.6-terra"
ITEM_ID = "eq_disclosure_timing"
COUNT_FROM = "2026-10-17"
THRESHOLD = 18
HOME_TVD = Fraction(2, 5)
NOTE = "STEP_CHANGE_DECISION_RULE_2026-10-18.md"


def tvd(a, b):
    na = sum(a.values())
    nb = sum(b.values())
    return sum(abs(Fraction(a.get(o, 0), na) - Fraction(b.get(o, 0), nb))
               for o in OPTIONS) / 2


def modal(counts):
    if not counts:
        return None
    top = max(counts.values())
    leaders = [o for o in OPTIONS if counts.get(o, 0) == top]
    return leaders[0] if len(leaders) == 1 else None


def reference(rec):
    """The 2026-08-02 reference: the current record, or the earliest
    superseded entry once the item has been re-baselined."""
    old = rec.get("superseded", [])
    if old:
        return min(old, key=lambda e: e["valid_through"])
    return rec


def is_home(counts, ref):
    return (tvd(counts, ref["baseline_counts"]) <= HOME_TVD
            and modal(counts) == modal(ref["baseline_counts"]) == "A")


def evaluate(days, ref, threshold=THRESHOLD, count_from=COUNT_FROM):
    """Apply clauses 1 to 4 to a sorted list of (date, counts) observed
    days, with missing and ERROR days already removed. Returns (date,
    counts, tvd, home, count, event) per countable day; event is
    "THRESHOLD" on the day the count reaches threshold, "RESET" on a
    second consecutive HOME day that clears a nonzero count, else "".
    Nothing after the threshold day is returned."""
    out = []
    count = 0
    prev_home = False
    for d, c in days:
        if d < count_from:
            continue
        home = is_home(c, ref)
        event = ""
        if home:
            if prev_home and count:
                count = 0
                event = "RESET"
        else:
            count += 1
            if count == threshold:
                event = "THRESHOLD"
        prev_home = home
        out.append((d, c, tvd(c, ref["baseline_counts"]), home, count,
                    event))
        if event == "THRESHOLD":
            break
    return out


def earliest(last_date, count, threshold=THRESHOLD):
    """The earliest calendar date the threshold can fall on: every
    day after last_date observed and AWAY."""
    d = datetime.date.fromisoformat(last_date)
    return (d + datetime.timedelta(threshold - count)).isoformat()


def load_days():
    errors = set()
    with open(os.path.join(MONITOR, "verdicts.jsonl"),
              encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if r["model"] == MODEL and r["verdict"] == "ERROR":
                errors.add(r["date"])
    days = {}
    path = os.path.join(MONITOR, "derived", "daily_counts.jsonl")
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if (r["phase"] == "monitor_probe" and r["model"] == MODEL
                    and r["item_id"] == ITEM_ID
                    and r["date"] not in errors):
                days[r["date"]] = r["counts"]
    return sorted(days.items()), errors


def main():
    days, errors = load_days()
    path = os.path.join(MONITOR, "baselines", "%s.json" % MODEL)
    ref = reference(json.load(open(path, encoding="utf-8"))
                    ["items"][ITEM_ID])
    print("%s / %s  (%s)" % (MODEL, ITEM_ID, NOTE))
    print("  reference %s, HOME at tvd <= 0.40 with unique modal A; "
          "threshold %d observed AWAY days from %s; two consecutive "
          "HOME days reset" % (ref["baseline_counts"], THRESHOLD,
                               COUNT_FROM))
    skipped = sorted(e for e in errors if e >= COUNT_FROM)
    if skipped:
        print("  ERROR days skipped: %s" % ", ".join(skipped))
    table = evaluate(days, ref)
    if not table:
        print("  no countable days on or after %s in the committed "
              "counts yet" % COUNT_FROM)
        return
    for d, c, t, home, count, event in table:
        line = "  %s  %s  tvd=%s  %s  count=%d" % (
            d, "/".join(str(c.get(o, 0)) for o in OPTIONS), t,
            "HOME" if home else "AWAY", count)
        if event == "THRESHOLD":
            line += "  THRESHOLD (run rebaseline_item.py per clause 2)"
        elif event == "RESET":
            line += "  RESET (two consecutive HOME days)"
        print(line)
    d, count = table[-1][0], table[-1][4]
    if count < THRESHOLD:
        print("  count %d of %d through %s; earliest threshold date "
              "%s" % (count, THRESHOLD, d, earliest(d, count)))


if __name__ == "__main__":
    main()
