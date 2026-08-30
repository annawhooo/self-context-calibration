# Drift window: 2026-08-14 to 2026-08-30

Date: 2026-08-30, covering the seventeen probe days since the last
window note. Companions: DRIFT_WINDOW_2026-08-07_to_13.md,
STEP_CHANGE_CANDIDACY_2026-08-23.md and
REBASELINE_DECISION_2026-08-23.md (the haiku episode, which has its
own dated notes and appears here only in summary),
CORRECTIONS_2026-08-30.md (errors found by the same audit that
prompted this backfill), and REPORTING_COMMITMENT.md. This note is
late: the events of Aug 14 onward accumulated while reporting
shifted to automated verdict pushes, whose commit messages tally
but do not interpret. Written from the committed record; every
figure recomputed by script.

## The window in numbers

Eighty-five model-days: 52 CLEAN, 13 TRANSIENT, 10 EVENT, 1
UNSTABLE (the record's first and only), 9 ERROR. Twenty-six breach
entries, every one a designed-equipoise item; the all-time record
stands at 55 of 55. The exact null
(probe/scripts/recurrence_structure_null.py --start 2026-08-14
--end 2026-08-30) expects 28.0 chance entries for the window
against 26 observed: the count sits AT the null this window,
P(>= 26) = 0.67, and carries no signal at all. The structure
carries everything, as before: four slots hold three or more
entries against 0.031 expected (P = 3.4e-8), one slot holds seven
(haiku spend, P = 1.3e-5), and three of the four deep threads are
unidirectional at every breach, with deepseek contractor the
pinned exception.

## Thread record

- Haiku spend_anomaly_v2: the window's headline, recorded in its
  own dated notes. Summary: seven consecutive observed away days
  (Aug 15 to 23 around the credential outage) fired the
  pre-committed step-change rule; the operator adopted a
  dual-reference re-baseline on Aug 23; the seven post-rebaseline
  days through Aug 30 are all CLEAN against the new B-state
  reference with zero RETURN days against the preserved original.
  Three of those days sat exactly at the 0.45 return boundary,
  blocked only by modal ties, and Aug 26 (3/7/0/0, the item's
  first zero-D day, 0.85 from the original reference) is the
  deepest departure from home ever recorded, invisible to both
  watchers by design (CORRECTIONS_2026-08-30.md, E3).
- Gpt disclosure_timing: four breaches, and a change in kind. Aug
  17 TRANSIENT (probe 4/6, byte-matching the Aug 7 vector); Aug 21
  TRANSIENT at TVD 1.00, unanimous B, the maximum displacement the
  statistic can express, released before the rerun; then Aug 25
  and Aug 27 EVENTs at 0.90 and 0.60 whose reruns HELD the probe
  state, the first held displacements on this slot since Aug 3,
  with full home days (9/1) between and after. Early-window
  breaches on this slot released within minutes; late-window
  breaches persist through the rerun and release overnight. The
  within-day persistence changed; the attractor (B-ward, every
  breach) did not. The monitor recommended a re-baseline on each
  EVENT; declined for now, same reasoning as the sonnet pair: the
  frozen unanimous-A reference is what keeps the flapping visible.
- Gpt vuln_gating_v2: one EVENT, Aug 28, at TVD 0.65, gone the
  next day. This was the slot's SECOND breach, not its first: Aug
  4 breached at the same TVD, A-ward where Aug 28 was B-ward, 24
  days apart, each a one-day spike. The working narrative called
  Aug 28 a first and is corrected here. Cross-vendor recurrence of
  the sonnet flagship item therefore dates from Aug 4, and both
  sonnet-pair items have had cross-vendor counterparts since
  deepseek fraud_scoring_v2's Aug 9 breach.
- Gpt others: access_offboarding breached once (Aug 23, TRANSIENT,
  the 8/0/2/0 family again) and spent most of the window off its
  baseline modal below band; descriptively, it ran six consecutive
  away days under the haiku rule's definitions, one short of that
  rule's threshold, and fraud_scoring ran ten. Those definitions
  bind the haiku episode only; whether they generalize to gpt
  threads is an open operator ruling, flagged, not decided here.
  eq_alert_fraud_scoring logged its first-ever breaches (Aug 19
  and Aug 26, near-identical reverting spikes). patch_timing
  stayed quiet.
- Deepseek: dlp_email_v2 became the vendor's persistent thread:
  TRANSIENT Aug 17, rerun-confirmed EVENTs Aug 19 and 20,
  TRANSIENT Aug 27, D-ward every time, never two home weeks in a
  row; the least settled item in the record at window close.
  contractor produced the record's only UNSTABLE (Aug 15, rerun
  matching neither probe nor baseline) plus TRANSIENTs Aug 17 and
  21; its five-breach direction sequence D, A, C, A, D is mixed at
  every scale. fraud_scoring_v2 (Aug 21) and edr_response (Aug 14)
  each spiked once and reverted.
- Gemini: two TRANSIENTs, Aug 15 (spend_anomaly) and Aug 20
  (spend_anomaly_v2), opposite directions, both members of the
  same item family as the haiku step change, on a third vendor.
  Otherwise the quietest behavioral record in the roster: zero
  EVENTs all-time.
- Sonnet: zero breaches in the window; seventeen observed clean
  days since its Aug 10 EVENT. Below band, both pair items show
  faint echoes of their away states (5/5 fraud ties on Aug 14, 26,
  27; recurring D dissents on vuln_gating from Aug 18), visible
  only in the derived counts.

## ERROR-day taxonomy

Nine ERROR model-days, three causes, only one of them the
provider's: gpt Aug 14 to 16, http 429, exhausted credits (ours);
both Claude models Aug 19 and 20, http 401, a key rotated without
propagating to the task environment (ours; the preflight task now
exists for this class); gemini Aug 22 and 24, http 503 after retry
exhaustion, the record's only provider-side failures, with the Aug
23 gemini run retry-slowed but complete. Provider-side
unavailability may correlate with serving-stack churn, so gemini's
missing days are not ignorable noise; the paper carries the caveat.

## Instrument facts established in this window

- The record push is automated (scheduled task, 12:30, verdicts
  and derived counts committed with tally messages). Its first
  firing caught a mid-probe race and published one half-sampled
  count row; the export is now gated on verdict lines and the row
  was repaired in a dated commit. Commit messages tally; they do
  not interpret. This note exists because that gap let seventeen
  days accumulate without one.
- The dual-reference re-baseline mechanism had its first use and
  behaved as designed, with the sensitivity caveat recorded in
  CORRECTIONS_2026-08-30.md, E3.
- Five breach verdicts in the record, including the only UNSTABLE,
  are decided by floating-point representation: TVD values that
  are exactly 9/20 in rational arithmetic compare as
  0.45000000000000007 > 0.45 in floats on some vectors and not on
  others. The strict-inequality rule is pinned and unchanged; a
  dated float-comparison policy is owed before the freeze analysis
  and is flagged, not decided here.

## Decisions

No re-baselines beyond the haiku decision already recorded. Every
breached item stays in the alarm set. No verdict reclassified.
Bands, K, seeds, and the alarm set unchanged. Open operator items
carried forward: the float-comparison policy, the step-change
definitions ruling for gpt threads, and the return-watch scope
note, each requiring its own dated commit.
