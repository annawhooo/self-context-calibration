# Step-change decision rules for two gpt threads, pinned 2026-08-31

Date: 2026-08-31. Status: DRAFT until merged to main; the merge is
the operator's adoption and is the pin. Companions:
STEP_CHANGE_DECISION_RULE_2026-08-16.md (the template and the only
prior pinned rule), RULINGS_2026-08-30.md (Ruling 1, which requires
this instrument and recorded both descriptive runs),
REBASELINE_DECISION_2026-08-23.md (the consequence procedure),
DRIFT_WINDOW_2026-08-14_to_30.md, FLOAT_POLICY_2026-08-30.md, and
REPORTING_COMMITMENT.md.

## Registration status, stated plainly

These rules are pinned on 2026-08-31, hours after the Aug 31
verdicts were read, and the pin was prompted by what they showed: a
first held EVENT on eq_alert_fraud_scoring. Everything through
2026-08-31 is therefore deciding data already read, and it counts
toward nothing. Each rule's count starts at zero at the pin; the
first countable observation is the 2026-09-01 probe. At commit time
no post-Aug-31 probe data exists anywhere (the next scheduled run
is 2026-09-01 13:00 UTC), so relative to every countable day this
is a clean pre-registration, a cleaner position than the 2026-08-16
rule's, which had three unread days already on disk when it was
committed.

## The threads and the question

Both threads are gpt-5.6-terra slots whose descriptive away runs
were recorded in Ruling 1 without candidacy, because no rule
existed before the runs were read. The question for each is the
2026-08-16 binary: a step change (a one-way transition to a new
stable state; the frozen baseline becomes obsolete; the
dual-reference re-baseline procedure is the response) or
alternation with asymmetric dwell (two homes; re-baselining would
chase the oscillation).

eq_alert_fraud_scoring. Baseline (2026-08-02, n=20): C-modal,
8 A / 2 B / 9 C / 1 D, band p99 0.45. 27 observed days through
Aug 31: the gpt credit outage (http 429, Aug 14 to 16,
DRIFT_WINDOW_2026-08-14_to_30.md) left no monitor_probe rows for
either slot, Aug 14's run having completed only 43 of 68 items.
The record: a ten-day consecutive observed away run Aug 12 to
Aug 24 spanning the outage gap, a return home Aug 25, then
oscillation (home Aug 25, 27, 29, 30), a reverted breach Aug 26
(8/2/0/0 at TVD 0.50), the record's only D-modal day Aug 28
(1/0/4/5 at 0.45, at band, not a breach under the strict-> rule),
and on Aug 31 the slot's third breach and first held EVENT: probe
9/0/1/0, TVD 0.50, same-day rerun matching the probe at 0.10 and
the baseline at 0.50.

eq_access_offboarding. Baseline: C-modal, 6 A / 12 C / 2 D, band
p99 0.40. 27 observed days. Longest observed away run six days
(Aug 11 to 19 across the outage gap), all of it A-shifted; five
consecutive home days Aug 27 to 31, closing at TVD 0.00 today.
This thread is pinned from home, before any live away run, which
is the cleanest registration position available; it is included
now precisely so that its next long run, if one comes, is
countable from its first day instead of becoming another
descriptive observation.

## Definitions

Identical in form to the 2026-08-16 rule, anchored per item:

- HOME DAY: TVD vs baseline_counts at or below band p99 (no
  breach) AND the day's modal answer is the baseline modal (C for
  both threads). Ties for modal count as not-home.
- AWAY DAY: any observed day that is not a HOME day.
- Missing days (ERROR verdicts, outage days, no probe rows) count
  as neither and do not reset the count; a run is a streak in the
  sequence of observed days.
- Arithmetic is the monitor's as it stands: float comparisons
  against the stored band (FLOAT_POLICY_2026-08-30.md). If the
  monitor converts to integer arithmetic after the freeze, the
  watch converts with it.

