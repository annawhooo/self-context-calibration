# Re-baseline decision: haiku spend_anomaly_v2, dual reference

Notice, 2026-08-30: the return-sensitivity claim below ("a return
home IS a breach") holds only for a deep home vector; the observed
home vector sits inside the new band, so return detection rests on
the offline watch. See CORRECTIONS_2026-08-30.md, E3. Original
text preserved unedited.

Notice, 2026-09-02: the pre-registered return criterion fired
(RETURN day 2026-09-02, post-rebaseline day 10). Its pre-committed
consequence, revision to slow alternation and re-examination of
the re-baseline, is executed in
SLOW_ALTERNATION_REVISION_2026-09-02.md. Original text preserved
unedited.

Date: 2026-08-23. Status: DRAFT until merged to main; the merge is
the operator's adoption of this decision, and the decision takes
effect only when probe/scripts/rebaseline_item.py has been run and
its baseline-file diff committed. Companion to
STEP_CHANGE_CANDIDACY_2026-08-23.md (which opened this decision),
STEP_CHANGE_DECISION_RULE_2026-08-16.md, and
DRIFT_EVENT_2026-08-06.md (whose decision 1 this note revisits for
one item). Recorded per REPORTING_COMMITMENT.md.

## The decision

Re-baseline eq_alert_spend_anomaly_v2 on claude-haiku-4-5-20251001
onto its current B-state, AND preserve the frozen Aug 2 reference
inside the same item record for daily offline tracking. Not either
alternative from the candidacy note; both. The alarm follows the
new reference; the history and the return question follow the old
one. This item only. No other slot, no bands elsewhere, no K, no
seeds elsewhere, no verdict, and no monitor code changes.

Why both is sound rather than a hedge: after re-baselining onto the
B-state, a return home IS a breach (the home state sits roughly
0.55 TVD from the new reference, above any band), so the monitor
does not lose return sensitivity; the Aug 6 blindness concern
applied to discarding the original reference, and this decision
discards nothing. What changes is what "quiet" means for this slot:
quiet now means the B-state is holding, and repeat EVENT lines
against a reference the item has not matched in nine days stop
consuming the alarm channel.

## Mechanism

probe/scripts/rebaseline_item.py, operator-run, roughly 20 calls:

1. Two same-day K=10 runs of this one item through the monitor's
   own imported machinery (run_bank, echo tripwire armed with the
   baseline file's recorded model id), the original qualification
   semantics scoped to one item. No third-run logic: a failed
   run-pair gate aborts and writes nothing.
2. Gates: run-pair TVD within run1's smoothed p99 band;
   the new pooled reference outside the OLD reference's p99 band
   (a re-baseline onto an indistinct state voids the premise);
   no same-day superseded entry (double-run protection).
3. On success the baseline file is rewritten: the Aug 2 reference
   moves intact into the item's "superseded" list with validity
   dates; the new n=20 reference, with bands from new seed
   suffixes ("rebl:<date>", "rebl-band:<date>"), becomes the
   monitor-visible baseline_counts and band. monitor.py reads only
   those two keys and is untouched.

Validity convention, pinned: the superseded reference governs
THROUGH the run date; the new reference governs from the day
after. Run the script after the day's probe. The analysis tooling
(paper/figures/figdata.baseline_for) implements the same
convention so no historical day is ever re-scored against a
reference that was not in force when it ran.

## The return criterion, pre-registered before any new-regime data

A RETURN day is a probe day after the re-baseline with BOTH:

1. TVD against the superseded Aug 2 reference at or below that
   reference's p99 band (0.45), and
2. modal answer D, the superseded reference's modal, with a tie
   counting as not-returned.

This mirrors the step-change rule's HOME definition against the
old reference. probe/scripts/return_watch.py is the mechanical
check, computed from the committed daily counts, run ad hoc or
after each daily push. Consequences, pinned now:

- A RETURN day on or before 2026-09-26 (the INTERCEPT freeze):
  the step-change classification is revised to slow alternation
  with week-scale dwell, in a new dated note, and the re-baseline
  is then re-examined as a dated operator decision (the dual
  reference makes reversal cheap: the superseded entry is intact).
- No RETURN day through the freeze: the step change stands with a
  stated bound ("no return observed in N post-transition days"),
  never as proof of permanence.
- Either way the outcome is reported per REPORTING_COMMITMENT.md.

## On which state is "home"

The candidacy note asked whether the item returns home. This note
retires that framing for this item. The record shows two long-dwell
states: D-modal (unbroken Aug 2 to Aug 8) and B-modal (unbroken
observed Aug 15 to Aug 23). Neither dwell looks like a visit. What
distinguishes them is design intent: this is a designed-equipoise
item, the B-state splits 6/4 the way the item was authored to
split, and the near-unanimous 17/20 D reference is the shape the
design notes already flag as suspicious for a designed coin-flip
(DESIGN_LIMITATIONS.md, Limitation 4; the sign-inversion caveat).
The equipoise prior therefore favors the B-state as designed
behavior, and Aug 2 may have frozen the anomalous state as the
reference. That is a prior, not a finding: the instrument measures
change, not direction of health, and this note claims only the
transition.

## Interaction with the paper

The INTERCEPT data plan anticipated exactly this: the instrument
stays unchanged through the freeze UNLESS the committed haiku rule
triggers a re-baseline, and a triggered one is a finding to
document. Draft section 3.1.1 reports the candidacy, this decision,
and the return-watch outcome as of the freeze. The dual-reference
mechanism itself becomes operational-guidance material (section 5):
re-baselining a drifted slot without losing the original reference
is the pattern a monitoring team needs, and this is its first use.

## What this does not do

It does not re-baseline any other slot, including the sonnet pair
and the other alternators (their home visits keep their frozen
references correct). It does not change the alarm-set membership,
the verdict grammar, or any past verdict. It does not claim the
B-state is permanent, healthy, or attributable to any cause. It
does not touch the recalibration policy draft, which remains
dormant until after submission.
