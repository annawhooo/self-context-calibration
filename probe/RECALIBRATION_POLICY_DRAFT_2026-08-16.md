# DRAFT: pre-registered recalibration policy (DESIGN_LIMITATIONS fix 2)

Status: DRAFT, not in force. This policy binds nothing until the
operator adopts it by commit; adoption before the effective date is
what makes it a pre-registration. Drafted 2026-08-16 from the
measured between-day variance of the first twelve probe days
(2026-08-02 to 2026-08-13), working analysis verified by independent
recomputation.

## What this policy does and refuses to do

It derives new alarm bands for the DECISIVE item class only, from
accumulated cross-day observations, at a dated trigger. It does not
touch the equipoise class, the frozen Aug 2 baselines, K, seeds,
sims, smoothing, the alarm-set membership, or any past verdict. The
Aug 2 reference stays the reference: recalibration derives bands, it
does not re-baseline (DESIGN_LIMITATIONS.md fix 2 language).

## Why class-split, in numbers

Measured on the 327 quiet slots of the twelve-day window:

- Decisive class (225 slots, 2,700 slot-days): between-day daily-TVD
  p99 = 0.10, maximum observed = 0.20, zero exceedances above 0.20.
  Current bands 0.40 to 0.45 are roughly 4x above the empirical
  noise ceiling; sensitivity is being left on the table where
  monitoring is free.
- Equipoise class (102 quiet slots, 1,224 slot-days): between-day
  p99 = 0.35 against current bands of 0.40 to 0.50, and the
  between-day component of spread does not shrink with K. There is
  no safe narrowing for this class at K=10; its bands stay as
  qualified.

## The rule, pinned

1. EFFECTIVE DATE: no earlier than 2026-10-02. The instrument stays
   byte-constant through the INTERCEPT data freeze (2026-09-26) and
   submission. The operator picks the exact date at adoption.
2. DECISIVE BANDS: on the effective date, for every decisive-class
   item record in probe/monitor/baselines/*.json, set
   band.p99 := min(band.p99, 0.25) and record
   band.recal = {"date": <effective date>, "policy": this file,
   "basis_days": <n non-breach days observed for that slot>}.
   0.25 is one TVD lattice step above the worst daily value observed
   in 2,700 decisive slot-days; it converts the decisive breach
   threshold from roughly a 5-of-10 answer shift to roughly 3-of-10.
   p95 is left untouched (it is not an alarm input).
3. EQUIPOISE BANDS: unchanged, explicitly including the bistability
   set (sonnet fraud_scoring, sonnet vuln_gating, haiku
   spend_anomaly_v2), which is fix-3 territory, not band territory.
4. MECHANISM: offline recompute script with the sanity-gate pattern
   of the declined K=30 procedure: every new p99 <= its old p99;
   every new decisive p99 in [0.20, 0.30]; equipoise records
   byte-identical before and after; determinism check by running
   twice. One commit: script plus the five baseline files. If any
   gate fails, stop and report; nothing lands.
5. NO RETROACTIVITY: verdicts before the effective date are never
   rescored. The verdict log is append-only history.
6. PRE-REGISTERED ROLLBACK: if decisive-class breach entries exceed
   THREE in the first fourteen days after the effective date, revert
   the decisive bands to their Aug 2 values in one commit and record
   the outcome in a dated note. Expected false alarms at 0.25 from
   the observed data: zero exceedances in 2,700 slot-days; the
   rule-of-three upper bound is 0.11% per slot-day, at most 0.25
   per day across 225 decisive slots. Three in fourteen days sits
   far above that bound, so a trip means the calibration window was
   unrepresentative, and the honest response is retreat plus
   publication, not tuning.
7. OUT OF SCOPE, needs its own amendment if ever wanted: any K
   change for either class; per-item equipoise between-day bands
   (needs more clean days per slot than exist); regime annotations
   (fix 3); any change to the qualification records.

## Known biases, carried openly

The quiet-slot pool conditions on twelve days of not breaching, so
its quantiles are biased low (Limitation 2 selection in a new form).
The 0.25 value is chosen above the observed maximum partly for this
reason, and the rollback criterion is the empirical check on the
remainder. Between-day TVDs also embed baseline sampling error
(Limitation 3); with one frozen baseline the two cannot be
separated, and both push in the direction that makes 0.25
conservative rather than tight. The gpt series carries a three-day
gap (Aug 14 to 16, provider credit exhaustion); slots with fewer
basis days keep their old bands only if their basis_days fall below
40 at the effective date, evaluated per slot by the recompute
script.

## Adoption

To adopt: set the effective date in section rule 1, commit this file
with the word DRAFT removed from the title and status line, and let
the effective date arrive before running the recompute. Anything
else is a deviation and gets its own dated note.
