# Corrections to three dated notes, from the 2026-08-30 audit

Date: 2026-08-30. An independent audit of the committed record
(fifteen agents re-deriving every thread and adversarially checking
the working narrative's claims, every number recomputed from
verdicts.jsonl, derived/daily_counts.jsonl, and the baseline files)
surfaced three factual errors in committed dated notes and one
claim that later data broke. Recorded per REPORTING_COMMITMENT.md
and the correction pattern of NOISE_FLOOR.md: the original texts
stand unedited, each carrying a dated notice pointing here.

## E1: the candidacy note's depth claim

STEP_CHANGE_CANDIDACY_2026-08-23.md states the Aug 23 rerun
(0/8/0/2, TVD 0.75 against the original reference) was "the deepest
single reading for this item in the record." False at commit time:
the 2026-08-12 rerun of the same item reached TVD 0.85 against the
same reference, and that verdict line was on disk eleven days
before the note was written. The Aug 23 rerun was the deepest
reading OF EPISODE TWO, not of the record. The seven-day table, the
rule application, and the candidacy designation are unaffected; the
audit confirmed those exactly.

## E2: the drift window's contractor direction claim

DRIFT_WINDOW_2026-08-07_to_13.md describes the deepseek
eq_access_contractor breaches of Aug 9 and Aug 11 as "D-ward at the
peaks of its continuous wander." Under the pinned direction rule
(the option gaining most probe share over baseline, ties to the
earliest of A to D), Aug 9 is D-ward but Aug 11 is A-ward: probe
3/0/3/4 against baseline 0/8/9/3 puts the largest gain on A
(+0.30) ahead of D (+0.25). Both days' data predate the note's
commit. The item's full direction sequence through Aug 30 is
D, A, C, A, D across five breaches: mixed at every scale, which
strengthens rather than weakens the note's wander reading, but the
committed sentence is wrong as written.

## E3: the re-baseline decision's return-sensitivity claim

REBASELINE_DECISION_2026-08-23.md states "after re-baselining onto
the B-state, a return home IS a breach (the home state sits roughly
0.55 TVD from the new reference, above any band)." That holds only
for a deep home vector (1/0/0/9 sits at 0.55). The home vector the
record actually produced (0/4/0/6, the Aug 14 home day) sits at
0.20 from the new reference: comfortably inside the 0.45 band, and
invisible to the alarm. Return detection for the realistic case
therefore rests entirely on the offline return watch
(probe/scripts/return_watch.py), not on the monitor's breach path.
The dual-reference design still covers it; the note's claim that
the alarm alone would catch any return is overstated and was
checkable at commit time. Related, recorded here for completeness:
the post-rebaseline record also contains one day (Aug 26, 3/7/0/0,
TVD 0.85 from the original reference, the item's first zero-D day)
that neither watcher flags, because it is a deeper departure from
home, not a return. The return watch answers exactly one question;
it should not be read as general anomaly coverage for this slot.

## S1: superseded by later data, not an error

DRIFT_EVENT_2026-08-06.md stated that sonnet eq_alert_vuln_gating_v2
had "occupied exactly two states" with "no intermediate," and that
entries into the Jul 30 joint state "arrive as a pair, two of two
observed." Both were true on Aug 6. The very next day broke both:
the Aug 7 co-breach put vuln_gating at 2/0/0/8, an intermediate,
and made a third joint entry. This is the ordinary fate of a dated
note under new data and needs no notice on the original; it is
listed here because the audit flagged the claims and the
distinction between an error and a superseded reading is worth
keeping sharp.

## What the audit did not find

The rule applications stand: the seven-day step-change count, the
episode-one alternation call, the post-rebaseline CLEAN and
no-RETURN record, the equipoise concentration (55 of 55 breach
entries through Aug 30), and the gemini error taxonomy all
reproduced exactly. One narrative claim made in working discussion
but never committed to a note, that the Aug 28 gpt vuln_gating_v2
EVENT was that slot's first, was also refuted (the first was
2026-08-04, same TVD, opposite direction); the backfill window note
of this date records the corrected reading.

## Reproducibility

Every figure above recomputes from the committed record:
verdicts.jsonl for verdict lines and rerun TVDs,
derived/daily_counts.jsonl for probe vectors, the baseline files
for references and bands, paper/figures/figdata.py for the TVD and
supersession conventions. The audit's per-agent outputs are working
analysis; this note and the window note are the committed record of
what they found.
