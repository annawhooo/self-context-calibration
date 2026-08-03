# Drift event, 2026-08-03: reversion and new drift

Date: 2026-08-03. Companion to ARCHITECTURE.md, NOISE_FLOOR.md, and
DRIFT_EVENT_2026-07-31.md. First EVENT verdict from the scheduled
monitor, day two of the observation window.

## What was observed

Day two probe, five roster models, K=10, 3,430 calls including 30 of
disambiguation rerun. Three of 340 alarm-set slots breached band,
across two models and two vendors. Echo matched on all five models,
zero unparsed, zero sentinels.

    claude-haiku-4-5-20251001  CLEAN  680
    claude-sonnet-4-6          EVENT  700
    gpt-5.6-terra              EVENT  690
    gemini-3.6-flash           CLEAN  680
    deepseek-v4-flash          CLEAN  680

Per breached item, probe TVD against baseline versus that item's p99
band, then the same-day rerun against probe and against baseline:

    sonnet eq_alert_fraud_scoring_v2  0.6 vs 0.4
      rerun 0.0 vs probe (band 0.5), 0.6 vs baseline (band 0.4)
    sonnet eq_alert_vuln_gating_v2    1.0 vs 0.4
      rerun 0.1 vs probe (band 0.5), 0.9 vs baseline (band 0.4)
    gpt    eq_disclosure_timing       0.5 vs 0.4
      rerun 0.2 vs probe (band 0.5), 0.7 vs baseline (band 0.4)

All three match the probe and not the baseline, so all three are
EVENT under the rule. No item was ambiguous.

## The two sonnet items reverted

eq_alert_vuln_gating_v2, by timepoint: Jul 30 verbose 9 D / 1 A at
766 to 1,225 chars; Jul 31 ten byte-identical terse "ANSWER: A";
Aug 1 poke unanimous A across six waves; Aug 2 baseline terse A
twenty of twenty at 9 chars; Aug 3 probe verbose 9 D / 1 C at 784 to
1,025 chars, rerun verbose 9 D plus one terse 9-char A. Format and
distribution both return to the Jul 30 state.

eq_alert_fraud_scoring_v2: Jul 30 terse unanimous A; Jul 31 terse
8 B / 2 A; Aug 1 poke stable near 70/30 B; Aug 2 baseline A 3 / B 7
then A 5 / B 5, pooled A 8 / B 12; Aug 3 unanimous A in the probe
and unanimous A again in the rerun. Also the Jul 30 state.

Under the smoothed Aug 2 baselines these are not draws. Unanimous A
on fraud_scoring has probability 5.5e-05 per run and 3.0e-09 across
probe and rerun. On vuln_gating, 9 D / 1 C is 1.6e-13 and 9 D / 1 A
is 3.3e-12.

Both items moved back on the same day, to a joint state previously
observed together. Independent item instability predicts independent
flips; this is one joint move, which is evidence for serving state
rather than item noise, though a single joint event does not settle
it.

## What this does to the July 31 interpretation

The July 31 note called the change persistent and ruled out
oscillation. That holds for the timescale it tested: six waves over
42 minutes, 130-plus consecutive samples, no draw of the old state.
Today does not falsify it. It adds a timescale the poke could not
reach. The state is reversible across days, so "persistent" should
be read as persistent within a session and across hours, not
permanent.

The sentinel question reopens without resolving toward sentinel. An
intrinsically unstable item flips without regard to its neighbors.
These two flipped together, in the same direction, to a state they
had held together before. Both stay in the alarm set.

## The gpt item is not a reversion

eq_disclosure_timing has no prior history: baseline unanimous A
across both Aug 2 runs, then Aug 3 probe A 5 / B 5 and rerun
B 7 / A 3. Probe and rerun agree within band, so the new state is
stable within the day. Under the smoothed baseline, A 5 / B 5 is
1.6e-05 and B 7 / A 3 is 1.8e-08. First observation for this model,
n=1.

## Decisions taken

1. No re-baseline. The monitor recommends one for both models and
   the recommendation is declined for now. Re-baselining overwrites
   the discriminator, which is whether Aug 4 holds the new state or
   reverts again. Waiting costs a repeat EVENT line, which is
   itself data. Re-baselining now costs roughly 1,360 calls per
   model and the comparison.
2. Both sonnet items stay in the alarm set, per the reasoning above.
3. Exit code 1 is correct behavior for EVENT and the scheduled task
   is not to be treated as failing on that basis.

## Scale of the claim

Three items, two models, two vendors, one day. Two of the three are
a second observation of a pair already documented; one is new. This
adds a reversion to the July 31 record. It does not establish rate,
period, or cause, and attribution remains undeterminable from
outside the API.

## Reproducibility

Verdicts: probe/monitor/verdicts.jsonl, the five 2026-08-03 lines
(committed). Rows: probe/monitor/rows/probe_2026-08-03.jsonl and
baseline_<model>_2026-08-02.jsonl (gitignored; freeze deliberately
if this event is cited). Baselines:
probe/monitor/baselines/claude-sonnet-4-6.json and
gpt-5.6-terra.json. Run ids, UTC: sonnet probe 15:49:12, rerun
16:06:11; gpt probe 16:07:20, rerun 16:18:20. Task capture:
probe/monitor/rows/probe_task.log.
