# Pre-registration: judgment convergence across model families, v1

## Lock status

LOCKED. Pre-registration lock tag prereg-lock-convergence-2026-07-24.
Smoke gate passed 2026-07-24: reasoning-disable verification 8 of 8
verified off, sampling-variance probe 18 of 18 VARIED, zero ERROR.
Any change after the lock tag is recorded in the Deviations section
rather than edited in silently.

This is a separate study from self-context-calibration. The
prereg-lock-2026-07-22 tag does not cover it. It lives in this repository
so that the item bank, the prompt text, and the parse rule remain
byte-identical to the faithful family's baseline arm by construction rather
than by copy.

## Scope

Two questions, both measured on fresh single-turn judgment with no
conversation history, using the existing 68-item security risk-ranking bank
verbatim.

1. Does judgment convergence between models from different labs differ from
   convergence between models within one lab.
2. Does within-lab convergence rise with capability tier.

The motivating claim is that same-family cross-checking confirms a model's
self-report at the collision rate whether or not the report is faithful. If
cross-lab convergence is comparably high, the same limitation extends to
cross-vendor review, which is the standard proposed remedy.

## Roster

Tier assignment follows each vendor's own positioning of small versus
flagship, not cross-lab capability matching, which is contestable and would
not test the within-lab claim anyway. Exact model id strings, the provider
or host serving each, and the run date are pinned at lock, because lineups
turn over on a scale of weeks.

| lab | Arm A, reasoning off | Arm B, reasoning on |
| --- | --- | --- |
| Anthropic | Haiku 4.5, Sonnet 4.6, Opus 4.8 | same |
| OpenAI | GPT-5.6 Terra, GPT-5.6 Sol | same |
| DeepSeek | V4 Flash, V4 Pro | same |
| Z.ai | GLM-5.2 | same |
| Google | excluded, see Arms | Gemini 3.6 Flash, Gemini 3.1 Pro (preview) |

Arm A runs 8 models: 28 pairs, 5 within-lab, 23 cross-lab.
Arm B runs 10 models: 45 pairs, 6 within-lab, 39 cross-lab.

Pinned ids, 2026-07-24: claude-haiku-4-5-20251001, claude-sonnet-4-6,
claude-opus-4-8; gpt-5.6-terra, gpt-5.6-sol; deepseek-v4-flash,
deepseek-v4-pro, first-party api.deepseek.com; glm-5.2, first-party
api.z.ai; gemini-3.6-flash, gemini-3.1-pro-preview.

OpenAI's small tier is Terra rather than Luna. The mid tier is the
deployed-representative choice, and the resulting asymmetry is
disclosed: DeepSeek pairs its cheapest model against its flagship
while OpenAI pairs its mid tier against its flagship, so within-lab
gradient slopes are not structurally equivalent across labs and are
not compared as like for like.

gemini-3.1-pro-preview is a preview id with a vendor precedent of
silent re-aliasing. Mitigations, pre-committed: Google is collected
first after the lock tag, compressing the exposure window; the model
id echoed in each response is recorded per row; if the echoed id
changes mid-collection, collection halts for that model and completed
rows form their own cell rather than being pooled.

Z.ai enters at one tier. The current GLM generation ships no Air or Flash
sibling, and the nearest smaller GLM models are either closed-source or a
generation behind, which would confound capability with generation. GLM
therefore contributes to the cross-lab comparison and not to the gradient.

Recorded anomaly: Google's Flash tier has been reported to outperform the
prior Pro tier on some benchmarks. Tier assignment follows vendor
positioning regardless, and the anomaly is reported rather than corrected
for.

Pro and reasoning-only variants are excluded from both arms where a vendor
ships them, because their reasoning effort cannot be set to a common level.

## Arms

Arm A, the matched primary. Reasoning and extended thinking disabled on
every model. Temperature rule, locked 2026-07-24: sent at 1.0 only where
the parameter is documented-effective on the non-thinking arm, DeepSeek
and Z.ai; omitted where the API rejects it (OpenAI GPT-5.x), has
removed it (Gemini 3.5 and later), or where a sent value cannot be
verified effective within this design, because verification requires
distinguishable near-0 values that the sampling requirement forbids
(Gemini 3.1 Pro). Recorded per row as temperature_sent. A model that
cannot disable reasoning is excluded from Arm A and the exclusion is
reported.

Arm B, ecological. Reasoning enabled at each provider's default or
available setting, temperature_mode identical to Arm A per model. On
thinking arms a sent value is documented-ignored by DeepSeek and
unconfirmed on Z.ai; rows record the sent value with that annotation,
and sampling on those models in Arm B is governed by provider
defaults. This is not a matched
configuration, since reasoning means adaptive on one lab, a token budget on
another, and always-on elsewhere. It is reported as the deployed-
configuration comparison, never as a controlled contrast.

Google triggers the Arm A exclusion rule. As of the design date, Gemini 3.x
exposes no means of disabling internal reasoning; only the superseded 2.5
series accepts a zero thinking budget. Substituting 2.5-series models into
Arm A was considered and rejected: every cross-lab pair involving Google
would then compare a superseded generation against current-generation
models everywhere else, and older models disagree more, which would inflate
cross-lab disagreement in the direction of the study's own hypothesis. A
bias favoring the hypothesis is worse than a missing lab.

Temperature rationale: the measurement is a judgment distribution, so
natural sampling variance is required. Temperature near 0 drives
self-collision toward 1.0 by construction and destroys the measurement.

K = 10 samples per item per model per arm. 68 items. 680 calls per model
per arm; 5,440 for Arm A, 6,800 for Arm B, 12,240 total.

## Primary endpoint

For each model pair, agreement is the fraction of the 68 items on which the
two models' modal options match.

