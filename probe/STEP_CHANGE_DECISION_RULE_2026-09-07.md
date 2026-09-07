# Step-change decision rule: deepseek dlp_email_v2, pinned 2026-09-07

Date: 2026-09-07. Status: DRAFT until merged to main; the merge is
the operator's adoption and is the pin. Validity condition, stated
up front: this pin is valid only if merged before any
post-2026-09-07 probe data is read by operator or assistant; read
data never counts, so a later merge voids the note and it gets
redrafted with a later start date. Companions:
STEP_CHANGE_DECISION_RULES_2026-08-31.md (the standing-tripwire
form, the threshold construction, and the operational practice
this offer fulfills), STEP_CHANGE_DECISION_RULE_2026-08-16.md,
SLOW_ALTERNATION_REVISION_2026-09-02.md (what a fired candidacy
can and cannot claim), CORRECTIONS_2026-09-06.md (E5, which put
this thread's full history on the record),
REBASELINE_DECISION_2026-08-23.md (the consequence procedure), and
REPORTING_COMMITMENT.md.

## Registration status, stated plainly

This rule is pinned the evening of 2026-09-07, after that day's
verdicts were read, with the thread mid-escalation: the current
away run is two observed days (Sep 6 and 7), both held EVENTs,
both already read. Everything through 2026-09-07 counts toward
nothing. The count starts at zero at the pin; the first countable
observation is the 2026-09-08 probe (next scheduled run 13:00
UTC). The operator's established practice is merge before
reading, which keeps the pin clean under the same standard as
every prior rule.

## The thread

eq_alert_dlp_email_v2 on deepseek-v4-flash. Baseline (2026-08-02,
n=20): C-modal, 1 B / 17 C / 2 D, band p99 0.45. 37 observed
days, home-dominant, and every away day in the record is D-ward
or a C/D tie: away runs of one to three observed days, longest
returned-from run three (Sep 2 to 4). Six breaches, four held:
EVENTs Aug 19, Aug 20, Sep 6, Sep 7. The excursions deepen over
time: 0.40 to 0.45 on Aug 9 to 12, 0.50 to 0.60 on Aug 17 to 27,
0.65 to 0.70 on Sep 6 to 7, and the Sep 7 rerun (0/0/1/9, TVD
0.80 from baseline) is the slot's deepest reading in the record.
Exact vector recurrence throughout: probe 0/0/3/7 on both Aug 19
and Aug 27, and 1/0/3/6 four times across probes and reruns.

The question is the standard binary: a step change to a D-state,
or alternation with lengthening dwell. The haiku episode is the
standing caution here: this thread's own record already contains
three-day away runs that came home, so a fired candidacy is a
designation that opens the re-baseline decision, never itself a
classification, and the response to candidacy is dual reference
with a pre-registered return criterion, never a bare re-baseline.

## Definitions

Identical in form to the prior rules, anchored to this item:

- HOME DAY: TVD vs baseline_counts at or below 0.45 AND unique
  modal C. Ties for modal count as not-home.
- AWAY DAY: any observed day that is not a HOME day.
- Missing days count as neither and do not reset; a run is a
  streak in the sequence of observed days.
- Arithmetic is the monitor's as stored
  (FLOAT_POLICY_2026-08-30.md).

Null context (probe/scripts/step_change_watch.py, exact
enumeration): P(unique baseline modal survives a fair redraw) =
0.998, P(HOME day) = 0.998. This is a strong-margin item in the
haiku class, not a flapping item: away days here carry
information, and a five-day null away run has probability 5.9e-14
(the watch script prints the exact value). No flapping correction
is needed.

## The rule

A standing tripwire, evaluated in date order over observed days
from 2026-09-08 onward:

1. CANDIDACY: five consecutive observed AWAY days beginning
   2026-09-08 or later. Consequence: designate the item a
   step-change candidate, write a dated note, and open the
   re-baseline discussion for THIS ITEM ONLY as a dated operator
   decision per REBASELINE_DECISION_2026-08-23.md. The frozen
   Aug 2 baseline stays in force until that decision is recorded.
2. A HOME day resets the count to zero and terminates nothing;
   each reset is alternation evidence, visible in the watch
   output.
3. The rule stands until a candidacy fires or a dated note
   retires it. The freeze write-up reports whatever state exists
   on 2026-09-26.

Threshold derivation, fixed before any countable data exists:
five strictly exceeds the longest away dwell the item has been
observed to return home from (three), plus two days of clearance
because 37 observed days give a noisy lower bound on the dwell
tail, the same construction as the 2026-08-31 rules. The
mid-escalation position argues for the standard construction, not
against it: the thread has come home from three; only a run it
has never produced clears the bar. Freeze arithmetic is
comfortable: a qualifying run must begin by 2026-09-22 to fire
before the freeze.

## What is deliberately not pinned, from the log this time

deepseek eq_alert_spend_anomaly: three breaches (Aug 10, Sep 4,
Sep 7), all TRANSIENT, all reverted same-day, verified against
verdicts.jsonl; a one-count modal margin (10 D against 9 B, null
modal survival 0.481) puts it in the wanderer class with
contractor. deepseek eq_alert_fraud_scoring_v2: four breaches
(Aug 9, held EVENT; Aug 21, Sep 5, Sep 6, all reverted, Sep 5 a
float-edge entry per CORRECTIONS_2026-09-06.md S2), and its
September days since read A-modal at home. Neither shows a
persisting held state today. If either holds a breach across
consecutive days or consolidates directionally, a rule gets
pinned that day, count from the pin.

## Code adopted with this note

probe/scripts/step_change_watch.py gains this thread's RULES
entry (threshold 5, count_from 2026-09-08). The counting
semantics are unchanged and already pinned by
probe/tests/test_step_change_watch.py; no other code changes.
