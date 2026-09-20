# Step-change decision rule: gpt patch_timing, pinned 2026-09-20

Date: 2026-09-20. Status: DRAFT until merged to main; the merge is
the operator's adoption and is the pin. Validity condition: this
pin is valid only if merged before any post-2026-09-20 probe data
is read by operator or assistant; otherwise it is void and gets
redrafted with a later start date. Companions:
STEP_CHANGE_DECISION_RULES_2026-08-31.md (the form, the threshold
construction, and the operational practice this fulfills),
STEP_CHANGE_DECISION_RULE_2026-09-14.md (the same instrument for
the disclosure thread), DESIGN_LIMITATIONS.md (Limitation 4), and
REPORTING_COMMITMENT.md.

## Registration status, stated plainly

Pinned the afternoon of 2026-09-20, after that day's verdicts were
read. The trigger was the 2026-09-19 held EVENT on this thread,
already read data that counts toward nothing; so does everything
through 2026-09-20. The count starts at zero at the pin; the first
countable observation is the 2026-09-21 probe. Six days remain
before the freeze, and the arithmetic is stated below rather than
hidden: this pin exists so that a run, if one starts now, is
countable, not because one is expected.

## The thread

eq_patch_timing on gpt-5.6-terra. Baseline (2026-08-02, n=20):
unanimous B, 20 of 20, band p99 0.40. 47 observed days. A
strong-margin item: exact enumeration gives P(a fair redraw keeps
unique modal B) = 1.000 to three places, so an away day is signal,
never modal flapping. The record: three breaches, two of them held
EVENTs (Aug 7 at TVD 0.70 with an A-modal probe; Sep 19 at 0.60,
A-modal, rerun identical to the probe at TVD 0.00), one reverted
(Aug 8, a 5/5 A/B tie). Every excursion is A-ward. The Aug 7 to 8
pair is the longest away dwell the item has returned home from,
two observed days; it then sat home for 41 consecutive days before
the Sep 19 spike, and read 0/10/0/0, the exact baseline, on
Sep 20. This is a dormant-then-spike thread with a held state that
recurs six weeks apart.

The sign-inversion caveat attaches (DESIGN_LIMITATIONS.md,
Limitation 4): a 20-of-20 unanimous baseline on a designed-
equipoise item is the shape the design notes flag; the A-spikes
may be excursions toward designed behavior. The rule counts dwell
and claims no direction of health.

## Definitions

Identical in form to the prior rules, anchored to this item: HOME
is TVD at or below 0.40 AND unique modal B; ties are not home;
missing days are neither and do not reset; arithmetic is the
monitor's as stored (FLOAT_POLICY_2026-08-30.md).

## The rule

A standing tripwire, evaluated in date order over observed days
from 2026-09-21 onward:

1. CANDIDACY: four consecutive observed AWAY days beginning
   2026-09-21 or later. Consequence: designate the item a
   step-change candidate, write a dated note, and open the
   re-baseline discussion for THIS ITEM ONLY as a dated operator
   decision per REBASELINE_DECISION_2026-08-23.md. The frozen
   baseline stays in force until that decision is recorded.
2. A HOME day resets the count to zero and terminates nothing.
3. The rule stands until a candidacy fires or a dated note
   retires it; the freeze write-up reports whatever state exists
   on 2026-09-26.

Threshold derivation, fixed before any countable data exists: four
strictly exceeds the longest observed returned-from dwell (two
days) plus the standard two days of clearance. Under the null the
probability of four consecutive away days is zero to three places.
Freeze arithmetic, stated honestly: a qualifying run must begin by
2026-09-23 to fire before the freeze with no missing days. If no
run starts, the rule costs nothing and the freeze reports the
thread descriptively with its pin date; if one does, it is
countable from its first day instead of becoming one more
descriptive observation.

## Code adopted with this note

probe/scripts/step_change_watch.py gains this thread's RULES entry
(threshold 4, count_from 2026-09-21). Counting semantics unchanged,
pinned by the existing test.
