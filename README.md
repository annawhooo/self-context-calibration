# self-context-calibration

An experiment measuring whether a language model can tell that its own prior
committed content has been removed from its context, versus confidently
asserting an answer about content it can no longer see.

Standalone companion to the Divergence Series. The series cites this repo the way
Paper B cites mcp-tap. It is kept separate on purpose, so the executable
experiment, its paid-API harness, and its raw model outputs version independently
from the writing, and so confabulated model text never bleeds into the drafting
repo.

## What this measures

In turn 1 the model assesses four labeled options and commits to the single
highest-risk one. Its committed choice is the needle, and it is the model's own,
never preset. On a later turn that committing turn is either kept (present),
stripped to a content-free acknowledgment that removes the options and the
verdict (absent), or never placed at all (no-needle floor). The model is then
asked what it committed to, with an explicit UNKNOWN abstention option offered as
a first-class choice.

A calibrated model abstains when the content is gone. The failure of interest is
confident non-abstention under absence: the model asserts a choice it cannot
actually recover. The primary endpoint is the present-versus-absent abstention
contrast, per model.

Method framing matters and is load-bearing. This is a standard method, abstention
under unanswerable context and knowledge-gap recognition, pointed at a novel
target: the agent's own dropped prior commitment. It is self-context calibration,
not calibration in general. The standard method is what makes it credible; the
specific target is what makes it new.

## Scope

The repo now holds three studies on one instrument, and each pins its own model
roster.

v1 establishes existence and rate within three Claude models under a constructed
absence manipulation. It does not make a cross-vendor or quirk-versus-general
claim, because three Claude models share training lineage and cannot answer that
question. That question has its own arm now: the convergence study under
`convergence/` runs the shared item bank across ten models from five providers,
under its own pre-registration. A third layer, the drift monitor under `probe/`,
points the same instrument at five served APIs on a daily schedule and watches
for behavioral drift behind stable model ids.

In the writeup, the result section claims only the measured contrast. The
downstream consequences for agent handoffs, audit trails, and assurance live in
discussion, explicitly labeled as implication, not as measured fact.

## Models

There is no single repo-wide model list. Each study pins its roster in code, and
the code is authoritative. This section is a directory of the pins.

v1, generalized and faithful families (`harness/confab_harness_generalized.py`,
`harness/confab_harness_faithful.py`): `claude-opus-4-7`, `claude-sonnet-4-6`,
`claude-haiku-4-5-20251001`. Opus 4.7 is the model from the originating
incident.

Convergence study (`convergence/models.json`; ten models, five providers, 18
model-arm cells):

- Anthropic: `claude-haiku-4-5-20251001`, `claude-sonnet-4-6`, `claude-opus-4-8`
- OpenAI: `gpt-5.6-terra`, `gpt-5.6-sol`
- DeepSeek: `deepseek-v4-flash`, `deepseek-v4-pro`
- Z.ai: `glm-5.2`
- Google: `gemini-3.6-flash`, `gemini-3.1-pro-preview` (both Arm B only;
  Gemini 3.x exposes no way to disable reasoning)

Drift monitor (`probe/monitor/roster.json`; five models, one pinned arm each):
`claude-haiku-4-5-20251001`, `claude-sonnet-4-6`, `gpt-5.6-terra`,
`gemini-3.6-flash`, `deepseek-v4-flash`. `gemini-3.1-pro-preview` is excluded
because its 250-per-day request cap cannot hold a 680-call bank run.

The two opus ids are not interchangeable. The faithful study ran
`claude-opus-4-7`; the convergence roster pins `claude-opus-4-8`. Those are
different models, and their cells are never comparable despite the shared item
bank (`convergence/COLLECTION_LOG.md`, 2026-07-25). Four distinct Claude models
therefore appear across the repo, never more than three within one study.

## Status

- Faithful family (v1.5): complete. Pre-registration locked 2026-07-22, tag
  `prereg-lock-2026-07-22` (`LOCK.md`); real run 2026-07-22; the committed read
  is `results/faithful_realrun_analysis.txt`.
- Generalized family (v1): harness built; pilot ran clean on Haiku (all three
  inspection signs passed) and is excluded from primary per pre-registration.
  `PRE_REGISTRATION.md` remains a draft; no generalized real run has occurred.
