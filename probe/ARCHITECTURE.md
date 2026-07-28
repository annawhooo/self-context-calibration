# Active probing for model-mediated controls

Priority date: 2026-07-28. Author: Anna Hix.

## The problem

A model-mediated control degrades silently. Vendors change served
models, quantization, serving configuration, and safety layers behind
a stable model id. Nothing in the response announces the change. A
control qualified against last quarter's behavior is not qualified
today, and no signal tells you when qualification expired.

Passive monitoring does not close this. Passive detection assumes the
environment exercises the detector. A gas leak fills the mine, so the
canary breathes it continuously. A silently swapped model produces no
ambient signal. Silence and health are indistinguishable.

Passive baselines carry a second problem. A baseline learned from live
traffic drifts with the thing it measures. The reference point moves.

## The architecture

Smoke and carbon monoxide detectors carry two verification paths. The
low-battery chirp is passive. The test button is active. The chirp
tells you the unit lost power. The button tells you the unit still
alarms. Neither substitutes for the other.

Apply both to an agent:
- Passive. Monitor what the agent does in deployment. Behavioral
  detection against expected patterns.
- Active. Probe the model with a fixed stimulus on a schedule. Compare
  the response distribution against a recorded baseline.

The two cover different failure surfaces. Passive watches the
installed system: prompts, tools, accumulated context, scaffolding.
Active verifies the sensor underneath it. A model can drift with the
scaffolding untouched. Scaffolding can break with the model untouched.

Receipts sit under both. Tamper-evident records make a probe result
and a behavioral alert independently verifiable after the fact.

## The instrument

I built a multi-provider elicitation and measurement harness. It is
stimulus-agnostic. Swapping the item bank changes what it measures and
nothing else.

Per response, the harness verifies rather than assumes:
- Reasoning state. Reasoning-off is confirmed in the response, not
  trusted from the request flag. Undetectable states report
  UNVERIFIABLE rather than success.
- Served model identity. The exact echoed model id is recorded per
  row. A change mid-collection halts collection for that model.
- Sampling. Non-greedy sampling is proven empirically by duplicate
  calls, not assumed from documentation.
- Credentials. A missing key fails closed, names itself, and issues
  zero requests.

Collection is durable and resumable. Analysis is deterministic:
identical inputs and seed produce byte-identical artifacts.

Who tests the tester. Each of the above distinguishes "the instrument
reports no change" from "the instrument is not working."

## Validation

I ran a pre-registered convergence study on this harness. Ten models,
five providers, a 68-item enterprise security judgment bank, K=10,
12,240 calls. Every cell landed at exactly 680 rows with a single
echoed model id and a 0.49 percent unparsed rate.

The study measured judgment convergence across labs. It also
demonstrated that the harness holds conditions fixed across five
vendors and produces reproducible distributions. That second result is
what makes the harness an instrument.

A three-week test-retest on two models found 63 and 64 of 68 modal
answers held, with one complete flip each. That is drift detection
running as a pilot.

## Three measurements, one rig

The baseline determines what the reading means.

1. Against the model's own history: drift detection. No ground truth
   required. The model's prior behavior is the reference.
2. Against planted ground truth: detection capability. Does the model
   still catch what it used to catch.
3. Against another model: complementarity. Which candidate reviewer
   decorrelates from the primary rather than confirming it.

Conformity to a population is not health. Agreement across models is
not evidence of correctness. A model that deviates from the population
may be the one getting it right. Deviation means different. Only
different.

## What a signal triggers

A probe result is not a diagnosis. It ends the assumption that
qualification still holds.

You cannot fix a vendor's model. The response actions are yours:
- Re-run acceptance tests for pipelines depending on that model.
- Gate or freeze automated decisions qualified against prior behavior.
- Fail over to a pinned alternative where one exists.
- Open a vendor ticket with dated evidence rather than a hunch.
- Record a control-effectiveness event. Revalidation is due.

The degraded reviewer is the worst case. A model that used to catch
mandate violations and now misses them looks exactly like a clean
environment.

## Relationship to AARM

This is not an AARM component. AARM specifies runtime mediation. Some
mediation decisions are model-mediated, and AARM offers no way to know
whether those elements still behave as qualified.

A model-mediated control validated once and never rechecked is a
standing trust assumption inside an architecture built to eliminate
standing trust assumptions. Active probing closes that. The
relationship is complementary assurance tooling, the same posture as
mcp-tap.

## What is unsolved

Probing a model is not probing an agent. The harness today issues
fixed items to a model behind an API. Probing an assembled agent
raises problems I have not solved:
- Side effects. A synthetic trajectory through real tools acts on real
  systems. Sandboxing changes what is being measured.
- Evaluation awareness. An agent that detects a probe may respond
  differently than it responds to production traffic.
- Bank aging. A declining detection rate has two explanations: the
  model degraded, or the bank went stale as violation patterns moved.
  Distinguishing them requires a frozen bank for longitudinal
  comparison and a rotating bank for current coverage.

## Next

Build the trajectory bank. Planted violations with known ground truth,
minimal pairs holding surface features constant, taxonomy labels kept
out of the stimulus, no roster model used for generation, piloting on
non-roster models only, bank frozen and hashed before the first roster
call.

The estimand is the number a control document needs. Not agreement.
Per-model miss rate on planted violations, and the joint miss rate
across vendors.
