# Collection log

Operational notes on collection runs. Methodological changes live in
PRE_REGISTRATION_CONVERGENCE.md's Deviations section, not here.

2026-07-24. gemini-3.6-flash collected complete, 680 rows, single
echoed id, zero unparsed. gemini-3.1-pro-preview reached 251 of 680
rows and stopped at the provider's 250-requests-per-day cap (console
verified: 254 requests including 3 smoke probe calls). Collection
resumes across daily quota windows; the pre-registered echo tripwire
covers each boundary, enforced in the runner from commit fb445ad
onward. The split collection window is a quota artifact, not a
protocol change.

2026-07-25. Model discontinuity note: the faithful study's baseline
arm ran claude-opus-4-7; the convergence roster pins claude-opus-4-8.
The faithful and convergence opus cells are different models and are
never comparable, despite the shared item bank. Recorded here so the
shared-instrument design is not mistaken for shared data.

2026-07-25. Anthropic cells are collected fresh on both arms for all
three models. Faithful baseline rows are not imported: the opus id
differs, baseline row counts exceed the design (1,160 haiku, 920
sonnet, multiple runs Jul 4-21) and would require post-hoc selection,
and baseline rows predate the study's provenance fields (temperature
record, model id echo, reasoning verification).

2026-07-25. Exposure note: the collection runner prints per-model
aggregate answer-option distributions to stdout on run completion, a
behavior predating the 2026-07-24 no-peeking clarification. The Arm A
anthropic run's marginals were therefore displayed at completion and
seen. Materiality: bank-level marginals reveal neither per-item
modals, tie rates, pair agreements, nor the within-versus-cross
primary quantity, and the provisional analysis clarifications pending
review concern rules whose data-dependence is invisible in marginals.
The primary decision is unaffected. Mitigation for all remaining
collection runs: stdout is redirected to
convergence/results/collection_stdout.log (gitignored), keeping
stderr, including halt and refusal reports, on the console. A runner
change is deferred until collection completes to avoid mid-collection
code churn.

2026-07-28. Collection complete. Final totals: 12,240 rows, 18
model-arm cells at exactly 680 each, 5,440 Arm A and 6,800 Arm B.
gemini-3.1-pro-preview completed 2026-07-27 across three daily quota
windows (2026-07-24 through 2026-07-27) with a single echoed id on
every row; the preview-id exposure window is closed and the aliasing
risk is retired. File-wide integrity: no multi-echo model, zero
duplicate (model, arm, item_id, sample_index) keys, 60 unparsed rows
total (0.49 percent), no cell above the 0.10 sensitivity threshold.
Sensitivity 1 excludes no model. Analysis is gated on the analyzer
build (handoff pending with Claude Code) and resolution of the two
provisional clarifications under independent review.

2026-07-28. Sequencing breach: see the Deviations entry of this date
in PRE_REGISTRATION_CONVERGENCE.md. The analysis gate recorded above
was not cleared before the first real-data analysis run.
