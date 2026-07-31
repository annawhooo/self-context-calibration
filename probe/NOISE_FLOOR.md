# Instrument characterization: noise floor and drift signal

Date: 2026-07-31. Companion to ARCHITECTURE.md.

## Question

Whether fixed-bank response distributions are stable enough that a
distribution shift means something. If same-day self-distance is as
large as self-distance across weeks, the instrument measures dice,
not drift, and the tool premise fails.

## Method

Two same-day collection runs (7.5 hours apart, 2026-07-30 local),
Arm A, K=10, claude-haiku-4-5-20251001 and claude-sonnet-4-6, 2,720
calls. Distance is per-item total variation (TVD), averaged over the
68-item bank, computed by the analyzer's compare-runs mode. Reference
points: the frozen three-week test-retest distances, and cross-model
distances from the frozen convergence data.

## Results

Same-day self-distance, mean TVD: haiku 0.0029; sonnet 0.0294, of
which two designed-equipoise items contribute 1.7 of the 2.0 total.
Excluding them, sonnet's floor is roughly 0.005. 66 of 68 items sit
at or near zero on both models.

Three-week self-distance: haiku 0.096, sonnet 0.063 (frozen
supplement). A K-mismatch confound was tested and ruled out:
subsampling the uneven baseline (per-item K 10 to 40) to K=10 over
200 resamples moves the means to 0.0977 and 0.0629. The three-week
distances are not sampling arithmetic.

Cross-model reference: haiku vs sonnet same-day 0.018; either small
model vs opus roughly 0.10 with five full flips.

Signal-to-noise: the three-week distance exceeds the decisive-item
noise floor by roughly 13x (sonnet) to 30x (haiku). Change on pinned
snapshot ids over three weeks is real and detectable on this bank.

## Design consequences

1. Per-item baselines, not a global threshold. Noise is
   item-specific.
2. Decisive items carry the drift alarm. Movement where the model
   commits hard is unambiguous signal.
3. Equipoise items are retained as positive controls, not discarded.
   An item designed to split should show variance; if it goes quiet,
   either the instrument broke or the model's sampling changed, and a
   designed coin-flip answering deterministically is itself a drift
   event (what a silent switch to greedy decoding or response caching
   would look like). Both anomaly directions are signals: decisive
   items going erratic means the model moved; equipoise items going
   quiet means the ruler or the sampler moved.

## Caveats

The three-week comparison crosses collection machinery: baseline rows
came from the faithful harness call path, fresh rows from the
convergence adapters. Prompt and parse rule are byte-identical by
construction; request assembly is not the same code. The 7.5-hour gap
between same-day runs makes the floor conservative (it includes any
intra-day serving variation). Attribution of the three-week change
(weights, quantization, serving config, safety layer) is not
determinable from outside; the claim is change detected, not cause
identified.
