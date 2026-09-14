# Step-change decision rule: gpt disclosure_timing, pinned 2026-09-14

Date: 2026-09-14. Status: DRAFT until merged to main; the merge is
the operator's adoption and is the pin. Validity condition: this
pin is valid only if merged before any post-2026-09-14 probe data
is read by operator or assistant; otherwise it is void and gets
redrafted with a later start date. Companions:
STEP_CHANGE_DECISION_RULES_2026-08-31.md (the form, the threshold
construction, and the operational practice this fulfills),
STEP_CHANGE_DECISION_RULE_2026-09-07.md (the same instrument for
the deepseek dlp thread, now suspended by the id change),
DESIGN_LIMITATIONS.md (Limitation 4, which attaches here), and
REPORTING_COMMITMENT.md.

## Registration status, stated plainly

Pinned the afternoon of 2026-09-14, after that day's verdicts
were read. The trigger was the 2026-09-13 held EVENT on this
thread, which is read data and counts toward nothing; so does
everything else through 2026-09-14. The count starts at zero at
the pin; the first countable observation is the 2026-09-15 probe.

## The thread

eq_disclosure_timing on gpt-5.6-terra. Baseline (2026-08-02,
n=20): unanimous A, 20 of 20, band p99 0.40. 41 observed days.
This is the record's cleanest-margin item: exact enumeration
gives P(a fair redraw keeps unique modal A) = 1.000 to three
places, so an away day here is signal, never modal flapping. The
record: eight breaches (Aug 3, 7, 9, 17, 21, 25, 27, Sep 13),
four held EVENTs (Aug 3, 25, 27, Sep 13), every excursion B-ward
including a full 0/10/0/0 flip on Aug 21 that reverted same-day.
Every away day in 41 days is a single-day spike; the longest
away dwell the item has been observed to return home from is one
day, and the thread sits at home today (9/1/0/0 on Sep 14). The
morphology to date is spike-hold: full-amplitude within-day
holds, no cross-day dwell, ever. This rule exists for the day
that changes.

One caveat attaches before counting starts, and it is the
sign-inversion caveat (DESIGN_LIMITATIONS.md, Limitation 4): a
20-of-20 unanimous baseline on a designed-equipoise item is the
shape the design notes flag as suspicious for a designed
coin-flip. The B-spikes may be excursions toward designed
behavior, and the frozen reference may itself be the anomalous
state. The rule counts dwell; it does not claim direction of
health.

## Definitions

Identical in form to the prior rules, anchored to this item:
HOME is TVD at or below 0.40 AND unique modal A; ties are not
home; missing days are neither and do not reset; arithmetic is
the monitor's as stored (FLOAT_POLICY_2026-08-30.md).

## The rule

A standing tripwire, evaluated in date order over observed days
from 2026-09-15 onward:

1. CANDIDACY: three consecutive observed AWAY days beginning
   2026-09-15 or later. Consequence: designate the item a
   step-change candidate, write a dated note, and open the
   re-baseline discussion for THIS ITEM ONLY as a dated operator
   decision per REBASELINE_DECISION_2026-08-23.md. The frozen
   baseline stays in force until that decision is recorded.
2. A HOME day resets the count to zero and terminates nothing.
3. The rule stands until a candidacy fires or a dated note
   retires it; the freeze write-up reports whatever state exists
   on 2026-09-26.

Threshold derivation, fixed before any countable data exists:
three strictly exceeds the longest observed returned-from dwell
(one day) plus the standard two days of clearance. On an item
whose null away probability is zero to three places, three
consecutive away days is not reachable by sampling noise at all;
the threshold is small because the item's own history makes even
a two-day dwell unprecedented. Freeze arithmetic is comfortable:
a qualifying run must begin by 2026-09-24.

## Code adopted with this note

probe/scripts/step_change_watch.py gains this thread's RULES
entry (threshold 3, count_from 2026-09-15). Counting semantics
unchanged, pinned by the existing test.
