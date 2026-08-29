# Return watch: haiku spend_anomaly_v2, five days, no return

Date: 2026-08-29. Companion to REBASELINE_DECISION_2026-08-23.md
(the pinned criterion, applied here unmodified) and
STEP_CHANGE_CANDIDACY_2026-08-23.md (episode two, whose away run
these days extend). Recorded per REPORTING_COMMITMENT.md. This note
is the mechanical application of a criterion pinned before any of
the classified days existed; no judgment sits between the
definitions and the outcome. Written 2026-08-29 with that day's
probe still in flight: today is not classified here and lands in a
later read.

## Outcome

No RETURN day. Five post-rebaseline probe days, 2026-08-24 through
2026-08-28, every one away under the pinned criterion. The
step-change classification stands unrevised, with the interim bound
stated the way the decision note requires: no return observed in
five post-transition probe days.

## The classified days

Superseded reference (Aug 2, n=20): 2 A / 1 B / 17 D, D-modal,
band p99 = 0.45, valid through 2026-08-23. A RETURN day needs both
legs: TVD against that reference at or below 0.45, AND modal D,
with a tie counting as not-returned. The rows below are
probe/scripts/return_watch.py over the committed record; I
spot-checked the two at-band rows by hand.

| date  | probe A/B/C/D | TVD vs superseded | modal   | class |
|-------|---------------|-------------------|---------|-------|
| 08-24 | 0/5/0/5       | 0.45              | tie B/D | away  |
| 08-25 | 0/6/0/4       | 0.55              | B       | away  |
| 08-26 | 3/7/0/0       | 0.85              | B       | away  |
| 08-27 | 1/5/0/4       | 0.45              | B       | away  |
| 08-28 | 0/6/0/4       | 0.55              | B       | away  |

## The two at-band days, stated plainly

Aug 24 and Aug 27 sat exactly at the superseded band. Both passed
the TVD leg (0.45 is at the band, not above it) and both failed the
modal leg: Aug 24 is a 5/5 B/D tie, which the criterion counts as
not-returned; Aug 27 is B-modal with D at 4. These are not returns.
They are the item's closest approaches to the old reference since
the Aug 14 home visit, and Aug 24 is its first observed day since
Aug 14 that is not B-modal. The criterion was pinned before these
days existed; I am recording the near misses, not reinterpreting
the rule around them. If a later read lands a true RETURN, these
two days are its early context.

## The far side of the same window

Aug 26 (3/7/0/0) ties the deepest reading for this item in the
record: TVD 0.85 against the superseded reference, matching the
Aug 12 rerun (1/9 A/B). It is the deepest probe-phase reading
outright, and the first scheduled probe with D at zero. (The
candidacy note called its Aug 23 rerun, at 0.75, the record's
deepest single reading; the Aug 12 rerun at 0.85 predates it. The
slip sits in that note's aside, not in its classified days, and it
stays uncorrected there per the records convention.) The same
Aug 26 vector sits at TVD 0.40 against the new B-state reference
(1 A / 11 B / 8 D, band 0.45): within band. The week holds both
extremes at once, the item's farthest reading from the old
reference and five CLEAN verdicts against the new one.

## Under the new reference

All five days verdicted CLEAN for this model, no breach line since
the re-baseline. That is the dual-reference design doing what it
was adopted for: the alarm channel is quiet while the B-state
holds, and the return question stays measured against the preserved
Aug 2 reference. This note is that measurement.

## What remains open

The watch runs through the INTERCEPT freeze. Twenty-eight scheduled
probe days remain in the window (2026-08-30 through 2026-09-26),
plus today's, unclassified at this writing. The pinned consequences
are unchanged: a RETURN day on or before 2026-09-26 revises the
classification to slow alternation in a new dated note and reopens
the re-baseline as a dated operator decision; no RETURN leaves the
step change standing at the freeze with the day-count bound, never
as proof of permanence.

Stated plainly, on cadence: this is the first recorded read, five
probe days after the decision note pinned "run ad hoc or after each
daily push." The classification is computed from committed counts,
so every day above classifies identically whenever the script runs;
the gap cost nothing this time, and the read is now current through
the committed record.

## Reproducibility

- Mechanism: probe/scripts/return_watch.py, run 2026-08-29; reads
  only probe/monitor/baselines/*.json and
  probe/monitor/derived/daily_counts.jsonl, writes nothing.
- Verdict lines: probe/monitor/verdicts.jsonl, dates 2026-08-24
  through 2026-08-28 for the haiku model (five CLEAN; commits
  a4e6432 through 8abb1c8).
- Deepest-reading and vs-new-reference figures: return_watch.tvd
  applied to the committed counts for this slot, both phases, all
  dates, against both references in the baseline file.
- Criterion: REBASELINE_DECISION_2026-08-23.md, applied unmodified.
