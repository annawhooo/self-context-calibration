# Baseline campaign run note, 2026-07-19

Recovery convention (pinned pre-run, research chat): legs run separately per
model; each leg's run_id is recorded here; if a leg aborts, a top-up run
covers only the missing item and sample slots and both run_ids are recorded;
analysis reads the run_ids in this note and never silently pools duplicate K.

Key: fresh console key created 2026-07-19 after the vault-path incident
(session-scoped interception of the prior coffer server spawn, resolved by
restart, old key to be disabled after the campaign). Key proven by 4-call
smoke test before the first leg (2 items x Sonnet + Opus, 4/4 parsed).

## Legs

- Sonnet baseline: run_id 2026-07-19T16:22:03, 680 rows (68 items x K=10),
  0 unparsed, COMPLETE. Tally: derivable n=450 A=100 B=100 C=110 D=140;
  equipoise n=230 A=47 B=49 C=69 D=65.
- Opus baseline: run_id 2026-07-19T18:46:32, 680 rows (68 items x K=10),
  0 unparsed, COMPLETE. Tally (equipoise): n=230 A=40 B=40 C=78 D=72.
- Haiku top-up: run_id 2026-07-20T01:16:45, 130 rows (13 round-two items x
  K=10, one-off runner reusing the harness's own functions and row schema),
  0 unparsed, all items at exactly K=10, COMPLETE.

Campaign totals: file at 2040 rows. Haiku 680 (550 from run
2026-07-04T15:03:51 over the original 55 items plus this top-up), Sonnet
680, Opus 680. Every model has a complete K=10 baseline over the 68-item
bank. Data collection for the baseline arm is closed; per-model stratum
classification, identifying-stratum interval widths, and the K upgrade
decision read from these run_ids only.

Smoke observation for the record: Opus returned empty thinking on both
baseline-path smoke calls, consistent with the known display gap; harmless
at baseline (answers parse from text), tracked separately for faithful runs.
