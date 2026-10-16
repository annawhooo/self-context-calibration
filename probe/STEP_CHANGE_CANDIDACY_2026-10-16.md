# Step-change candidacy: gpt disclosure_timing

Date: 2026-10-16. Status: DRAFT until merged to main; the merge adopts
the reporting. Companions: STEP_CHANGE_DECISION_RULE_2026-09-14.md
(the rule applied here, unmodified), REBASELINE_DECISION_2026-08-23.md
(the form of the decision this note opens),
STEP_CHANGE_CANDIDACY_2026-08-23.md (the precedent for this note),
OUTAGE_GAP_2026-10-10_to_11.md (the two missing days inside the run),
DESIGN_LIMITATIONS.md (Limitation 4), and REPORTING_COMMITMENT.md.
This note is the mechanical application of a rule pinned before the
deciding data existed. The one decision the rule opens is NOT taken
here.

## Outcome

Clause 1 of the 2026-09-14 rule fired on 2026-10-13, the third
consecutive observed AWAY day counted from 2026-09-15.
eq_disclosure_timing on gpt-5.6-terra is designated a STEP CHANGE
CANDIDATE, and the re-baseline discussion for this item only is open
as a dated operator decision. The frozen 2026-08-02 baseline stays in
force until that decision is recorded in its own dated commit.

## Registration status, stated plainly

The rule fired on 2026-10-13 and this note is written on 2026-10-16,
three days late. The rule sets no deadline for the note, and the
firing day is fixed by the record, not by when the note is written.
The days 2026-10-14 and 2026-10-15 were read before this note and are
reported below as context; the two later days are not part of the
firing.

## The classified days

Baseline (2026-08-02, n=20): 20 A, band p99 0.40. HOME is TVD at or
below 0.40 AND unique modal A; a tie is not home; a missing day is
neither home nor away and does not reset the count. Classes and the
CANDIDACY line are printed by probe/scripts/step_change_watch.py as
committed; the rerun columns come from the same day's verdict line
and derived/daily_counts.jsonl.

| date  | probe A/B | TVD  | modal | rerun A/B | verdict | class   |
|-------|-----------|------|-------|-----------|---------|---------|
| 10-08 | 10/0      | 0.00 | A     | none      | CLEAN   | HOME    |
| 10-09 | 0/10      | 1.00 | B     | 2/8       | EVENT   | AWAY 1  |
| 10-10 | no run (outage)  |      |       |           | none    | neither |
| 10-11 | no run (outage)  |      |       |           | none    | neither |
| 10-12 | 4/6       | 0.60 | B     | 4/6       | EVENT   | AWAY 2  |
| 10-13 | 5/5       | 0.50 | tie   | 4/6       | EVENT   | AWAY 3  |
| 10-14 | 2/8       | 0.80 | B     | 1/9       | EVENT   | AWAY 4  |
| 10-15 | 1/9       | 0.90 | B     | 5/5       | EVENT   | AWAY 5  |

Every away day moves toward B, and every rerun confirmed the breach
within the day (held EVENT on all five days). model_id_echo is
gpt-5.6-terra on every line, so the provider reported no change of
identity.

## What is new about this run

Through 2026-09-14 the rule note records every away day on this item
as a single-day spike: the longest away dwell the item had returned
home from was one day. From 2026-09-15 through 2026-10-08 the watch
output shows the same pattern, with single AWAY days on 09-19, 09-28,
and 09-30. The current run is the first multi-day away dwell in the
record. The three observed days that fired the rule span five
calendar days, because the 2026-10-10 and 2026-10-11 outage sits
inside the run; the rule pinned that treatment of missing days on
2026-09-14, before any of these days existed.

## Stated plainly, for evidential weight

Limitation 4 attaches. A unanimous 20-of-20 baseline on an item
designed for equipoise is the shape the design notes flag as
suspicious. The B-ward run may be a move toward the designed
coin-flip, and the frozen reference may itself be the anomalous
state. The rule counts dwell and makes no claim about which state is
healthy.

## The open decision

To re-baseline is to declare the current state the new reference.
The same two considerations named in STEP_CHANGE_CANDIDACY_2026-08-23.md
pull in opposite directions here. Keeping the frozen reference keeps a
return home visible; the 2026-08 haiku episode closed as slow
alternation after a sixteen-observed-day dwell
(SLOW_ALTERNATION_REVISION_2026-09-02.md). Re-baselining records the
change as a finding. The choice belongs to the operator, in a dated
commit. Until the decision is recorded, nothing changes: same baseline, same
band, same K, same seeds, same alarm set.

## Reproducibility

Run python probe/scripts/step_change_watch.py and read the
gpt-5.6-terra / eq_disclosure_timing block; the 2026-10-13 row carries
"CANDIDACY (threshold reached)". The verdict lines are in
probe/monitor/verdicts.jsonl for gpt-5.6-terra, 2026-10-08 through
2026-10-15, and the probe and rerun vectors are in
probe/monitor/derived/daily_counts.jsonl under the phases
monitor_probe and monitor_rerun. The baseline and band are in
probe/monitor/baselines/gpt-5.6-terra.json.
