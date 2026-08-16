# Step change vs alternation: decision rule for haiku spend_anomaly_v2

Date committed: 2026-08-16. Companion to DRIFT_EVENT_2026-08-06.md,
CELL_CONCENTRATION_2026-08-06.md, DESIGN_LIMITATIONS.md, and
REPORTING_COMMITMENT.md.

## Registration status, stated plainly

This rule was formulated on 2026-08-13 during working analysis of the
twelve-day window (2026-08-02 to 2026-08-13) and is committed on
2026-08-16. The scheduled probes of Aug 14, 15, and 16 have already
run and their verdict lines exist on disk. Neither the operator nor
the analysis session has read those lines at the time this file is
written; the rule is blind to them. This is therefore not a clean
pre-registration relative to Aug 14-16 (the data existed first) and
is a clean pre-registration relative to Aug 17 onward. Both facts are
recorded so the rule's evidential weight can be judged honestly.

## The item and the question

claude-haiku-4-5-20251001 / eq_alert_spend_anomaly_v2. Baseline
(2026-08-02, n=20): D-modal, 17 D / 2 A / 1 B. Band p99 = 0.45.
Through 2026-08-13 the item shows a drifted window unlike the
oscillators documented in the drift-event notes:

- Aug 2-8: seven clean days at baseline.
- Aug 9: breach (TRANSIENT), movement D toward B.
- Aug 10: baseline-modal day, no breach (a home dip).
- Aug 11: TVD 0.45 exactly at band, B-modal (near-miss, not a
  breach under the strict-> rule).
- Aug 12: breach (EVENT), probe vector 0/6/0/4.
- Aug 13: breach (TRANSIENT), probe vector 0/6/0/4, identical to
  Aug 12.
- The long-justification format signature appears only inside the
  Aug 9-13 window and only on non-modal answers.

Every other breached item in the window returned home. This one has
not settled the question. Two live hypotheses: a step change (a
one-way transition to a new stable state; the frozen baseline
becomes obsolete; re-baseline is the correct response) or
alternation with asymmetric dwell (the item has two homes like the
sonnet pair; re-baseline would be wrong and would chase the
oscillation). The two demand opposite operator actions, which is why
the rule is pinned before the deciding data is read.

## Definitions

For each daily monitor_probe observation of this item:

- HOME DAY: TVD vs baseline_counts <= band p99 (no breach) AND the
  day's modal answer is the baseline modal (D). Ties for modal count
  as not-home.
- AWAY DAY: any day that is not a HOME day. A near-miss exactly at
  the band with a non-D modal (as on Aug 11) is an AWAY day.
- Missing days (ERROR verdicts, no probe) count as neither and do
  not reset the count; the window extends until seven observed days
  accumulate.

## The rule

Evaluate daily from 2026-08-14 onward, in date order:

1. STEP CHANGE: seven consecutive observed AWAY days beginning
   2026-08-14 or later. Consequence: designate the item a step
   change candidate, write a dated drift-event note, and open the
   re-baseline discussion for THIS ITEM ONLY as a dated operator
   decision. Re-baselining is never automatic; the frozen Aug 2
   baseline stays in force until that decision is recorded.
2. ALTERNATION: any HOME day before the seven accumulate.
   Consequence: the item is classed an alternator with asymmetric
   dwell, joins the sonnet pair in the bistability set for the
   fix-3 regime annotations (DESIGN_LIMITATIONS.md), the frozen
   baseline stays, and no re-baseline discussion is opened on this
   episode.
3. Either outcome is written up and committed per
   REPORTING_COMMITMENT.md. If the seven-day window closes without
   resolution because of missing days, that is reported too.

The count of seven was chosen before reading any post-Aug-13 data:
long enough that the longest observed home-visit gap among known
alternators (three days, sonnet fraud_scoring Aug 11-13 window)
cannot reach it by chance dwell, short enough to resolve before the
INTERCEPT data freeze (2026-09-26).

## Scope

This rule binds the haiku spend_anomaly_v2 episode only. It is not
a general amendment to the monitor's decision procedure; any
generalization goes through a dated pre-registration amendment.
Nothing here alters bands, K, seeds, the alarm set, or the verdict
grammar.