One property of these definitions must be on the record before any
counting starts. They were built for the haiku item, whose
original baseline modal survives a fair redraw almost surely:
exact enumeration over K=10 multinomial draws from the baseline
proportions gives 0.998 for 2 A / 1 B / 17 D
(probe/scripts/step_change_watch.py computes every number in this
paragraph; the --null form reproduces them for any slot).
fraud_scoring's modal margin is one count, 9 C against 8 A, and
the same enumeration gives 0.494, with P(HOME day) = 0.493: under
the null of no change at all, roughly half of this thread's days
read AWAY by modal flapping alone. Short away runs on this thread
mean nothing, and the record shows it: the ten-day run contains
days at TVD 0.15 and 0.20 that are distributionally at baseline
with the modal flipped to A. The thresholds below are set with
exactly that in mind: the probability that twelve consecutive
observed null days all read away is 2.9e-04. offboarding's margin
is wide (modal survival 0.801, P(HOME day) = 0.801, eight-day null
run 2.5e-06) and needs no such correction, but takes the same form
of rule for uniformity.

## The rules

Standing tripwires, evaluated in date order over observed days
from 2026-09-01 onward. Unlike the 2026-08-16 rule, a HOME day
resets the count to zero and terminates nothing. The 2026-08-16
rule raced two hypotheses about an away run already in progress;
neither thread here is in a countable run at the pin, and a
one-shot race started now would resolve alternation at the first
home day, close the rule, and leave the next long run uncountable,
which is the exact gap this pin exists to close.

1. CANDIDACY, fraud_scoring: twelve consecutive observed AWAY days
   beginning 2026-09-01 or later. Consequence: designate the item
   a step-change candidate, write a dated note, and open the
   re-baseline discussion for THIS ITEM ONLY as a dated operator
   decision per REBASELINE_DECISION_2026-08-23.md. The frozen
   Aug 2 baseline stays in force until that decision is recorded.
2. CANDIDACY, offboarding: eight consecutive observed AWAY days
   beginning 2026-09-01 or later, same consequence.
3. A HOME day resets that thread's count to zero. Each reset is
   alternation evidence, visible in the watch output; no formal
   designation attaches to it.
4. The rules stand until a candidacy fires or a dated note retires
   them. The freeze write-up (2026-09-26) reports whatever state
   exists that day. If no candidacy has fired by then, each
   thread's record is reported descriptively with the pre-pin and
   post-pin boundary maintained, and fraud_scoring's pre-pin
   record, a ten-day away run that ended in a return, already
   reads as long-dwell alternation for the paper's bistability
   discussion.

Threshold derivation, fixed before any countable data exists: each
threshold strictly exceeds the longest away dwell its item has
been observed to return home from, ten days for fraud_scoring and
six for offboarding, plus two days of clearance because 27
observed days give a noisy lower bound on the true dwell tail.
Plus three and beyond was rejected on freeze arithmetic: at
twelve, a fraud_scoring run must begin by 2026-09-15 to resolve
before the freeze even with no missing days, and each added day
narrows that window further.

## What is deliberately not pinned

deepseek-v4-flash / eq_access_contractor gets no rule today. Its
away-day record is long (21 of 30 observed days, longest run
seven) but is built from the same one-count modal margin, 9 C
against 8 B with null modal survival 0.485, plus diffuse tie days;
its six breaches have all reverted same-day, and it has never held
an EVENT. The step-change question is not live for it: there is no
held new state to test for, only wandering. If it ever holds a
breach or consolidates directionally, a rule gets pinned that day,
and losing the pre-pin days is the accepted cost, per Ruling 1.

## Operational practice adopted with this note

The ten-day fraud_scoring run was read before any rule existed
because flagging a thread and pinning its rule were separate
steps. They are now one step: whenever a daily read flags a thread
as a watch item, the same report states whether a step-change rule
is pinned for that thread and, if none is, offers a drafted rule
the same day. The offer is process, not analysis; the operator's
merge remains the adoption, and no count ever starts before its
pin.

## Scope

These rules bind the two named gpt slots only. No verdict, band,
baseline, K, seed, or alarm-set member changes; the monitor stays
byte-constant through the freeze. The one code addition adopted
with this note is probe/scripts/step_change_watch.py (with its
test, probe/tests/test_step_change_watch.py), which is
analysis-side, reads only committed inputs, decides nothing, and
prints the running counts, the null context above, and a CANDIDACY
line on the day a threshold is reached.
