Handoff: convergence analysis implementation

Context. Implements the analysis pre-registered in
PRE_REGISTRATION_CONVERGENCE.md under prereg-lock-convergence-2026-07-24,
including the Deviations entries through 2026-07-25 (test-retest
supplement, modal-tie rule, three-singleton sensitivity). The
pre-registration is the spec; this handoff restates it operationally.
Where this document and the pre-registration disagree, the
pre-registration wins and the disagreement is a reportable bug. Nothing
outside convergence/ may change. The faithful study's analyzer and its
v1.5 reconciliation are out of scope.

Input. convergence/results/convergence_rows.jsonl, extended row schema.
Rows partition by (model, model_id_exact, arm): a model with more than
one distinct echo id forms separate cells and the analyzer must fail
loudly, naming the ids, rather than pool or choose; resolution is
human, per the pre-registered halt rule. Unparsed rows drop from the
per-item distribution and count toward the per-model unparsed rate.
The analyzer runs correctly on partial data for integrity reporting,
but primary computation refuses to run unless every Arm A cell holds
exactly 680 rows, stating what is missing.

Integrity report, runs on any state: per model per arm, row count,
unparsed count and rate, distinct echo ids, tie count over items,
duplicate (item_id, sample_index) detection.

Primary computation, Arm A. Per model per item: answer distribution
over parsed rows; modal option if unique, tied-flag otherwise. Per
pair: agreement is the fraction of 68 items with matching unique
modal options; a tied-flag on either side is a non-match. Within-lab
mean lab-balanced (per-lab mean first, then across labs) and
pair-weighted, both reported. Primary quantity: lab-balanced within
minus cross. Cluster bootstrap over items, B = 2000, seed 20260722,
percentile 90 percent interval: resample the 68 items with
replacement, keep per-model-per-item modals fixed, recompute the full
quantity per replicate. Decision output is exactly one of the two
pre-committed reporting sentences, with means, difference, and
interval; absolute cross-lab agreement is always reported against
0.25 chance and 1.00 identity, and never described as accuracy.

Voids and sensitivities. Unparsed rate over 0.20 on an arm voids that
model's reading for the arm. Sensitivity 1: primary recomputed
excluding any model with unparsed rate over 0.10. Sensitivity 2:
primary recomputed three times with each Anthropic model as sole lab
representative, range reported. Sensitivity 3: primary recomputed
under set-intersection tie matching per the Deviations clarification.
Sensitivities are reported alongside the primary, never substituted.

Secondary. Per-model p(modal) distribution over items, both arms; the
tier gradient within Anthropic, OpenAI, and DeepSeek only; Arm A
versus Arm B agreement compared descriptively with bootstrap
intervals and the confounded-by-construction label; the full pair
agreement matrix for both arms, per-item and per-pair records
retained to file.

Test-retest supplement, Deviations 2026-07-25. For
claude-haiku-4-5-20251001 and claude-sonnet-4-6 only: fresh Arm A
per-item distributions compared against
results/confab_baseline_faithful.jsonl rows for the same model id,
reporting per-item modal match rate and per-item total variation
distance, summarized. Output to its own file, labelled corroborative,
never entering the primary. Opus is excluded and the exclusion stated
in the output.

Output. Deterministic artifacts under convergence/analysis/: a
machine-readable results json and a human-readable markdown report,
plus per-item and per-pair csvs. Identical inputs and seed produce
byte-identical outputs; a repeated run overwrites rather than
appends. Directory gitignored; a frozen result is committed
deliberately with git add -f.

Tests. No-network fixture tests in the existing style: hand-built row
fixtures with known modals, ties, and agreement values; lab-balancing
against a hand-computed example; bootstrap determinism, same seed
same interval twice; the 680-row gate; multi-echo fail-loud; both
void triggers; all three sensitivities; test-retest on a
baseline-schema fixture; both pre-committed sentences selected by
constructed inputs. Existing 12 test files pass unmodified.

Deviations. Exhaustive per the standing contract: departures and
additions both, flag semantics included.
