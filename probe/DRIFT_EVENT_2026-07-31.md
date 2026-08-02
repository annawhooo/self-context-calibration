# Drift event, 2026-07-31: detection during calibration

Date: 2026-08-01. Companion to ARCHITECTURE.md and NOISE_FLOOR.md.
Supersedes the run-bistability interpretation considered during
threshold validation; that interpretation was wrong and is recorded
below because the correction is part of the record.

## What was observed

Between 2026-07-30 20:20 UTC and 2026-07-31 03:28 UTC,
claude-sonnet-4-6 (a pinned snapshot id) changed behavior on exactly
two of 68 bank items and held every other item at the noise floor.

Three timepoints, Arm A, K=10:

- run1 (Jul 30): eq_alert_vuln_gating_v2 answered in a verbose
  reasoning format, ten distinct texts of 766 to 1,225 chars, 9 D /
  1 A. eq_alert_fraud_scoring_v2 answered ten byte-identical terse
  "ANSWER: A".
- run2 (Jul 31): vuln_gating ten byte-identical "ANSWER: A";
  fraud_scoring terse, 8 B / 2 A.
- poke runs (Aug 1): six waves over 42 minutes plus one full-bank
  run. vuln_gating unanimous A every wave; fraud_scoring stable near
  70/30 B across waves. 130+ samples produced exactly two distinct
  byte-strings total.

Full-bank comparison: today vs run2, mean TVD 0.0074, 68/68 modal
matches, no flips. Today vs run1, mean TVD 0.0309, with 90 percent
of the distance mass in the two items above (1.9 of 2.1).

## Interpretation

A persistent behavioral change occurred within the seven-hour window
between the two calibration runs, affecting two items and nothing
else. Supporting arithmetic: run1's unanimous fraud_scoring draw has
probability on the order of 1e-6 under the current stable
distribution, so run1 sampled a different state, not a noisy draw of
this one. Oscillation is ruled out by six stable waves; time-of-day
is ruled out because run1 and the poke waves ran in the same local
afternoon window with opposite behavior; per-request routing lottery
is ruled out by 130+ consecutive samples never drawing the old
state.

Attribution is not determinable from outside the API. The change
could be a safety-layer adjustment, a decoding or serving config
change, or prompt handling these two items happen to be sensitive
to. The narrowness (2 of 68 items) is itself information: a
whole-model swap would not look like this.

Scale of the claim: n=1 event, one model, one vendor. It instantiates
the prior that serving stacks change quietly behind stable ids; it
does not establish frequency.

## The interpretation that was wrong

During threshold validation these two items exceeded smoothed
simulation bands and were provisionally classed as run-bistable
sentinels: items intrinsically sensitive to serving state, to be
excluded from the alarm set. A 42-minute six-wave probe falsified
this: the items are not intrinsically unstable, they were mid-flip
during calibration. Had the sentinel classification shipped, both
items would have been permanently discarded from the alarm set and
their signal lost. The falsifying probe cost roughly 120 calls.

## Design consequences

1. The two-run baseline qualification stands, with a revised
   rationale: items whose run-pair distance exceeds smoothed
   simulation bands indicate either intrinsic instability or a drift
   event straddling calibration. The response is not exclusion; it
   is a third same-day run. If the third run matches the second, a
   drift event occurred during calibration and the baseline is the
   post-event state. If it matches neither, the item is intrinsically
   unstable and becomes a sentinel.
2. Sonnet's corrected noise floor is 0.005 to 0.007 on all 68 items,
   matching haiku. No item on this bank is intrinsically run-level
   unstable as far as current data shows.
3. Item sensitivity is uneven and useful: the two items that moved
   are contested judgment items near a decision boundary. A drift
   bank benefits from including boundary items precisely because
   narrow serving changes surface there first.

## Reproducibility

Rows: convergence/results/poke_bistable.jsonl and poke_fullbank.jsonl
(gitignored; freeze deliberately if this event is cited).
Comparisons: convergence/analysis_runs/poke_vs_run1.json and
poke_vs_run2.json. Probe script: probe/scripts/poke_bistable.py.
Threshold validation: probe/scripts/validate_sim_thresholds.py.
