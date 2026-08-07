# Design limitations of the drift monitor

Date: 2026-08-04. Companion to ARCHITECTURE.md, NOISE_FLOOR.md,
DRIFT_EVENT_2026-07-31.md, and DRIFT_EVENT_2026-08-03.md.

Three days of monitoring produced six EVENT entries. Before more
data accrues, this note audits the design against its own output.
The locked decision rule is unchanged; nothing here is applied
retroactively. These limitations attach as caveats to every verdict
until the fixes at the end are in place.

## Corrected false-breach expectation

Working analysis on 2026-08-03 estimated chance breaches as 340
slots times 1 percent, or 3.4 per day. That arithmetic treats p99
as an exact exceedance rate. On a discrete statistic at K=10 it is
not: the band is the smallest value with at least 99 percent
coverage, and the true tail mass varies per item, often far below
1 percent. The corrected expectation, by exact enumeration over all
286 compositions of 10 draws into 4 options, per item, against each
item's band p99 (strict inequality, TVD versus the empirical pooled
baseline):

    truth = smoothed baseline    1.64 expected false breaches/day
    truth = empirical baseline   0.05 expected false breaches/day

Per model, smoothed: haiku 0.30, sonnet 0.31, deepseek 0.38, gemini
0.32, gpt 0.32. The naive figure appeared only in working analysis,
not in a committed document; it is recorded here so the correct
number is the citable one. Observed breach counts (0, 3, 3 on Aug
2, 3, 4) exceed the honest null on both readings.

## Limitation 1: cross-day variance was never measured

The bands derive from a within-day run-pair bootstrap on the Aug 2
baseline. They are deployed on cross-day comparisons. Those are
different quantities. Providers plausibly vary at day scale
(deployments, routing, serving config) in ways hour-scale sampling
never observes. The data shows the predicted signature: the Aug 2
same-day probe, run at 22:24 UTC against a baseline collected hours
earlier, produced 0 breaches in 340 slots. Both cross-day probes
produced 3. The monitor therefore cannot currently distinguish a
drift event from ordinary between-day serving variance, because the
noise floor was measured on the wrong timescale. NOISE_FLOOR.md
characterized within-day and three-week distances on an earlier
instrument generation; the day-to-day gap between them was never
characterized on this one. This is the largest validity threat to
the EVENT label.

## Limitation 2: qualification selects for lucky-quiet items

The 68 alarm items per model qualified by run-pair agreement on Aug
2. Conditioning on observed quietness selects items whose sampled
variance understates their true variance. The corrected
expectations above are therefore lower bounds, and regression to
the mean manufactures apparent drift on the days that follow. This
compounds Limitation 1 in the same direction: false EVENTs.

## Limitation 3: baseline as point estimate, bimodal items

Bands treat the n=20 baseline as truth; baseline sampling error is
not propagated. Worse, eq_alert_fraud_scoring_v2 on sonnet looks
bimodal: unanimous A (Jul 30), 8 B / 2 A (Jul 31), roughly 70/30 B
(Aug 1 poke), A 3 / B 7 and A 5 / B 5 (Aug 2), then four
consecutive unanimous-A runs (Aug 3 and 4). The pooled baseline
A 8 / B 12 is a mixture average that possibly no regime ever
produces. An item like that emits a standing EVENT whenever it
occupies its A regime, and the rerun gate confirms it every time,
because the gate cannot distinguish "probe moved" from "baseline
mis-centered." This also bounds the 6-of-6 EVENT inference: zero
TRANSIENTs is evidence against probe-side sampling noise, and
equally consistent with baseline error. The three excursions that
later reverted cleanly into band argue those baselines are
well-centered; the standing sonnet EVENT is the one where the
phantom-mixture reading stays live. The design assumes stationary
unimodal per-item multinomials. This item violates it.

## Limitation 4: every event so far is a designed-equipoise item

The bank contains 23 designed-equipoise items (eq_ prefix) and 45
decisive items; 115 of 340 slots, a 0.338 share. All six breach
entries, five distinct slots, are eq_ items. Under uniform spread
that has probability under 0.005. The drift signal concentrates
entirely in the class designed to sit near decision boundaries.

