# S3: the record's first verdict-class float flip, at the rerun gate

Date: 2026-09-14. Status: DRAFT until merged; the merge adopts the
reporting. Recorded in the spirit of CORRECTIONS_2026-09-06.md S2,
so the freeze census table surprises nobody. Companions:
FLOAT_POLICY_2026-08-30.md (which governs; the verdict log
stands) and REPORTING_COMMITMENT.md.

## The entry

2026-09-13, gpt-5.6-terra / eq_alert_edr_response. The probe
(0/10/0/0, ten B against the 9 B / 11 D baseline) breached
genuinely: exact TVD 11/20 against exact band 9/20, no edge
anywhere. The float edge sits at the rerun gate. The same-day
rerun came back 0/9/0/1, exact TVD 9/20 against the baseline,
exactly at the band. Exact arithmetic: the rerun matches the
baseline under at-or-below, so the item reads TRANSIENT. The
float path compared 0.45000000000000007 against the stored
0.45000000000000001 and read not-matching, so the log says
EVENT. Both values are float dust on the same rational, 9/20.

## Why this one is new

The 2026-08-30 census found six float-edge BREACH entries and
zero verdict flips among surviving entries: every prior edge sat
at the breach comparison, where at-band equality decides fired
or not-fired. This edge sits at the rerun disambiguation, where
it decides EVENT against TRANSIENT, a verdict-class flip. It is
the first of its kind in the record. The day verdict for
2026-09-13 is unaffected: eq_disclosure_timing held its EVENT
cleanly (rerun 0.60 against band 0.40), so the gpt day reads
EVENT under either semantics.

## What happens with it

Per FLOAT_POLICY_2026-08-30.md: the verdict log stands as
recorded; the freeze census reruns over the full record and
reports both semantics, and this entry will appear in its table
as the record's first rerun-gate flip; the instrument converts
to integer arithmetic after submission on the dated schedule.
The paper's honest-failure item (f) carried the census results
as untagged prose ("zero verdict flips"); those values are now
FREEZE-tagged in the same commit as this note so the drafting
claim cannot outlive the record that falsified it.

## Reproducibility

Probe and rerun vectors: derived/daily_counts.jsonl, 2026-09-13,
gpt-5.6-terra, eq_alert_edr_response. Verdict line:
verdicts.jsonl, same date. Baseline and band:
baselines/gpt-5.6-terra.json. Exact comparison: the census
arithmetic in probe/scripts/float_census.py; the fractions
recompute in two lines from the counts above.
