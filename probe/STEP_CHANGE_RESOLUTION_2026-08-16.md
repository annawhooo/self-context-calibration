# Resolution: haiku spend_anomaly_v2 is an alternator

Date: 2026-08-16. Companion to STEP_CHANGE_DECISION_RULE_2026-08-16.md
(the rule this note applies), DRIFT_EVENT_2026-08-06.md, and
DESIGN_LIMITATIONS.md. Rule committed at dcdd15c before any
post-Aug-13 verdict line was read; evaluated the same day, minutes
later, by the same session. Recorded per REPORTING_COMMITMENT.md.

## Outcome

Alternation, not a step change. Clause 2 of the rule fired on the
first evaluated day. The re-baseline question is closed for this
episode: the frozen Aug 2 baseline stays in force, and
eq_alert_spend_anomaly_v2 joins the sonnet pair in the bistability
set for the fix-3 regime annotations.

## The classified days

Baseline: 17 D / 2 A / 1 B (n=20, D-modal), band p99 = 0.45.

| date | probe A/B/C/D | TVD | breach | modal | class |
|---|---|---|---|---|---|
| 08-14 | 0/4/0/6 | 0.350 | no | D | HOME |
| 08-15 | 0/6/0/4 | 0.550 | yes | B | AWAY |
| 08-16 | 0/6/0/4 | 0.550 | yes | B | AWAY |

Aug 14 is a HOME day under the committed definitions (no breach and
baseline-modal D), which classifies the episode as alternation with
asymmetric dwell before any away-count could accumulate. The
monitor's own verdict lines agree with the recomputed values: CLEAN
on Aug 14; EVENT on Aug 15 and Aug 16, both with the same-day rerun
confirming the away state held through the rerun window.

## What the episode now looks like in full

Aug 2-8 home (seven days). Aug 9 away (TRANSIENT). Aug 10 home.
Aug 11 away shape at exactly the band (0.45, not a breach under
strict >). Aug 12-13 away (EVENT, TRANSIENT). Aug 14 home. Aug 15-16
away (EVENT, EVENT). The away state is discrete and exact: the probe
vector 0/6/0/4 has now occurred four times identically (Aug 12, 13,
15, 16). The Aug 14 home visit (0/4/0/6) is the near-mirror of that
away state. This is the sonnet oscillation pattern with the dwell
asymmetry inverted: this item rests away and visits home, where
sonnet fraud_scoring rests home and visits away. It is the second
alternator documented on a second vendor.

## What this resolution is and is not

It is the mechanical application of a rule whose definitions were
pinned before the deciding data was read; no judgment was exercised
between rule and outcome. It resolved by the alternation clause,
which is the outcome requiring no operator action, so the late (blind
rather than pre-registered) commitment of the rule has no
self-serving direction. It binds this episode only. If the item
later sustains a long unbroken away run, that is a new episode and a
new dated note, evaluated under the same definitions unless amended
first. Nothing here changes bands, K, seeds, the alarm set, or any
baseline.
