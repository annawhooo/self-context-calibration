# Post-submission decisions: effective dates, retry, deepseek watch

Date: 2026-10-02. Status: DRAFT until merged to main; the merge is the
operator's adoption and is the pin. Validity condition: section 4's
comparison rule is valid only if this note is merged before any watch data
is read by operator or assistant; otherwise that section is void and gets
redrafted. Companions: FLOAT_POLICY_2026-08-30.md (layer 3, whose date this
note sets), RECALIBRATION_POLICY_DRAFT_2026-08-16.md (adopted in the same
commit, effective date set there), paper/FREEZE_2026-09-26.md (the 56-day
figures cited below), probe/scripts/deepseek_watch.py and
probe/tests/test_deepseek_watch.py (the side channel of section 4),
DESIGN_LIMITATIONS.md, and REPORTING_COMMITMENT.md.

## Registration status, stated plainly

Drafted on 2026-10-02, the day after the INTERCEPT submission and the day
before the operator leaves for eight days. The 56-day record through
2026-09-26 has been read in full; verdict lines for 09-27 to 09-29 are on
main and have been seen as tallies only; lines after 09-29 have not been
pushed or read. Every rule below acts only on probe days on or after its
effective date, so no data already read counts toward any of them. No watch
data exists at drafting.

## 1. Effective date for both pending policies: 2026-10-13

FLOAT_POLICY_2026-08-30.md layer 3 (exact integer comparison) and the
recalibration policy both said "no earlier than 2026-10-02, the operator
picks the exact date." The operator picks 2026-10-13, the first weekday
after her return. The instrument runs unattended and unchanged from
2026-10-03 through 2026-10-12; no commit touches probe/monitor/ on main in
that window. Order on the effective date: the exact-arithmetic commit lands
first, then the recompute under the recalibration policy, so recalibrated
decisive bands are stored with their lattice values from the start. Each
lands as its own dated commit with its sanity gates, and a gate failure
stops it with nothing landed.

## 2. Recalibration band kept at 0.25

The operator adopts the recalibration policy as drafted, decisive band 0.25.
That value was set on 2026-08-16 one lattice step above the twelve-day
decisive maximum of 0.20. At the freeze the decisive maximum is 0.30, on 2
of 11,057 slot-days (paper/FREEZE_2026-09-26.md, Section 5,
between_day_variance.py), so 0.25 would have fired twice in 56 days under
either arithmetic. The value is kept rather than moved above the longer
record's maximum: moving it now would tune the band to data read after the
pin. The pre-registered rollback (more than three decisive entries in the
first fourteen days) stands unchanged. By the policy's basis_days rule,
slots with fewer than 40 basis days keep their old bands; the halted
deepseek arm, at 39 probe days, keeps all of its bands.

## 3. Second-hour retry, ERROR models only, from 2026-10-13

The paper's item (g) says a monitor that matters should retry at a second
scheduled hour. Pinned design: a second scheduled task, three hours after
the probe task, runs the probe only for roster models whose newest verdict
line for that date is ERROR. It never reruns a model with any other verdict
that day. A retry appends its own verdict line; the ERROR line stays in the
log, and for every analysis the later line for a model-date supersedes the
earlier one. The monitor flag, the analysis-side reader change, and the
second schtasks entry land together on or after 2026-10-13, after every file
in probe/tests/ passes. Until then a 503 day is an availability gap,
recorded as such.

## 4. Deepseek: the arm stays halted; a side channel watches

The monitor's deepseek arm stays halted by its own tripwire and keeps making
its one detecting call a day; that is unchanged. Re-qualifying the renamed
identity as a new arm needs two operator-run baseline runs and is not
decided here. To observe the renamed identity without touching the study, a
side channel runs daily:

1. What it sends: the monitor's own request path (the collect_row the
   monitor imports), the monitor's roster entry for deepseek-v4-flash, arm
   A, K=10, the 68-item bank. It requests the pinned id a customer would
   have pinned.
2. Where it lives: a separate clone on the operator's desktop, checked out
   on branch deepseek-watch. The script refuses to run on any other branch,
   writes only under probe/deepseek_watch/, and pushes only that branch. Raw
   rows stay gitignored; one counts-only line per day is committed.
3. What it never touches: verdicts.jsonl, probe/monitor/derived/, any
   baseline, band, null, alarm, or paper number.

Pinned comparison, descriptive only. For each complete watch day (all 680
calls returned), score every item's watch distribution against the
old arm's frozen 2026-08-02 baseline
(probe/monitor/baselines/deepseek-v4-flash.json, read only), in exact
arithmetic, against that item's own stored band; count the items strictly
above band. Report the mean daily count over the first fourteen complete
watch days beside the old arm's mean daily count of exact-arithmetic
above-band slot-days over its 39 probe days, both from one committed script
written before the fourteenth watch day. Also report, per item, the watch
modal answer against the baseline modal answer. Interim reads of the daily
counts are permitted and do not change this rule. The outcome decides
nothing in the study; it informs whether the operator drafts a separate
dated note to re-qualify the renamed identity as a new arm.

## What this note does not do

It changes no verdict, band, baseline, K, seed, or alarm-set member today,
and it adds nothing to the verdict log. It does not adopt the retry or the
exact comparison before 2026-10-13. It does not re-qualify or retire the
deepseek arm.
