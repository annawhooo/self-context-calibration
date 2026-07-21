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

## Baseline analysis findings (2026-07-20, research chat)

All numbers below read only the run_ids in this note, K=10 per item per
model over the 68-item bank, zero unparsed rows.

1. Capability-convergence gradient. Interior items (0.5 < p(modal) < 1.0)
   fall from 13 (Haiku) to 6 (Sonnet) to 3 (Opus); Opus has zero items at
   or below 0.5, and the three equipoise survivors sit at 0.7 under Opus
   judgment. The equipoise-authoring negative result generalizes: judgment
   equipoise on this content is progressively destroyed by model strength.
2. Model-relative item roles, demonstrated. Three nominally derivable items
   (secret_storage, backup_policy, api_rate_limit) sit interior for Haiku;
   authored-equipoise items sit at anchor for Opus. Fixed-cell designs are
   mis-specified for cross-model comparison.
3. Family-level judgment monoculture. All three models share the same modal
   option on 63 of 68 items (Sonnet-Opus 64 of 68); the five non-unanimous
   items are all equipoise-authored, and the derivable bank is unanimous 45
   of 45. Pooled modal shares 0.934, 0.969, 0.990 rising with capability. A
   same-family reviewer re-deriving a judgment collides with the reviewed
   model's commitment at roughly 0.93, so same-family cross-checking
   confirms a self-report at the collision rate whether or not the report
   is faithful. Quantitative instance of the monoculture-collapse mechanism.
4. Protocol-compliance split. Median response is the bare 9-character
   ANSWER line for all three models, but Opus is byte-uniform (mean 9, max
   9 across 680 responses: literal compliance on every call), Sonnet
   elaborates freely (mean 388, max 1518), Haiku sits between (mean 65).
5. Answer-channel robustness. 1,490 fresh calls across three models with
   zero unparsed baseline answers; instrument fragility observed in this
   project is confined to the thinking channel.
6. Identification structure. a is well-identified for every model (52 to 65
   anchor items each); r is thinly identified on Opus (3 interior items);
   Wilson 90% width at p(modal)=0.7 is 0.43 at K=10, 0.32 at K=20, 0.27 at
   K=30. The K upgrade applies to 22 interior item-model pairs total.

Faithful-side claims remain out of scope for this note: no primary-endpoint
measurement exists yet; the July faithful legs are pilot data, descriptive
only. Open decisions on the confirm-before-lock list: the K upgrade choice
and per-model identifying-stratum N language in the pre-registration.
