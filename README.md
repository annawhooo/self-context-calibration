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

v1 establishes existence and rate within three Claude models under a constructed
absence manipulation. It does not make a cross-vendor or quirk-versus-general
claim, because three Claude models share training lineage and cannot answer that
question. The quirk-versus-general question is what the v2 cross-vendor arms
(OpenAI as a generalized-condition bridge, DeepSeek as a second faithful-channel
model) exist to answer.

In the writeup, the result section claims only the measured contrast. The
downstream consequences for agent handoffs, audit trails, and assurance live in
discussion, explicitly labeled as implication, not as measured fact.

## Models

`claude-opus-4-7`, `claude-sonnet-4-6`, `claude-haiku-4-5-20251001`. Opus 4.7 is
the model from the originating incident.

## Status

- Generalized-family harness: built. Collects the present-versus-absent contrast,
  the no-needle floor, and the assertion-true fidelity arm. No thinking
  dependencies.
- Generalized pilot: run on Haiku, clean (all three inspection signs passed:
  present-recall correct, near-zero invalid, absent-recall far below the
  one-in-four chance level). Excluded from primary per pre-registration.
- Faithful-family harness (needle in a thinking block): built and reviewed pre-run
  (see `docs/faithful_harness_review_findings.md`). An Opus probe confirmed the
  committed choice survives summarized thinking, but the review found a
  display-config blocker (Opus needs `display: "summarized"`), needle-parser
  brittleness, and pre-registration gaps to resolve before a real run.
- Analysis script (Wilson, Newcombe, threshold application): not built.
- Pre-registration: content agreed, not yet locked. Must be committed as a dated,
  tagged record before any real run.
- Item bank: six seed items. Must be expanded to a pool of at least 45 (1.5 times
  N at N equals 30) before a real run.

## Layout

```
self-context-calibration/
  README.md                  this file
  PRE_REGISTRATION.md        the dated, committed lock (create and tag before any real run)
  .gitignore
  harness/
    confab_harness_generalized.py
    confab_harness_faithful.py
    thinking_probe.py             (future)
  analysis/
    analyze.py                    pre-registered analysis (Wilson, Newcombe)
  items/
    items.py                      shared item pool (45 items)
  results/
    *.jsonl                       run outputs
  docs/
    claude_code_handoff_generalized_pilot.md
    claude_code_handoff_faithful_pilot.md
    faithful_harness_review_findings.md
```

## How to run

The harness self-documents. Read the docstring at the top of
`harness/confab_harness_generalized.py` for the full locked construct and the
agreed pre-registration before running anything.

To run the generalized pilot, follow `docs/claude_code_handoff_generalized_pilot.md`.
In short: install `requests`, set `ANTHROPIC_API_KEY` in the shell from the coffer
alias `itr-experiment`, reduce the model list to one model for the pilot, and run.
The harness writes `results/confab_results_generalized.jsonl` and
`results/confab_exclusions_generalized.jsonl`.

The harness requests no thinking. Temperature is omitted on all three models,
because claude-opus-4-7 deprecated it entirely (any value returns a 400); the
other two models are kept consistent with it.

## Pre-registration

The pre-registration is agreed in content but is not the lock until it is
committed to a dated, immutable record, a registry entry or at minimum a tagged
git commit, before the first real run. Locking it after seeing data defeats its
purpose. The primary endpoint, the outcome coding, the thresholds tied to the
resolution of the chosen N, and the stopping and exclusion rules all belong in
`PRE_REGISTRATION.md`.
