# Resume chat handoff, 2026-09-11

Audience: the claude.ai chat session helping Anna Hix update her resume.
Purpose: the verified, current state of the research program in this repo
(self-context-calibration), so resume bullets about it are accurate and
every number traces to a committed file. Data is current through the
2026-09-10 monitor run. This is not the research-chat state of record;
that series lives at docs/chat_session_handoff_2026-07-20.md and is
stale on status. This document supersedes any earlier summary given to
the resume chat.

Repo: github.com/annawhooo/self-context-calibration (public).
Author of everything described here: Anna Hix, hix.anna@gmail.com,
independent researcher. Priority date on the probing architecture:
2026-07-28 (probe/ARCHITECTURE.md).

## The program in one paragraph

A pre-registered AI-honesty and AI-reliability measurement program
built around one instrument: a 68-item forced-choice enterprise
security judgment bank (45 clear-cut, 23 designed-equipoise). Three
studies and one live instrument share it. Study one measures whether a
model can tell that its own prior committed decision was silently
removed from context, versus confidently asserting an answer it can no
longer see. Study two runs the same bank across ten models from five
providers to measure cross-vendor judgment convergence. The live
instrument points the bank at five production APIs daily and watches
for behavioral drift behind stable model ids. Everything is public:
pre-registrations locked before data, dated decision records,
corrections kept on the record, and a rule that no number is reported
without a script behind it.

## What exists, with verified numbers

All numbers below were recomputed or re-read from the committed record
on 2026-09-11. Source paths in parentheses.

1. Faithful self-context study (v1.5). Complete. Pre-registration
   locked 2026-07-22, tag prereg-lock-2026-07-22, before the first
   real run; run the same day on three Claude models. Committed read:
   results/faithful_realrun_analysis.txt. Supporting baseline
   campaign: 2,850 rows across the three models, K=10 over the full
   bank plus K=30 on identifying pairs (README.md, Status;
   docs/baseline_run_note_2026-07-19.md).

2. Cross-vendor convergence study. Complete. Pre-registration locked
   2026-07-24, tag prereg-lock-convergence-2026-07-24; collection
   finished 2026-07-28. 12,240 rows, ten models, five providers
   (Anthropic, OpenAI, DeepSeek, Z.ai, Google), 18 model-arm cells at
   exactly 680 rows each, one echoed model id per cell, 60 unparsed
   rows total (0.49 percent). Committed read:
   convergence/analysis/convergence_report.md.

3. Drift monitor. Live since 2026-08-02, daily at 13:00 UTC, five
   models from four vendors, frozen August 2 baseline that is never
   updated, per-item total variation distance against
   simulation-calibrated p99 alarm bands, same-day disambiguation
   rerun on every alarm, committed verdict log. As of 2026-09-10: 40
   observation days, 200 model-day verdicts, 191 covered (9 ERROR
   model-days from credential outages, each an explicit log line),
   129,871 recorded calls. Verdict mix: 137 CLEAN, 27 EVENT, 25
   TRANSIENT, 1 UNSTABLE, 1 ECHO_CHANGE. Operating cost about 20 USD
   per month. (probe/monitor/verdicts.jsonl; probe/monitor/README.md.)

4. Generalized study (v1). Harness built and piloted clean; the
   pre-registration is still a draft and no real run has occurred. Not
   a completed study; do not put results bullets on it.

5. Talk. "What the auditor sees without receipts," presented to the
   CSA AARM Working Group on 2026-08-21, with a two-page data handout
   committed in-repo (docs/aarm_wg_20260821_handout_v2.pdf). The repo
   never expands the AARM acronym; write "CSA AARM Working Group" and
   do not invent an expansion.

6. Paper in preparation. Target: INTERCEPT, AARM's runtime-security
   venue (San Francisco, Feb 2027), Defenders track, IEEE short paper.
   Full prose draft completed 2026-08-22 (paper/INTERCEPT_DRAFT.md,
   working title "Judgment-Layer Drift, No Changelog"); planned data
   freeze 2026-09-26; submission deadline 2026-10-01. NOT yet
   submitted as of 2026-09-11.

## Headline findings a resume can carry

Each with the supportable phrasing and where it is recorded.

- Self-context calibration splits by capability, inverted. With its
  own prior commitment silently removed, claude-haiku-4-5 abstains 80
  percent of the time, while claude-opus-4-7 and claude-sonnet-4-6
  confidently answer anyway at 90 and 97 percent (pooled
  non-abstention under absence, the v1 secondary). The pre-registered
  mixture read attributes that confident answering almost entirely to
  re-derivation from the surviving inputs rather than recall; the
  absence-induced excess endpoint was not substantively detected in
  any model at this N. Say "the stronger models answered anyway and
  the mechanism is re-derivation," not "models lie about their
  memories." (results/faithful_realrun_analysis.txt.)

