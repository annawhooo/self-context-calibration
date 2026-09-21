# Correction to the 2026-09-20 rule note

Date: 2026-09-21. Continues the numbering and the pattern of
CORRECTIONS_2026-08-30.md and CORRECTIONS_2026-09-06.md: the
original text stands unedited and carries a dated notice pointing
here. Recorded per REPORTING_COMMITMENT.md. Companion to
PIN_COLLISION_2026-09-21.md, which records the verification pass
that surfaced this entry.

## E6: the equipoise quantifier in the 2026-09-20 rule note

STEP_CHANGE_DECISION_RULE_2026-09-20.md states: "on 2026-09-19
both of this model's unanimous-baseline equipoise items breached,
and both moved toward an even split rather than toward each
other." The quantifier is false, and it was checkable in the committed
baseline file at commit time. Under Ruling 3 of
RULINGS_2026-08-30.md (the equipoise class is the eq_ prefix),
gpt-5.6-terra's committed baseline carries 23 eq_ items, 17 of
them with unanimous 20-of-20 baselines, not two. What is true,
and what the sentence was written to say: exactly two items
breached on 2026-09-19 (eq_patch_timing, held EVENT;
eq_disclosure_timing, TRANSIENT), and both belong to the
unanimous-baseline equipoise class. Two of seventeen breached,
not both of two.

The rule is unaffected: the threshold, count_from, definitions,
away-day table, threshold derivation, and freeze arithmetic all
reproduce exactly from the committed record, and the pin's
validity does not rest on this sentence. The source of the error,
recorded for process honesty: the sentence was drafted by the
assistant as an appositive (both items that breached, which are
unanimous-baseline equipoise items) and committed with the
class-count reading unchecked; the 2026-09-21 verification pass
(PIN_COLLISION_2026-09-21.md) surfaced it against the baseline
file.

Recorded alongside, not as errors, three imprecisions in the
same note that a reader should not carry forward:

- "the roughly 20-minute gate" is inherited from
  DESIGN_LIMITATIONS.md; the 2026-09-19 verdict line's own run
  ids put the probe-to-rerun run-start gap at 9.0 minutes.
- "rejected twelve plus three" misquotes the 2026-08-31 note,
  which set twelve and rejected thirteen and beyond ("Plus three
  and beyond") on freeze arithmetic.
- "At the time of this pin that is a one-day open run" was true
  at draft time only. The merge is the pin, and by the merge
  (2026-09-21) the run had closed: the 2026-09-20 probe read
  0/10/0/0, HOME.

## Reproducibility

The class counts recompute from
probe/monitor/baselines/gpt-5.6-terra.json: 23 items carry the
eq_ prefix, 17 of them a single-option baseline at n=20. The
breach list is the 2026-09-19 gpt-5.6-terra line of
probe/monitor/verdicts.jsonl (breached: eq_patch_timing EVENT,
eq_disclosure_timing TRANSIENT). The 9.0-minute gap is the same
line's run_ids pair (13:21:27Z to 13:30:26Z).