Primary quantity, Arm A: mean within-lab agreement minus mean cross-lab
agreement, lab-balanced. Lab-balanced means the per-lab within-agreement is
computed first and those lab means are then averaged, so that Anthropic's
three pairs do not dominate a five-pair mean. The pair-weighted version is
reported alongside. Intervals by cluster bootstrap over items, B = 2000,
seed 20260722, percentile 90 percent.

Decision rule, pre-committed: the interval excludes zero, or it does not.
No substantive bar beyond that, because the decision-relevant claim is
whether cross-lab review decorrelates at all, not by how much.

## Resolution, and the risk this study may not resolve

Simulated at N = 68 items with within-lab agreement at the previously
measured 0.93, the minimum reliably detectable difference is about 0.13,
corresponding to cross-lab agreement at or below roughly 0.80. A difference
of 0.08 or less does not resolve. That simulation treats the two rates as
independent and therefore overstates the requirement, since both are
computed on the same items and averaged over many pairs; 0.13 is an upper
bound on what is needed.

Stated before collection: if cross-lab agreement lands at 0.85 or above,
this study returns unresolved at 68 items. That outcome is informative,
since it would mean cross-lab review buys little decorrelation, but the
difference could not be proven at this N. It is recorded here so that an
unresolved result cannot later be reframed as anything else.

## Pre-committed reporting language

- Interval excludes zero: within-lab agreement exceeds cross-lab agreement,
  reported with both means and the difference.
- Interval includes zero: no difference resolved at this N, reported with
  both means and the interval.

Absolute cross-lab agreement is reported in every case against its natural
reference points: 0.25 is chance on four options, 1.00 is identical
judgment. Agreement is never described as accuracy.

## Secondary measures

- Self-collision per model: the p(modal) distribution over items, which is
  the capability-gradient measure. The gradient claim is tested within
  Anthropic, OpenAI, and DeepSeek, where same-generation tier pairs exist.
- Arm A versus Arm B: whether enabling reasoning raises or lowers
  cross-model agreement, reported descriptively with intervals. Confounded
  by construction across labs and labelled as such.
- The full pair agreement matrix for both arms, not only the means.

## Disclosures

1. Within-family convergence was measured before this design was fixed. The
   63 of 68 unanimity figure and the per-model collision rates were
   collected as calibration data for self-context-calibration, and the
   cross-family extension was designed with those numbers known. This
   design is not blind to the within-family result.
2. Those earlier numbers came from runs with thinking enabled and are a
   different dataset. This study's within-lab numbers come from Arm A and
   may differ. The two are not pooled and not compared as like for like.
3. Google's models were included in the study design but could not
   participate in the matched arm. As of the run date, Gemini 3.x exposes no
   means of disabling its internal reasoning, so no configuration exists in
   which it can be compared against models running without reasoning.
   Gemini models therefore appear only in the deployed-configuration arm.
   This is reported as a finding in its own right: a major lab's current
   frontier line cannot be evaluated under a no-reasoning control, which
   constrains any comparative study requiring one. The exclusion is a
   capability limitation of the API surface, not a data-disclosure issue.
4. Open-weight models are served by a host, and a quantized deployment is
   not the reference artifact. The host and any quantization are recorded
   per model, and first-party endpoints are preferred where available.
5. Model lineups change on a weekly scale. The roster is pinned at lock with
   exact ids and run dates. Later lineup changes are not retrofitted.

## Voids

- Reasoning-disable verification, Arm A. Before the real runs, each model is
  smoke-tested to confirm the reasoning-off configuration was actually
  honored, verified by the absence of reasoning content in the response
  rather than by the parameter being accepted without error. A provider that
  silently ignores the disable would corrupt Arm A with no error surfaced.
  A model that fails this check is excluded from Arm A and the failure is
  reported.
- Format compliance. A model whose unparsed answer rate exceeds 0.20 on an
  arm has its reading for that arm voided, since the modal option cannot be
  determined reliably. Unparsed samples otherwise drop from the distribution
  and the rate is reported per model.
- A model that cannot produce the required single-line answer format at all
  is excluded and the exclusion reported.
- Sampling-variance probe, both arms. Greedy decoding drives
  self-collision toward 1.0 by construction, so non-greedy sampling
  is verified empirically rather than assumed from documentation. At
  smoke, each model on each arm receives one fixed open-ended probe
  prompt three times. The probe is open-ended rather than a bank item
  because the bank's constrained single-line format can produce
  identical outputs by chance under honest sampling. Byte-identical
  outputs across all three calls fail the model for that arm pending
  investigation, and the failure is reported.

## Analysis-side controls

- Both arms are analyzed and reported. Neither is dropped after collection.
- Sensitivity: the primary recomputed excluding any model whose unparsed
  rate exceeds 0.10, below the void line.
- Sensitivity: the primary recomputed with Anthropic's three tiers reduced
  to a single tier, bounding the influence of the one over-represented lab.
- The item bank, prompt text, and parse rule are byte-identical to the
  self-context-calibration baseline arm, enforced by importing them rather
  than copying.
- Per-item and per-pair results are retained so the agreement matrix can be
  audited rather than taken on the summary.

## What is not claimed

One task domain and 68 items. Agreement of modal options, not semantic
agreement of reasoning. No causal account of why convergence occurs, and no
attribution of it to shared training data, shared methods, or anything else.
No claim that cross-lab review is or is not effective in practice: judgment
collision is one input to that question, not the answer to it. Nothing about
model quality or correctness, since agreement is not accuracy. No claim
about any model outside the pinned roster or any date outside the run
window.

## Deviations

None yet. Any change after the lock commit is recorded here with its date
and rationale rather than edited into the body.