- Family judgment monoculture, measured. 63 of 68 items unanimous
  across all three Claude models; a same-family reviewer collides
  with a reviewed model's commitment at roughly 0.93, so same-family
  cross-checking confirms self-reports whether or not they are
  faithful. (docs/baseline_run_note_2026-07-19.md, summarized in
  docs/chat_session_handoff_2026-07-20.md.)

- Cross-lab convergence with a measurable family signature.
  Cross-lab agreement 0.8593 against a 0.25 chance floor; within-lab
  exceeds cross-lab by +0.0312, 90 percent interval [+0.0072,
  +0.0583]. Agreement is not accuracy; the study measures
  convergence, not correctness.
  (convergence/analysis/convergence_report.md.)

- Judgment drifts behind stable model ids, and it recurs. Verified
  19-day window (Aug 2 to Aug 20, the handout numbers): 43 alarms,
  every one on judgment pairs, zero alarms in 4,003 clear-cut
  checks; identical ten-answer splits returned on separate days;
  recurrence structure versus the chance-only null at P = 2.9e-11
  (upper bound), while the raw alarm count alone is weak (p = 0.026)
  and is reported that way on purpose. Across 67,070 calls in that
  window the echoed model id carried zero bits: detection without
  attribution. (docs/aarm_wg_20260821_handout_v2.pdf;
  probe/ scripts regenerate every figure.)

- The instrument catches serving-side identity changes. On
  2026-09-10 the monitor logged the record's first echoed-model-id
  divergence (deepseek-v4-flash echoed "deepseek-flash" on one call)
  and halted that model's run by design, an ECHO_CHANGE verdict.
  Fresh, one observation; fine as "tripwire fired as designed," not
  as a vendor claim. (probe/monitor/verdicts.jsonl, 2026-09-10.)

## Skills the record demonstrates

For the chat to mine into bullets; every one is evidenced in-repo.

- Study design: three pre-registrations at different lock states,
  locked-before-data discipline, deviations sections, a committed
  reporting commitment for the monitor, dated decision rules pinned
  before deciding data arrives (probe/STEP_CHANGE_* files).
- Statistics: mixture/residual decomposition, cluster bootstrap,
  Wilson intervals, total variation distance, exact-enumeration
  nulls, simulation-calibrated false-alarm bands, test-retest.
- Engineering: multi-provider elicitation harness (five provider
  adapters) that verifies rather than assumes: reasoning state
  confirmed per response, echoed model id recorded per row with
  collection halt on change, non-greedy sampling proven empirically,
  fail-closed credentials; durable resumable collection;
  deterministic byte-identical analysis; test suites across harness,
  parser, analyzer, and monitor; standard-library-only analysis.
- Operations: a live instrument run daily for 40 days with committed
  verdicts, outages logged as ERROR lines rather than hidden, and
  corrections published (probe/CORRECTIONS_*.md).
- Communication: a two-page practitioner handout that translates the
  statistics into plain language, delivered to a working group.

## Claim discipline (what the resume must not say)

- Nothing here is peer-reviewed or published in a venue yet. One
  working-group talk, one public repo, one submission in
  preparation. Do not write "published," "submitted," or "accepted"
  for INTERCEPT until each is true.
- claude-opus-4-7 and claude-opus-4-8 are different models in
  different studies; never merge them. Repo-wide totals if needed:
  11 distinct models, 5 providers.
- The monitor detects change; it never attributes cause and never
  says "degraded." Keep that asymmetry in any bullet.
- The 19-day statistics end 2026-08-20; the coverage and call totals
  above run through 2026-09-10. Do not mix the windows in one claim.
- Scale honestly: committed study totals are 2,850 baseline rows,
  12,240 convergence rows, and 129,871 monitor calls. Do not add
  them into one number without labeling what it is.

## Not in this repo; ask Anna

- Her current resume and the target role or job description.
- The Divergence Series and mcp-tap: cited here as sibling work but
  maintained elsewhere. Get their descriptions from Anna before
  writing bullets about them.
- Employment, education, prior talks or publications.
- Whether she wants the WG talk and the INTERCEPT plan named on the
  resume, and how to title her independent-research role.

## Working with Anna

Casual, direct, concise. Data-driven; verify every count with the
code interpreter before asserting it. No em dashes in her prose.
Show proposed edits before applying them; nothing extra without
consent. On catching your own error, correct with "oh, my bad, let
me correct myself" and move on. If a needed reference is missing,
ask instead of guessing.
