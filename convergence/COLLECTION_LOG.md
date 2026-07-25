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
