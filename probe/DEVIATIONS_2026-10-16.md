# Deviations from the 2026-10-02 pins: three items did not land

Date: 2026-10-16. Status: DRAFT until merged to main; the merge adopts
the reporting. This note decides nothing. Companions:
DECISIONS_2026-10-02.md (the pins, sections 1, 3 and 4),
FLOAT_POLICY_2026-08-30.md (layer 3),
RECALIBRATION_POLICY_DRAFT_2026-08-16.md (whose Adoption section says
any departure "is a deviation and gets its own dated note"),
OUTAGE_GAP_2026-10-10_to_11.md, and REPORTING_COMMITMENT.md.

## The entries

D1. Exact arithmetic and the recalibration recompute (section 1).
Both were due on 2026-10-13, exact arithmetic first, and neither
commit landed.
No commit on any branch of origin touches probe/monitor/monitor.py,
probe/monitor/preflight.py, probe/monitor/baselines/, probe/scripts/,
or probe/tests/ since 2026-10-02. The monitor ran on 2026-10-13,
2026-10-14 and 2026-10-15 with float comparison and the 2026-08-02
bands.

D2. The second-hour retry (section 3). Due on or after 2026-10-13.
monitor.py has no retry flag, and the verdict log has one line per
model-date from 2026-10-13 through 2026-10-15. gemini-3.6-flash
returned ERROR (http 503) on all three of those days, and no retry
line exists for any of the three days.

D3. The deepseek watch comparison script (section 4). The pin requires
"one committed script written before the fourteenth watch day." The
deepseek-watch branch holds 14 complete watch days (680 calls each),
2026-10-02 through 2026-10-16 with no line for 2026-10-10. The
fourteenth, 2026-10-16, was committed at 10:12 EDT on 2026-10-16. No
comparison script exists on any branch of origin.

## What each one touched

D1 produced one observable effect. On 2026-10-13 claude-haiku-4-5
breached eq_alert_spend_anomaly_v2 at an observed TVD stored as
0.45000000000000007 against a p99 of 0.45. Under exact comparison the
observed value is 9/20 and the band is 9/20, and equal values are not
a breach. The 2026-10-13 breach is the float-only equality breach
that layer 3 was written to remove. FLOAT_POLICY_2026-08-30.md names
a repeat before the effective date as expected behavior; this repeat
fell on the effective date itself, because the conversion had not
landed. The breach was the day's only breach for that model, and its
rerun scored 0.2 against baseline, so the line reads TRANSIENT. The
line stands as recorded: the log is append-only, and neither policy
rescores past days. The recompute would have lowered decisive bands
to 0.25, so a decisive slot between 0.25 and its stored band on these
days would have breached after the recompute. This note does not
compute whether any slot fell in that range, because the computation
reads the three days against a band that has no effective date yet.

D2 means three gemini days are availability gaps rather than retried
days. The rest of the record is unaffected: the retry would have run
only for ERROR lines.

D3 leaves the section 4 comparison without the script its timing
condition requires. The assistant writing this note counted watch
lines and their call totals only and did not read any watch answer
distribution. Whether the operator has read the watch distributions
is not recorded here.

## Open decisions, for the operator

The decisions below are listed, not taken.

1. A new effective date for D1, and whether the recalibration
   rollback window ("the first fourteen days after the effective
   date") counts from that new date.
2. A landing date for D2.
3. For D3: whether section 4's comparison is void and redrafted, as
   the note's own validity language does for other conditions, or
   carried forward with this deviation named.

## Reproducibility

D1: git log origin/<branch> --since=2026-10-02 over the five paths
above, for every branch of origin, returns no commits. D2: the
verdict log lines for 2026-10-13 through 2026-10-15, five per date.
D3: probe/deepseek_watch/daily_counts.jsonl on origin/deepseek-watch,
14 lines; commit 74f3150 is the 2026-10-16 line.
