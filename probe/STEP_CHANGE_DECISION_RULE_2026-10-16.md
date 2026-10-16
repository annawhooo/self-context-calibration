# Wait rule: gpt disclosure_timing, 18 observed days, then dual reference

Date: 2026-10-16. Status: DRAFT until merged to main; the merge is the
operator's adoption and is the pin. Validity condition: this pin is
valid only if merged before any 2026-10-17 probe data is read by
operator or assistant; otherwise it is void and gets redrafted with a
later start date. Companions: STEP_CHANGE_CANDIDACY_2026-10-16.md
(which opened the decision this note takes),
STEP_CHANGE_DECISION_RULE_2026-09-14.md (the definitions reused here),
REBASELINE_DECISION_2026-08-23.md (the dual-reference mechanism and
the form of the return criterion), SLOW_ALTERNATION_REVISION_2026-09-02.md
(the dwell that sets the threshold), DEVIATIONS_2026-10-16.md (D1,
whose recompute also writes baseline files), DESIGN_LIMITATIONS.md
(Limitation 4), and REPORTING_COMMITMENT.md.

## The decision

The operator takes neither alternative from the candidacy note today.
The frozen 2026-08-02 reference stays in force while a pre-registered
wait runs. If the item stays away for the full wait, the item is
re-baselined with the dual reference of REBASELINE_DECISION_2026-08-23.md.
This item only. No band, K, seed, alarm-set member, verdict, or monitor
code changes with this note.

The reason for waiting is the one precedent. The haiku item was
re-baselined after a seven-observed-day candidacy and returned home
ten days later, and the return revised the classification to slow
alternation. This item's current run is five observed days long, its
probe vectors since 2026-10-09 range from 0/10 to 5/5, and before this
run the item had never stayed away more than one day. A reference
drawn from that state now could freeze an unrepresentative point.

## Registration status, stated plainly

Drafted on the afternoon of 2026-10-16. Verdict lines through
2026-10-15 have been read. The 2026-10-16 verdict line is on main; the
assistant saw the opening characters of its commit subject (a
verdict tally) and nothing else, and the operator has not read the
line.
Every day through 2026-10-16 counts toward nothing here. The first
countable observation is the 2026-10-17 probe.

## The rule

The definitions are unchanged from
STEP_CHANGE_DECISION_RULE_2026-09-14.md: HOME is TVD at or below 0.40
against the 2026-08-02 reference AND unique modal A; a tie is not
home; a missing day or an ERROR day is neither home nor away and does
not reset the count;
arithmetic is the monitor's as stored on the day.

1. COUNT: consecutive observed AWAY days, beginning 2026-10-17.
2. THRESHOLD: 18. On the probe day the count reaches 18, run
   probe/scripts/rebaseline_item.py for this item after that day's
   probe, under the gates and validity convention of
   REBASELINE_DECISION_2026-08-23.md, and record the run in a dated
   note. A failed gate writes nothing, and the outcome goes to the
   operator as a dated decision.
3. RESET: a HOME day resets the count to zero and terminates nothing.
   The first HOME day on or after 2026-10-17 also gets a dated note
   reporting the episode's observed dwell.
4. SUSPENSION: if the monitor's echo tripwire halts this model's arm,
   the count stops with the arm.
5. The rule stands until the threshold is reached or a dated note
   retires the rule.

## Threshold derivation

The 2026-09-14 rule set its threshold to strictly exceed the item's
longest observed returned-from dwell, plus two days of clearance. The
item's own longest is one day, which the current run already exceeds,
so this rule uses the longest returned-from dwell in the whole record.
Computed in session on 2026-10-16 over probe/monitor/derived/
daily_counts.jsonl through 2026-10-15, against each item's 2026-08-02
reference (the superseded entry where an item was re-baselined), with
the HOME definition above: the longest is 16 observed days, on
claude-haiku-4-5-20251001 eq_alert_spend_anomaly_v2. That figure
matches the B-rest of sixteen consecutive observed away days that
SLOW_ALTERNATION_REVISION_2026-09-02.md records for the same item. The
next longest are 12 (deepseek-v4-flash eq_alert_spend_anomaly) and 10
(gpt-5.6-terra eq_alert_fraud_scoring). 16 plus 2 is 18. With no
missing days, the 18th observed day is 2026-11-03.

## The return criterion, pinned now for the re-baselined state

If rule clause 2 executes, a RETURN day is a probe day after the
re-baseline with BOTH TVD at or below 0.40 against the superseded
2026-08-02 reference AND unique modal A, a tie counting as
not-returned. The criterion mirrors the haiku criterion. probe/scripts/
return_watch.py is the mechanical check. The consequence of a RETURN
day is a dated note revising the classification to alternation and a
re-examination of the re-baseline as a dated operator decision.

## Interaction with D1

DEVIATIONS_2026-10-16.md leaves the recalibration recompute without an
effective date, and the recompute also rewrites the baseline files. If
the re-baseline and the recompute both land, each lands as its own
dated commit, and the later commit runs against the baseline file as
the earlier commit left the file. This item is equipoise class, and
the recompute's own gate requires equipoise records to stay
byte-identical.

## Stated plainly, for evidential weight

Limitation 4 attaches as in the candidacy note: the 20-of-20 A
reference may itself be the anomalous state on an item designed for
equipoise. Waiting does not settle which state is healthy. The rule
measures dwell only.

## Reproducibility

The definitions and the reference are in
STEP_CHANGE_DECISION_RULE_2026-09-14.md and
probe/monitor/baselines/gpt-5.6-terra.json. The daily classification
from 2026-10-17 is the gpt-5.6-terra / eq_disclosure_timing block of
probe/scripts/step_change_watch.py once its RULES entry carries
threshold 18 and count_from 2026-10-17. The dwell figures come from the
session computation described above, over the committed daily counts.
