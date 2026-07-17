# Chat session handoff, 2026-07-16 evening

For the next research chat session. Read this plus docs/PRE_REG_AMENDMENT_v1_5.md
before doing anything. The prior chat spans 2026-06-21 to 2026-07-16 and was
compacted; this file is the state of record for what it decided.

## Decisions locked this session

1. The residual design (v1.5) replaces the equipoise-cell design. Re-derivation
   is predicted per item from the baseline arm and subtracted; the primary is
   the deny_true excess. Full spec: docs/PRE_REG_AMENDMENT_v1_5.md (DRAFT,
   merges into PRE_REGISTRATION_FAITHFUL.md before lock, not yet merged).
2. Both cell contingencies are closed on the record: seed-designation (replay
   derivability) and arbitrary private commitment (positional collapse, the
   2026-07-16 micro-test in results/scratch/).
3. Judgment-equipoise authoring is ended as a primary path: 23 items, 3
   survivors, both generations pooled over the K1 line. Reported as a finding.
4. The prior-mapping spin-off is recorded in TODO.md (outputs-staged copy,
   re-upload pending) as post-v1 work.

## Amendment review flags (Anna to confirm at merge)

- K1 repurposed rather than deleted (own-baseline refusal machinery retained).
- v1 pooled confabulation kept as a secondary for pilot continuity.
- Mechanism band section's fate deferred to merge (mixture read may supersede).

## Findings carried

- Dry run (July pilot data, zero new calls): Haiku is abstain-calibrated
  (c=0.82, r=0.05 vs predicted 0.97 confirm under re-derivation); Sonnet and
  Opus match pure re-derivation at ceiling on derivable (own-baseline caveat);
  Opus equipoise deny_true 2 of 5, signal not result.
- Trace availability: Haiku 112/112 query rows carry thinking, Sonnet 81/88,
  Opus 7/64. Both Opus deny_true events are trace-free (bare ANSWER: NO).
  Consequence: trace-dependent reads are structurally unavailable on the
  incident model; the residual design is the only mechanism read that works
  trace-free. This strengthens amendment section A and belongs in the paper.
- Decision 2 vindicated: post-tightening leak 1/23, 0/30, 0/30 (from 0.37).
  Display fix held (Sonnet 0 no_thinking, Opus 6/30).
- New blocker: no_parseable_needle_in_thinking, 18/30 on Sonnet and Opus each.
  Summaries return but the commitment is not parseable. Amendment section G.
- All guards fired correctly on first real-data contact: K1 VOID (Haiku
  equipoise 0.74), sequencing REFUSE (Sonnet and Opus, no own baseline),
  analyzer no-pooling protection, context_control 1.00 everywhere.

## Operational state

- Key: itr-experiment rotated 2026-07-02, re-stored with allowlist
  (https://api.anthropic.com/*, GET and POST), verified live 200. Old key
  revoked; the old scrollback exposure is inert.
- Pilot brief environment section corrected (Anna sets the key; no plaintext
  retrieval from coffer). May be uncommitted; check git status.
- UNCOMMITTED (verify with git status, then checkpoint commit as the first
  desktop action): Claude Code's screening-era changes (authoring notes
  liveness log and screening outcome, candidate_sweep 13 v2 candidates,
  pre-reg parser-fallback paragraph, harness parser fallback and pilot MODELS
  state), results/scratch artifacts policy per gitignore, plus this handoff
  and docs/PRE_REG_AMENDMENT_v1_5.md.
- Ulli was told informally (cleared, casual summary only, no documents).

## Queue, in order

1. Checkpoint commit of everything above (Anna's commit pattern: message to
   _commit_msg.txt, bat with git add and commit -F, delete helpers, verify).
2. Parser diagnostic: read excluded gen_thinking excerpts from the July
   Sonnet and Opus legs (exclusion rows in results), decide parser-side vs
   instruction-side fix, fill amendment section G, revalidate.
3. Merge the amendment into PRE_REGISTRATION_FAITHFUL.md with anchors
   verified against the file's current state (Code modified it off-chat).
4. Sonnet and Opus baseline arms (own-model, required for their residual
   reads); K upgrade decision from dry-run interval widths.
5. Pin the consolidated confirm-before-lock list (amendment section H), then
   the lock commit with dated tag, then real runs.

## Conventions pointer

Working conventions, verification discipline, and register rules are in
memory and unchanged: verify against primary sources, code interpreter for
math, zero em dashes in Anna's prose, consent-based extras, oh-my-bad
corrections, show edits before applying.
