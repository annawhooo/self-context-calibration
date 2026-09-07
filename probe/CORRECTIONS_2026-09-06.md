# Correction to the 2026-08-31 rules note, and two float-edge entries

Date: 2026-09-06. Continues the numbering and the pattern of
CORRECTIONS_2026-08-30.md: the original text stands unedited and
carries a dated notice pointing here. Recorded per
REPORTING_COMMITMENT.md.

## E4: the contractor characterization in the 2026-08-31 rules note

STEP_CHANGE_DECISION_RULES_2026-08-31.md states, of deepseek
eq_access_contractor: "its six breaches have all reverted
same-day, and it has never held an EVENT." Both clauses are false,
and both were checkable in verdicts.jsonl at commit time. The
item's breach history as committed: EVENT 2026-08-09 (probe
2/2/1/5, rerun 1/0/2/7, held), EVENT 2026-08-11 (probe 3/0/3/4,
rerun 1/2/1/6, held), UNSTABLE 2026-08-15 (rerun matched neither
side), TRANSIENT 2026-08-17, 2026-08-21, 2026-08-31. Two of the
six held; a third matched neither. The source of the error,
recorded for process honesty: the tooling in that day's read
failed to surface item-level verdicts, and the sentence was
written from working memory of the late-August window instead of
from the log. The audit note this rules note itself lists as a
companion (CORRECTIONS_2026-08-30.md, E2) already carried the
Aug 9 and Aug 11 breaches.

What the correction does not change, stated with the corrected
record in front of it: the held states did not persist (Aug 10
read 1/3/3/3, a four-way near-tie; Aug 12 read 1/3/2/4,
sub-band), the breach direction sequence is mixed at every scale
(E2: D, A, C, A, D through Aug 30), and the baseline modal margin
remains one count with null modal survival 0.485. There is still
no stable candidate state to name for this slot. The no-pin
decision for contractor stands, now on that rationale rather than
the false one, and pinning remains the operator's call at any
time, count from the pin.

## E5: the working reads' novelty framing for the deepseek flares

Never committed to a note, corrected here because it shaped two
daily reports: the Sep 4 and Sep 5 reads described deepseek's
recent flares as landing on novel, non-repeating slots. That was
an artifact of starting the window at Aug 31. In the full record
eq_alert_dlp_email_v2 is a repeat thread: six breaches (Aug 17,
19, 20, 27, Sep 2, Sep 6), three held EVENTs (Aug 19, 20, Sep 6),
every excursion D-ward against a 17-of-20 C-modal baseline, and
exact vector recurrence (probe 0/0/3/7 on both Aug 19 and Aug 27;
1/0/3/6 four times across probes and reruns). The thread is
discrete and directional, deepseek's own two-state oscillator,
not a wander and not noise. Under the operational practice
adopted 2026-08-31 it is flagged as a watch item in the Sep 6
report, with a rule offer the same day.

## S2: two new float-edge breach entries, recorded, not errors

Per FLOAT_POLICY_2026-08-30.md the verdict log stands and the
freeze census reports both semantics; these two entries are
recorded here so the freeze table surprises nobody. On 2026-09-05,
deepseek eq_alert_fraud_scoring_v2 logged observed TVD
0.45000000000000007 against stored band 0.45000000000000001;
exact arithmetic puts both at 9/20, an at-band equality, no
breach under strict-greater. On 2026-09-06, deepseek
eq_alert_edr_response logged observed 0.5 against stored band
0.49999999999999994; exact arithmetic puts both at 1/2, the same
class. Both days' remaining entries survive exact arithmetic
unchanged, including the Sep 6 dlp_email_v2 EVENT at exact 7/10.

## Reproducibility

Every figure above recomputes from the committed record:
verdicts.jsonl for verdict lines and rerun TVDs,
derived/daily_counts.jsonl for probe vectors, the baseline files
for references and bands, and the exact comparisons per the
census arithmetic in probe/scripts/float_census.py.
