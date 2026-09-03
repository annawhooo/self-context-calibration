# Revision: haiku spend_anomaly_v2 is a slow alternator

Date: 2026-09-02. Status: DRAFT until merged to main; the merge is
the operator's adoption of both decisions in this note, the
classification revision and the reference decision. Companions:
REBASELINE_DECISION_2026-08-23.md (whose pre-registered return
criterion and consequence execute here),
STEP_CHANGE_CANDIDACY_2026-08-23.md,
STEP_CHANGE_DECISION_RULE_2026-08-16.md,
STEP_CHANGE_RESOLUTION_2026-08-16.md (episode one, closed as
alternation), CORRECTIONS_2026-08-30.md (E3), and
STEP_CHANGE_DECISION_RULES_2026-08-31.md. Recorded per
REPORTING_COMMITMENT.md.

## The trigger, mechanically

The 2026-09-02 probe for eq_alert_spend_anomaly_v2 on
claude-haiku-4-5-20251001 came in 1/4/0/5: TVD 0.35 against the
superseded Aug 2 reference (2 A / 1 B / 17 D, band 0.45), inside
that band, with unique modal D, the superseded reference's modal.
That satisfies both clauses of the return criterion pre-registered
in REBASELINE_DECISION_2026-08-23.md before any new-regime data
existed. probe/scripts/return_watch.py flags the day RETURN, the
first in ten post-rebaseline days. The consequence was pinned with
the criterion: a RETURN day on or before the 2026-09-26 freeze
revises the step-change classification to slow alternation in a
new dated note, and the re-baseline is re-examined as a dated
operator decision. This note is both.

Texture, on the record before anyone discovers it as a surprise:
this is a boundary day. One fewer D (a 5/5 tie) would not have
been a return. The same probe is CLEAN against the new B-state
reference at TVD 0.15, closer to the new reference than to the
old one; the two references sit 0.50 apart with a 0.45 band each,
so their bands overlap and this day lands in the overlap. Under
the pinned criterion none of that matters: the criterion asks for
modal D inside the old band and got it. The criterion is executed
as written.

## The revised classification

The step-change designation of 2026-08-23 is revised: the
transition was not one-way. Episode two closes as ALTERNATION with
long dwell, the same verdict as episode one at a longer time
scale. The full dwell record against the Aug 2 reference (per-day
vectors in probe/monitor/derived/daily_counts.jsonl; post-
rebaseline days in the return_watch output):

- D-rest, Aug 2 to Aug 8: seven consecutive observed home days
  (including two shallow 1/4/0/5 days, Aug 5 and 6).
- Single-day B excursion Aug 9; home Aug 10; B run Aug 11 to 13.
- D visit Aug 14, which closed episode one as alternation.
- B-rest, Aug 15 to Sep 1: sixteen consecutive observed away
  days, eighteen calendar days with the Aug 19 to 20 credential
  outage inside, spanning the Aug 23 re-baseline.
- D visit Sep 2, vector 1/4/0/5, identical to the Aug 5 and
  Aug 6 home-dwell days.

The item is a two-state alternator whose rest state switched from
D to B and whose dwells lengthened: seven observed days in the
D-rest, sixteen in the B-rest, with single-day visits between.
"Slow alternation with week-scale dwell" is the pre-committed
term; the measured dwells run week-to-fortnight scale.

What is NOT revised: the Aug 23 candidacy fired correctly under a
rule pinned before its deciding data, and its record stands. The
2026-08-16 rule chose seven days to clear the longest alternator
gap then known, three days; this item then produced a sixteen-day
gap. A candidacy is a designation that opens a decision, not a
classification, and this episode is now the demonstration of why
the rule was built that way.

## The reference decision: keep the new reference

Pre-commitment: the re-baseline is re-examined as a dated operator
decision. Re-examined here. The decision adopted with this merge
is to KEEP the B-state reference as the monitor-visible baseline,
with the superseded Aug 2 reference intact, through the freeze.

- The item rests in B and visits D. Quiet in the alarm channel
  should mean the rest state is holding. Reversal would restore a
  daily EVENT line whenever the item rests, the exact noise the
  Aug 23 decision removed, and buys nothing an alternator will
  not undo on its next flip.
- The triggering day itself sits closer to the new reference
  (0.15) than to the old (0.35). Reversing the reference on the
  evidence of a day the current reference explains better would
  invert the evidence.
- Sensitivity is unchanged from what is already on record
  (CORRECTIONS_2026-08-30.md, E3): shallow D visits inside the
  new band stay silent in the alarm and visible in the offline
  watch; deep D days of the 0/1/0/9 class sit at TVD 0.50 from
  the new reference and breach it.
- Reversal stays cheap and available: the superseded entry is
  intact by design. No reversal script exists; if a sustained
  D re-dwell ever argues for one, that reversal is its own dated
  decision with its own script and gates, not an edit.

## What the watch does now

probe/scripts/return_watch.py continues unchanged, daily. The
return criterion existed to trigger this revision and has done so;
it is not re-armed, and additional RETURN days carry no further
classification consequence. The watch keeps recording RETURN and
away days and the FARTHEST-YET extremes as the descriptive record
for the freeze report, where the open question is only whether
Sep 2 was a visit (the alternator pattern predicts it) or the
start of a D re-dwell.

## What this teaches the instrument

- The dual-reference pattern did its job in its first use: rule
  fired Aug 23, re-baseline with preserved reference the same
  day, return criterion pre-registered the same day, detection on
  post-rebaseline day 10, pre-registered revision the same day as
  detection. The operational-guidance claim in the paper's
  section 5 now has its complete worked example.
- It validates the 2026-08-31 gpt thresholds' construction, which
  clear each item's own longest returned-from dwell rather than
  borrowing another item's. And it bounds what any fired candidacy
  can claim: a threshold crossing before the freeze can still be
  slow alternation on a dwell longer than the observation window,
  so the tested response to candidacy is dual reference plus a
  pinned return criterion, never a bare re-baseline.

## Interaction with the paper

Section 3.1.1 reports the full arc as of the freeze: candidacy,
dual-reference re-baseline, a sixteen-observed-day away dwell,
return on post-rebaseline day 10, and this pre-registered
revision. Sections 3.3 and 3.5 gain a fully resolved specimen:
slow alternation joins the fast alternators and the wanderer as
an observed morphology with a closed loop from rule to revision.
The draft edits are separate work and follow the counting rule.

## What this does not do

No verdict, band, baseline file, K, seed, alarm-set, or monitor
code changes. The baseline file is untouched by this note: the
new reference stays monitor-visible exactly as the Aug 23 diff
left it. This note does not claim the B-state is healthy,
permanent, or attributable to any cause; it does not reopen
episode one; and it does not touch the 2026-08-31 gpt rules,
whose counters run independently.
