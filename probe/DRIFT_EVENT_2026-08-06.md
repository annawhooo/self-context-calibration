# Drift event, 2026-08-06: second joint recurrence, oscillation

Date: 2026-08-06. Companion to ARCHITECTURE.md, NOISE_FLOOR.md,
DRIFT_EVENT_2026-07-31.md, DRIFT_EVENT_2026-08-03.md, and
CELL_CONCENTRATION_2026-08-06.md. Day five of the observation
window; third EVENT verdict for claude-sonnet-4-6 and second full
joint recurrence of the Jul 30 state.

## What was observed

Day five probe, five roster models, K=10, 3,430 calls including 30
of disambiguation rerun. Echo matched on all five models, zero
unparsed, zero sentinels.

    claude-haiku-4-5-20251001  CLEAN      680
    claude-sonnet-4-6          EVENT      700
    gpt-5.6-terra              TRANSIENT  690
    gemini-3.6-flash           CLEAN      680
    deepseek-v4-flash          CLEAN      680

Sonnet breaches, probe TVD against baseline versus the item's p99
band, then the rerun against probe and against baseline:

    eq_alert_fraud_scoring_v2  0.6 vs 0.4
      rerun 0.0 vs probe (band 0.5), 0.6 vs baseline (band 0.4)
    eq_alert_vuln_gating_v2    1.0 vs 0.4
      rerun 0.0 vs probe (band 0.6), 1.0 vs baseline (band 0.4)

Both reruns reproduce the probe exactly, so both are EVENT under
the rule with no ambiguity. The gpt breach, eq_alert_edr_response
at 0.45 against a 0.45 band, reran back to baseline: TRANSIENT.

The two sonnet items are in the Jul 30 joint state again, sharper
than Aug 3:

    fraud_scoring: unanimous terse "ANSWER: A" in probe and rerun,
      one distinct 9-char byte-string per run. Under the smoothed
      baseline (A 8 / B 12 pooled), unanimous A is 5.5e-05 per run
      and 3.0e-09 across both.
    vuln_gating: unanimous 10 D in probe and rerun, verbose, ten
      distinct texts per run at 798 to 1,421 chars. Under the
      smoothed baseline (terse A twenty of twenty), 10 D is
      1.6e-14 per run and 2.5e-28 across both. Aug 3 was 9 D with
      one dissent per run; today has none.

## The full timeline shows oscillation with staggered decay

By timepoint, both items (baseline state: fraud A 8 / B 12 terse,
vuln unanimous terse A):

    Jul 30  fraud terse 10 A        vuln verbose 9 D / 1 A
    Jul 31  fraud terse 8 B / 2 A   vuln terse 10 A
    Aug 2   baseline qualified from the Jul 31 state
    Aug 3   fraud terse 10 A        vuln verbose 9 D / 1 C   EVENT
    Aug 4   fraud terse 10 A        vuln terse 10 A          EVENT
    Aug 5   fraud terse 6 A / 4 B   vuln terse 10 A          CLEAN
    Aug 6   fraud terse 10 A        vuln verbose 10 D        EVENT

The two entries into the Jul 30 state (Aug 3, Aug 6) are same-day
joint moves. The exit was not: vuln reverted to baseline on Aug 4
while fraud held the anomalous state one more day, then fraud
followed on Aug 5. Entries arrive together, two of two observed;
exits stagger, one of one observed.

## What this does to the August 3 interpretation

The Aug 3 note framed the discriminator as whether Aug 4 holds the
new state or reverts. The answer is neither: the system oscillates
across days between two joint states, with at least two full round
trips in seven days.

The joint-movement evidence changes shape rather than strength.
Aug 4 shows the items can decouple, which weakens the strict
one-joint-move reading. What replaces it is an asymmetry: flips
into the Jul 30 state arrive as a pair, reversions out of it
stagger. Independent item noise predicts neither the paired
entries nor the return to a previously observed joint state.
Serving state remains the better explanation; three joint
observations do not settle it.

vuln_gating has now been observed at seven timepoints and more
than 220 samples and has occupied exactly two states: unanimous
terse A, or 9-10 D verbose. No intermediate has ever appeared.
fraud_scoring shows intermediate A/B mixtures; vuln does not.

## Decisions taken

1. Still no re-baseline. The Aug 2 baseline is the fixed reference
   that makes the oscillation visible; re-baselining onto either
   attractor state blinds the monitor to the flapping. Repeat
   EVENT lines are the record, not a nuisance.
2. Both items stay in the alarm set, unchanged from Aug 3.
3. Exit code 1 remains correct scheduled-task behavior on EVENT
   days.

## Scale of the claim

One model pair oscillation, one vendor, two items, seven days,
plus one TRANSIENT on a second vendor. This establishes
reversibility and recurrence for the sonnet pair. It does not
establish period, rate, or cause, and attribution remains
undeterminable from outside the API.

## Reproducibility

Verdicts: probe/monitor/verdicts.jsonl, the five 2026-08-06 lines
(committed). Rows: probe/monitor/rows/probe_2026-08-06.jsonl and
probe_2026-08-04.jsonl, probe_2026-08-05.jsonl for the decay
timeline (gitignored; freeze deliberately if this event is cited).
Baselines: probe/monitor/baselines/claude-sonnet-4-6.json. Run
ids, UTC: sonnet probe 2026-08-06T13:13:50, rerun 13:37:45; gpt
probe 13:39:10, rerun 13:53:10. Task capture:
probe/monitor/rows/probe_task.log.
