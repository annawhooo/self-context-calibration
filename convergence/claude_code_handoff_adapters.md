# Code handoff: convergence collection runner and provider adapters

Context: convergence/PRE_REGISTRATION_CONVERGENCE.md (DRAFT, commit
d8f52f2) defines a cross-family judgment convergence study. This handoff
builds its collection path. The study is separate from
self-context-calibration and must not alter it: the faithful harness, the
analyzer, the item bank, and their tests are read-only for this work.

## Scope

A new collection module under convergence/ that runs the existing 68-item
bank against models from five providers in two arms, writing rows in a
schema compatible with the existing baseline analysis.

## Import, do not copy

The pre-registration requires the item bank, prompt text, and parse rule to
be byte-identical to the faithful baseline arm by import rather than by
copy. Import ITEMS, baseline_prompt, and parse_baseline_answer from the
existing modules rather than reproducing them. A test asserts that the
imported prompt for a fixed item is byte-identical to a pinned expected
string, so a future edit to the faithful harness cannot silently change
this study's stimulus without a test failing.

## Provider adapters

Three client shapes cover five providers:

1. Anthropic native. Reuse the existing call_model. Reasoning off means
   omitting the thinking parameter; reasoning on means passing it.
2. OpenAI-compatible. One client parameterized by base_url and key, serving
   OpenAI, DeepSeek, and Z.ai. Reasoning control differs per provider and
   is pinned in a per-model config table, never inferred from the base_url.
3. Google native. Arm B only, since Gemini 3.x cannot disable reasoning.

Reasoning-off mechanism per provider, pinned:

- Anthropic: omit the thinking parameter.
- OpenAI: reasoning_effort "none". Reject any model that does not accept
  it rather than falling back to a low effort setting.
- DeepSeek: the documented thinking toggle for the V4 line.
- Z.ai: enable_thinking false. Do NOT use the thinking {type: disabled}
  form; it has been reported to be silently ignored while enable_thinking
  works correctly.
- Google: not applicable, Arm B only.

Temperature: send 1.0 where the API accepts it, omit where it rejects it,
and record per row which was done. Never send 0 or accept a provider
default near 0. The measurement is a judgment distribution and depends on
natural sampling variance; near-zero temperature drives self-collision
toward 1.0 by construction and destroys the study.

## Row schema

Extend the baseline row with: provider, model_id_exact, host (for
open-weight models, including any quantization string the host reports),
arm ("A" or "B"), reasoning_requested ("off" or "on"), reasoning_detected
(true, false, or null when the provider exposes no way to tell),
temperature_sent (float or null). Keep run_id, phase, model, item_id,
sample_index, parsed, raw_text, and ts exactly as the baseline arm writes
them.

## Reasoning-disable verification

The pre-registration makes this a void condition, so it is a required
feature rather than a convenience. For each Arm A model, a verification
mode issues a small number of calls and reports whether reasoning content
appeared despite being disabled. Detection is per adapter because the
field differs: thinking blocks for Anthropic, reasoning items or reasoning
token counts for OpenAI, reasoning_content for the OpenAI-compatible
Chinese providers.

If a provider exposes no way to detect whether reasoning ran, report that
rather than assuming success. An undetectable state cannot satisfy a void
condition that requires positive verification, so the correct outcome is a
reported failure that may cost a model its place in Arm A, not a silent
pass.

## Credentials

Keys live in the coffer vault as the durable record (aliases
openai-convergence, deepseek-convergence, zai-convergence,
google-convergence) and are supplied to runs through environment
variables. The runner reads only the environment and does not call coffer;
the vault is the record, not the runtime source. Do not add a coffer
integration.

Pinned variable names, matching each provider SDK's own convention so
official clients pick them up without extra wiring:

  ANTHROPIC_API_KEY, OPENAI_API_KEY, DEEPSEEK_API_KEY, ZAI_API_KEY,
  GOOGLE_API_KEY

Read at start, never logged, never written to any row or log line. Fail
closed with a message naming the missing variable and issue no request. Do
not add any credential-loading convenience that persists secrets to disk.

## Reliability

Reuse the existing retry semantics (bounded retries, linear backoff,
per-row durable append) rather than reimplementing them. New providers
return different rate-limit and error shapes, so map each provider's
retryable statuses explicitly and record the mapping in a comment. A run
that aborts must leave every completed row on disk, because the recovery
convention depends on topping up only the missing slots. The faithful
campaign lost an Opus leg to a mid-run credit exhaustion and recovered
cleanly for exactly this reason.

## Tests (TDD, no network)

1. Byte-identity: the imported prompt for a pinned item matches a pinned
   expected string exactly.
2. Adapter request shaping: for each provider and each arm, the constructed
   request body carries the pinned reasoning setting and the correct
   temperature handling. Assert against recorded fixtures, not live calls.
3. Response parsing: each adapter extracts answer text and reasoning
   presence correctly from recorded example payloads.
4. Credential handling: a missing environment variable fails closed with a
   named error and issues no request.
5. The existing suite stays green and no file outside convergence/ is
   modified.

## Hard constraints

- No change to the faithful harness, the analyzer, the item bank, or their
  tests. Nothing outside convergence/ is modified.
- No live API calls in tests.
- Do not pin OpenAI or Google model ids in code. They are configuration and
  get pinned on lock day, because those lineups have already moved once
  since the study was scoped.
- No em dashes.

## Report back

The adapter structure chosen; the per-provider reasoning-off mechanism and
the detection field for each; which providers expose no reasoning-content
detection; test results per assertion; confirmation that nothing outside
convergence/ changed.
