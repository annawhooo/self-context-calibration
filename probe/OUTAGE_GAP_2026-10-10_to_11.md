# Two days with no probe rows: 2026-10-10 and 2026-10-11

Date: 2026-10-13. Status: DRAFT until merged; the merge adopts the
reporting. Recorded under REPORTING_COMMITMENT.md so the record's
calendar gap is documented where the analysis reads the record.
Companions: STEP_CHANGE_DECISION_RULES_2026-08-31.md and
STEP_CHANGE_DECISION_RULE_2026-09-20.md (each defines how missing days
count) and DECISIONS_2026-10-02.md (the second-hour retry, scheduled to
start on or after 2026-10-13).

## The entry

verdicts.jsonl holds no line for any of the five roster models on
2026-10-10 or 2026-10-11, and derived/daily_counts.jsonl holds no row
for either date. The day before has five verdict lines and 253 count
rows; the day after has five verdict lines and 274 count rows. The
span from 2026-08-02 to 2026-10-12 is 72 calendar days; the record
holds 70 of those days, 350 model-days, and the gap removes 10
model-days (2 days times 5 models).

## Cause

Per the operator, a power outage from Hurricane Isaias stopped the
scheduled task on 2026-10-10 and 2026-10-11. The repository carries no
log, status page, or run record for 2026-10-10 or 2026-10-11, so the
cause is the operator's report and was not verified in the writing of
this note.

## What happens with the gap

Nothing in the record changes. The gap is not backfilled: a probe run
after the fact would sample a different day under the date label of
another, and verdicts.jsonl and daily_counts.jsonl are append-only.
Under the two pins named above, a missing day is not HOME, is not
AWAY, and resets no count, so the gap advances no tripwire and clears
no tripwire. The second-hour retry in DECISIONS_2026-10-02.md starts on
or after 2026-10-13; the retry covers ERROR verdicts only, and a day
with no run at all produces no ERROR line to retry.

## Reproducibility

Count the verdict lines and the count rows for each date from
2026-10-09 through 2026-10-12 in probe/monitor/verdicts.jsonl and
probe/monitor/derived/daily_counts.jsonl; the dates 2026-10-10 and
2026-10-11 return zero lines and zero rows. The span and model-day
figures come from the same two files: 350 verdict lines, 70 distinct
dates, 5 models.