- Item bank: 68 items, 45 derivable and 23 equipoise, in `items/items.py`.
  Authoring rationale in `docs/equipoise_authoring_notes.md`.
- Baselines: 2,850 rows across the three v1 models, complete K=10 over the
  68-item bank with identifying pairs at K=30. Run ids and the read rule:
  `docs/baseline_run_note_2026-07-19.md`.
- Analysis: built, `analysis/analyze.py`, both families, standard library only,
  with the test suite in `tests/`.
- Convergence study: collection complete 2026-07-28. 12,240 rows, 18 model-arm
  cells at exactly 680 each. Operational record in
  `convergence/COLLECTION_LOG.md`; deviations in
  `convergence/PRE_REGISTRATION_CONVERGENCE.md`.
- Drift monitor: live since 2026-08-02, daily probes over the five-model
  roster. The first event was caught during threshold calibration
  (`probe/DRIFT_EVENT_2026-07-31.md`); events, decision rules, and the noise
  floor are dated files under `probe/`.

## Layout

```
self-context-calibration/
  README.md                       this file
  PRE_REGISTRATION.md             generalized family (v1); draft until tagged
  PRE_REGISTRATION_FAITHFUL.md    faithful family (v1.5); locked 2026-07-22
  LOCK.md                         what the 2026-07-22 lock covers, and what it does not
  harness/
    confab_harness_generalized.py
    confab_harness_faithful.py
  items/
    items.py                      shared 68-item bank (45 derivable, 23 equipoise)
    candidate_sweep.py            authoring tool; the frozen screening jsonl is the record
  analysis/
    analyze.py                    pre-registered analysis, both families
  results/
    faithful_realrun_analysis.txt committed read of the 2026-07-22 real run
  tests/                          harness, parser, and analyzer tests
  docs/                           dated handoffs and run notes; historical records
  convergence/                    cross-vendor convergence study
    PRE_REGISTRATION_CONVERGENCE.md
    models.json                   ten-model roster, five providers
    collect.py, providers.py, analyze.py
  probe/                          active drift monitor over served APIs
    ARCHITECTURE.md
    monitor/                      monitor.py, roster.json, baselines, verdicts
```

Files under `docs/` and the dated files under `probe/` are records, not living
documentation. They describe the repo as of their date and are not edited to
track later state.

## How to run

Each harness self-documents. Read the docstring at the top of the harness file
for the locked construct and the governing pre-registration before running
anything.

For the v1 harnesses: install `requests`, set `ANTHROPIC_API_KEY` in the shell
from the coffer alias `itr-experiment`, and run. `--models` takes a
comma-separated list of model ids, validated against the harness's pinned
configuration before any API call is made. The generalized harness writes
`results/confab_results_generalized.jsonl` and
`results/confab_exclusions_generalized.jsonl`; the faithful harness writes
`results/confab_results_faithful.jsonl` and
`results/confab_exclusions_faithful.jsonl`.

The generalized harness requests no thinking. Temperature is omitted on all
three v1 models, because claude-opus-4-7 deprecated it entirely (any value
returns a 400); the other two models are kept consistent with it. The
convergence and monitor rosters pin temperature and reasoning handling per
model in `convergence/models.json` and `probe/monitor/roster.json`.

The convergence runner is `convergence/collect.py`; the monitor is
`probe/monitor/monitor.py`. Their handoffs (`convergence/claude_code_handoff_*.md`,
`probe/claude_code_handoff_monitor.md`) record the operating procedure.

## Pre-registration

Three registrations exist, one per study, at different lock states.

- Generalized (v1): `PRE_REGISTRATION.md`, still a draft. It becomes the lock
  only when committed as a dated, tagged record before the first generalized
  real run. Locking it after seeing data defeats its purpose.
- Faithful (v1.5): `PRE_REGISTRATION_FAITHFUL.md`, locked 2026-07-22 before the
  first real run. `LOCK.md` records what is locked, as of which commit, and
  what remains open by design. Changes after the lock go in the document's
  Deviations section, never edited in silently.
- Convergence: `convergence/PRE_REGISTRATION_CONVERGENCE.md`, with its own
  Deviations section. `convergence/COLLECTION_LOG.md` is the operational log;
  methodological changes do not live there.
