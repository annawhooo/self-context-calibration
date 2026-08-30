# Drift window: 2026-08-07 to 2026-08-13

Notice, 2026-08-30: the contractor direction claim below ("D-ward
at the peaks") is wrong for Aug 11, which is A-ward under the
pinned direction rule. See CORRECTIONS_2026-08-30.md, E2. Original
text preserved unedited.

Date: 2026-08-16, covering the seven probe days between the last
dated event note (DRIFT_EVENT_2026-08-06.md) and the twelve-day
analysis cutoff. Companions: NOISE_FLOOR.md, DESIGN_LIMITATIONS.md,
CELL_CONCENTRATION_2026-08-06.md, STEP_CHANGE_DECISION_RULE and
STEP_CHANGE_RESOLUTION (2026-08-16), REPORTING_COMMITMENT.md. The
haiku episode that began in this window resolved under the committed
rule and is documented there; this note records the window itself.
Written after the fact from the committed verdict record and raw
rows; every figure recomputed by script.

## The window in numbers

Thirty-five model-days: 21 CLEAN, 8 EVENT, 6 TRANSIENT, no UNSTABLE,
no ERROR. Twenty breach entries, 10 EVENT and 10 TRANSIENT at item
level, every one a designed-equipoise item. By model: gpt 8,
deepseek 6, haiku 3, sonnet 3, gemini 0. The smoothed-truth null
(probe/scripts/expected_false_breaches.py) predicts 11.5 chance
breaches for a seven-day window; the count excess is mild, and the
count is not the signal. The structure is: the entries concentrate
on repeat threads, and every repeating thread moved the same
direction every time.

## Thread record

- Sonnet pair: co-breach on Aug 7 (fraud_scoring and vuln_gating,
  both EVENT; fraud at 9/1 with a 10/0 rerun, vuln at 2/0/0/8).
  Fraud EVENTed alone on Aug 10 at exactly 10/0/0/0, its fourth
  identical visit to that state. Vuln has not breached since Aug 7.
  The pair decoupled again after moving jointly.
- Gpt patch_timing: a two-day pulse. EVENT Aug 7 (7/3), TRANSIENT
  Aug 8 (5/5, rerun 2/8), exact baseline 0/10 every day after.
- Gpt offboarding: the oscillation continued through the window.
  Breaches Aug 8 (TRANSIENT), Aug 9 (EVENT), Aug 11 (EVENT), Aug 13
  (TRANSIENT), with exact vector recurrence: 8/0/2/0 on Aug 8 and
  13 (third occurrence counting Aug 4), 9/0/1/0 on Aug 9 and 11.
  Rerun outcomes are inconsistent across identical probe states,
  which is the gate wobbling, not the state.
- Gpt disclosure_timing: two single-day spikes (TRANSIENT Aug 7 and
  Aug 9). The Aug 9 spike is the sharpest sub-day observation in
  the record: probe 2/8, rerun 8/2 roughly fifteen minutes later.
  Whatever state produced the probe had already released by the
  rerun.
- Deepseek contractor: first EVENTs for this model, Aug 9 and
  Aug 11, D-ward at the peaks of its continuous wander.
- Deepseek fraud_scoring_v2: EVENT Aug 9 (2/2/2/4). Cross-vendor
  recurrence of sonnet's flagship item, and not synchronized:
  sonnet sat in its baseline state (2/8, CLEAN) the same day.
- Haiku spend_anomaly_v2: first-ever haiku breaches. TRANSIENT
  Aug 9, a home day Aug 10, TVD exactly at the band Aug 11 (0.45,
  not a breach under strict >), EVENT Aug 12 and TRANSIENT Aug 13
  on the identical vector 0/6/0/4. Classified an alternator on
  2026-08-16 under the pre-pinned rule; see the resolution note.

Aug 9 was the widest day in the record: five of the eight focal
threads breached, spanning gpt, deepseek, and haiku, while both
sonnet threads sat at baseline. Gpt offboarding and deepseek
contractor breached on exactly the same two days (Aug 9 and 11,
contractor's only breaches). Slots within a model-day share a
scaffold and the providers do not, so same-day cross-vendor
co-movement is noted as observation, not inference.

## Instrument facts established in this window

- Hour is dead as a confound for day-over-day changes here: every
  probe from Aug 4 onward started at 13:00 UTC within one second,
  and per-model start spread across the window is at most 18
  minutes (at most 3.1 for the Claude models).
- The persistence an EVENT actually certifies is minutes, not the
  roughly twenty of Limitation 8: across the twelve-day record the
  item-level gap between last probe sample and first rerun sample
  runs 0.43 to 5.28 minutes, median 2.4. EVENT and TRANSIENT are
  therefore weaker labels than designed, and the cross-day
  recurrence structure carries the persistence evidence instead.
- The equipoise concentration continued: with this window the
  all-time record stood at 29 of 29 breach entries on eq_ items.
  Working analysis after the window put the honest eq share of
  null breach mass at 0.381 (not the 0.338 uniform share used in
  CELL_CONCENTRATION_2026-08-06.md, whose text stands unedited per
  the correction pattern); the concentration survives the honest
  weighting.

## Decisions

No re-baselines. Every breached item remains in the alarm set. No
verdict was reclassified. The window closed with the instrument
unchanged: same bands, same K, same seeds, same baselines.
