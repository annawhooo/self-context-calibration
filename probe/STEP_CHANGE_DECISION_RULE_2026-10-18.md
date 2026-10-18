# Wait rule: gpt disclosure_timing, 18 observed days, then dual reference

Date: 2026-10-18 (first drafted 2026-10-16). Status: DRAFT until merged
to main; the merge is the operator's adoption and is the pin. Validity
condition: this pin is valid only if merged before any 2026-10-17 or
later probe data is read by operator or assistant; otherwise it is
void and gets redrafted with a later start date. Companions:
STEP_CHANGE_CANDIDACY_2026-10-16.md (which opened the decision this
note takes), STEP_CHANGE_DECISION_RULE_2026-09-14.md (the definitions
reused here), REBASELINE_DECISION_2026-08-23.md (the dual-reference
mechanism), SLOW_ALTERNATION_REVISION_2026-09-02.md (the dwell that
sets the threshold), DEVIATIONS_2026-10-16.md (D1, whose recompute
also writes baseline files), REGISTRATION_ATTESTATION_2026-10-18.md
(the attestation for this pin), DESIGN_LIMITATIONS.md (Limitation 4),
and REPORTING_COMMITMENT.md.

## The decision

The operator takes neither alternative from the candidacy note. The
frozen 2026-08-02 reference stays in force while a pre-registered wait
runs. If the item stays away for the full wait, the item is
re-baselined with the dual reference of
REBASELINE_DECISION_2026-08-23.md. This item only. No band, K, seed,
alarm-set member, verdict, or monitor code changes with this note.

The reason for waiting is the one precedent. The haiku item was
re-baselined after a seven-observed-day candidacy and returned home
ten days later, and the return revised the classification to slow
alternation. This item's current run is five observed days long, its
probe vectors since 2026-10-09 range from 0/10 to 5/5, and before this
run the item had never stayed away more than one day. A reference
drawn from that state now could freeze an unrepresentative point.

## Registration status, stated plainly

Verdict lines through 2026-10-15 have been read. The 2026-10-16 and
2026-10-17 verdict lines are on main. For 2026-10-16 the assistant saw
the opening characters of the commit subject (a verdict tally) and
nothing else; for 2026-10-17 the assistant saw the commit hash and
timestamp only. The operator reads the record only through Claude
sessions and has read neither line. The evidence for what each party
saw is in REGISTRATION_ATTESTATION_2026-10-18.md. Every day through
2026-10-16 counts toward nothing here, and the first countable
observation is the 2026-10-17 probe. The simulation in the evaluation
section loads only data through 2026-10-15.

## The rule

HOME and AWAY keep the definitions of
STEP_CHANGE_DECISION_RULE_2026-09-14.md: HOME is TVD at or below 0.40
against the 2026-08-02 reference AND unique modal A; a tie is not
home; a missing day or an ERROR day is neither home nor away and is
skipped when counting; arithmetic is the monitor's as stored on the
day. The reset differs from every earlier rule, as clause 3 states.

1. COUNT: observed AWAY days beginning 2026-10-17, each AWAY day
   adding one to the count.
2. THRESHOLD: 18. On the probe day the count reaches 18, run
   probe/scripts/rebaseline_item.py for this item after that day's
   probe, under the gates and validity convention of
   REBASELINE_DECISION_2026-08-23.md, and record the run in a dated
   note. A failed gate writes nothing, and the outcome goes to the
   operator as a dated decision.
3. RESET: two consecutive observed HOME days reset the count to zero
   and terminate nothing. A single HOME day between AWAY days adds
   nothing to the count and resets nothing. Earlier rules reset on one
   HOME day; the change is the operator's, proposed on 2026-10-18
   before the evaluation below was run.
4. The rule stands until the threshold is reached or a dated note
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
missing days and no single HOME days, the 18th observed day is
2026-11-03.

## Evaluation of the reset forms

Six reset forms were compared by simulation on 2026-10-18, with the
plan fixed in the script before the first run. Each simulated path is
60 observed days from 2026-10-17. A HOME day is 6 or more A answers
out of 10, which is the HOME definition above for this reference.

Inputs, all read data through 2026-10-15. The home regime is the 64
probe days from 2026-08-02 to 2026-10-08, of which 82.8% are HOME
days. The away regime is the 5 probe days from 2026-10-09 to
2026-10-15, with A counts 0, 4, 5, 2 and 1. Because 5 days cannot fix
the away state, three away models were run: W1 resamples the 5 days
(a 0% chance of a HOME day), W2 is a beta-binomial fitted to the
spread of the 5 days (9.3%), and W3 is a binomial at the pooled 24% A
share of the 5 days (1.6%).

Scenarios for the truth: S1 a step change that stays away; S2a and
S2b slow alternators with away dwells averaging 10 and 20 days and
home dwells averaging 7; S3 a return within a few days.

Forms, all with threshold 18: R1 resets on one HOME day; C1 closes the
episode on the first HOME day; R2 is clause 3 above; C2 closes on two
consecutive HOME days; W re-baselines when 16 of the latest 18 days
are AWAY; B3 pools 3-day blocks and needs 6 AWAY blocks in a row.

Share of 20,000 simulated step changes (S1) re-baselined within 60
days, with the median day:

| form | W2         | W3          | W1         |
|------|------------|-------------|------------|
| R1   | 70%, day 30 | 99.8%, day 18 | 100%, day 18 |
| C1   | 17%, day 18 | 75%, day 18 | 100%, day 18 |
| R2   | 99.9%, day 20 | 100%, day 18 | 100%, day 18 |
| C2   | 85%, day 19 | 99.5%, day 18 | 100%, day 18 |
| W    | 99.9%, day 18 | 100%, day 18 | 100%, day 18 |
| B3   | 100%, day 18 | 100%, day 18 | 100%, day 18 |

C1 wrongly closed 83% of W2 step changes as alternation. Under a
quick return (S3), no form re-baselined more than 0.4% of paths. Under
the slow alternators, every form that tolerates noise re-baselined
often and then met a return within 30 days: R2 under S2b and W2
re-baselined 81% of paths, and 64% of all paths saw a return within
30 days of the re-baseline. No 18-day rule separates a long-dwell
alternator from a step change before the alternator returns; the
forms that re-baselined less under S2 (R1, C1) are the forms that
failed S1. The cost of that outcome is bounded by the dual reference,
whose superseded entry makes a reversal one dated note.

Check: for R1 and C1 under S1 and W3, the exact probabilities, 0.998
and 0.746, match the simulation.

Selection: R2. R2 matches B3 and W on step changes and quick returns,
and R2 adds one condition to the house definitions where W and B3 add
parameters chosen by the assistant. Assumptions carried openly: days
are independent within a state, so clustered noise would raise the
chance of two consecutive HOME days and narrow R2's margin over R1;
the away state rests on 5 days; S2 and S3 dwell lengths are
assumptions, not estimates; missing days are not simulated; and R2 by
design ignores a genuine one-day visit home.

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
probe/scripts/step_change_watch.py once that script implements clause
3 and carries threshold 18 and count_from 2026-10-17. The dwell figures
and the evaluation come from session computations over the committed
daily counts through 2026-10-15.