Two consequences. First, boundary items are the sensitive sensors,
so concentration there is partly expected. Second, and worse:
several breached baselines were quiet equipoise, unanimous A on
items designed to split (sonnet eq_alert_vuln_gating_v2, gpt
eq_disclosure_timing, both A twenty of twenty). NOISE_FLOOR.md
consequence 3 states that a designed coin-flip answering
deterministically is itself an anomaly. For those items the monitor
enshrined an anomalous state as the reference and then alarmed on
movement toward designed behavior. The sign of the anomaly may be
inverted: the baseline was the excursion. The alarm set currently
carries no class distinction between decisive and equipoise items,
so the verdict line cannot express this.

## Limitation 5: hour of day is confounded with day

The three probes ran at 22:24, 15:49, and 13:11 UTC. Every
"reverted next day" statement is equally "different at a different
hour." The Aug 1 poke covered 42 minutes. Nothing in the schedule
separates day boundaries from diurnal serving variation.

## Limitation 6: the leading indicator on format flips is untracked

Sonnet eq_alert_vuln_gating_v2 flips terse-A to verbose-D in
lockstep at every timepoint, both directions (terse 9-char rows
versus 766 to 1,225 char reasoned rows). Response format is a
serving-state observable that moves with the answer, and TVD over
parsed letters registers it only when the letter moves. Raw text is
captured per row, so the signal is recoverable, but no length or
format statistic is tracked or reported. Parser validity was
hand-checked on the Aug 3 verbose rows: both sampled rows end with
an explicit ANSWER: D line, tier 1 extraction, so the D counts are
real and extraction is not the artifact.

## Limitation 7: infrastructure covariates are dead on arrival

The host field is None for four of five providers and holds a prose
note for deepseek, which is schema misuse rather than data.
reasoning_detected is constant per model (gemini always true, the
rest always false), so it cannot covary with drift. temperature_sent
is None for four of five providers. No latency is recorded. The
layer of the design that would support infrastructure attribution
has no data feeding it, which matters because attribution from
outside the API is the point of the study.

## Limitation 8: smaller items

Slots within a model-day share a scaffold and are not independent;
day-level breach counts are overdispersed relative to independent
arithmetic. The roughly 20-minute probe-to-rerun gap cannot demote
hour-scale transients, so EVENT certifies persistence over minutes,
not "stable within the day." The joint-move argument in the Aug 3
note weakened on Aug 4 when the two sonnet items decoupled, one
holding and one reverting. Both new gpt drifts and the persistent
sonnet drift move toward option A; whether that is first-option
bias or movement toward the bank's general attractor is
undetermined, since A is also the modal baseline answer.

## What stands

The architecture is not the problem. The frozen out-of-band
reference, the pre-committed decision rule, the rerun gate, and the
reporting commitment all functioned as designed, and the excursions
that reverted returned precisely into band, which shows the
machinery is well-centered for most items. What failed is one
calibration assumption: stationary unimodal per-item distributions,
with within-day variance standing in for between-day variance.
Limitations 1 through 4 are faces of that assumption. Its failure
biases toward false EVENTs, the conservative direction for a
monitor and the wrong one for a paper claim.

## Bearing on prior notes

DRIFT_EVENT_2026-08-03.md framed Aug 4 as a two-way discriminator,
hold or revert. Aug 4 did both on different items and added two
more; the framing was too coarse. Its joint-move inference is
weakened per Limitation 8. Its item classifications stand. Original
text preserved unedited, following the NOISE_FLOOR.md correction
pattern.

## Fixes

None of these alter the locked rule without a dated amendment.

1. Forward instrumentation in the harness: populate host from the
   actual endpoint, record per-call latency, record response length,
   fix temperature_sent capture. Harness work, Claude Code.
2. Pre-registered recalibration policy: accumulate cross-day CLEAN
   observations into per-item between-day distributions; derive
   corrected bands from those; write the policy, with its trigger
   date and formula, before any corrected band is applied. The Aug 2
   reference stays frozen; recalibration derives new bands, it does
   not re-baseline.
3. Class annotations in the verdict path: tag equipoise versus
   decisive per item, and add a regime status for items whose
   observed states match previously observed states but not the
   pooled baseline, so a standing EVENT is distinguishable from a
   new one.
4. Commit the exact-enumeration script behind the corrected
   expectations (probe/scripts/expected_false_breaches.py) so the
   1.64 and 0.05 figures are regenerable from the committed
   baselines with no network.
