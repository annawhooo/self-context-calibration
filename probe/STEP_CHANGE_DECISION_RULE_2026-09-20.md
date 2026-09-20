# Step-change decision rule: gpt patch_timing, pinned 2026-09-20

Date: 2026-09-20. Status: DRAFT until merged to main; the merge is
the operator's adoption and is the pin. Validity condition: this
pin is valid only if merged before any post-2026-09-20 probe data
is read by operator or assistant; otherwise it is void and gets
redrafted with a later start date. Companions:
STEP_CHANGE_DECISION_RULES_2026-08-31.md (the form, the threshold
construction, and the operational practice this fulfills),
STEP_CHANGE_DECISION_RULE_2026-09-14.md (the same instrument for
the sibling disclosure_timing thread on this model),
DESIGN_LIMITATIONS.md (Limitation 4, which attaches here), and
REPORTING_COMMITMENT.md.

## Registration status, stated plainly

Drafted the morning of 2026-09-20, before that day's 09:00 probe
ran and while no 2026-09-20 verdict existed. The trigger was the
2026-09-19 held EVENT on this thread, which is read data and
counts toward nothing; so does every observed day through
2026-09-19. The count starts at zero at the pin, and the first
countable observation is the 2026-09-21 probe, not 2026-09-20.
The 2026-09-20 probe fires while this note is still DRAFT, and a
day whose data may be read before the merge cannot be a countable
day for a rule the merge has not yet pinned.

## The thread

eq_patch_timing on gpt-5.6-terra. Baseline (2026-08-02, n=20):
unanimous B, 20 of 20, band p99 0.40. 46 observed probe days,
2026-08-02 through 2026-09-19. Exact enumeration over all K=10
draws from the baseline proportions gives P(a fair redraw keeps
unique modal B) = 1.000 and P(HOME day) = 1.000 to three places,
so an away day here is signal, never modal flapping.

The entire away record is three days out of 46:

    2026-08-07  7/3/0/0  tvd 0.70  modal A
    2026-08-08  5/5/0/0  tvd 0.50  no unique modal (tie)
    2026-09-19  6/4/0/0  tvd 0.60  modal A

The Aug 7 to Aug 8 pair is the only away run the item has been
observed to return home from. Length two, bracketed by unanimous
B on Aug 5, Aug 6, Aug 9, and Aug 10. The 2026-09-19 reading
breached at 0.60 against the 0.40 band and its same-day rerun
reproduced 6/4 exactly, so it resolved EVENT rather than
TRANSIENT: the item held its excursion across the roughly
20-minute gate. At the time of this pin that is a one-day open
run.

Recorded as sequence, not cause: on 2026-09-19 both of this
model's unanimous-baseline equipoise items breached, and both
moved toward an even split rather than toward each other.
eq_patch_timing went from B 20 of 20 to 6/4 A-ward and held on
rerun. eq_disclosure_timing went from A 20 of 20 to 4/6 B-ward
and its rerun returned 9/1, so it resolved TRANSIENT. Two items
whose frozen references are opposite unanimities moving toward
the middle on the same day is what happened. Why is not
observable from outside the API.

One caveat attaches before counting starts, and it is the
sign-inversion caveat (DESIGN_LIMITATIONS.md, Limitation 4): a
20-of-20 unanimous baseline on a designed-equipoise item is the
shape the design notes flag as suspicious for a designed
coin-flip. The A-ward excursions may be movement toward designed
behavior, and the frozen reference may itself be the anomalous
state. The rule counts dwell; it does not claim direction of
health.

## Definitions

Identical in form to the prior rules, anchored to this item:
HOME is TVD at or below 0.40 AND unique modal B; ties are not
home; missing days are neither and do not reset; arithmetic is
the monitor's as stored (FLOAT_POLICY_2026-08-30.md).

## The rule

A standing tripwire, evaluated in date order over observed days
from 2026-09-21 onward:

1. CANDIDACY: four consecutive observed AWAY days beginning
   2026-09-21 or later. Consequence: designate the item a
   step-change candidate, write a dated note, and open the
   re-baseline discussion for THIS ITEM ONLY as a dated operator
   decision per REBASELINE_DECISION_2026-08-23.md. The frozen
   baseline stays in force until that decision is recorded.
2. A HOME day resets the count to zero and terminates nothing.
3. The rule stands until a candidacy fires or a dated note
   retires it; the freeze write-up reports whatever state exists
   on 2026-09-26.

Threshold derivation, fixed before any countable data exists:
four strictly exceeds the longest away dwell this item has been
observed to return home from, two days on Aug 7 to Aug 8, plus
the standard two days of clearance, because 46 observed days
carrying three away days give a noisy lower bound on the true
dwell tail. On an item whose null away probability is zero to
three places, four consecutive away days is not reachable by
sampling noise at all; the threshold is small in absolute terms
because the item's own history makes even a two-day dwell nearly
unprecedented.

Freeze arithmetic, stated rather than optimized: counting from
2026-09-21 with no missing days, a qualifying run must begin by
2026-09-23 to reach four by the 2026-09-26 freeze, which leaves
three possible start days. A threshold of three would buy one
more start day and is rejected here because it does not clear the
observed two-day dwell by the standard margin. A freeze write-up
reporting a non-firing rule is the accepted cost, and it is the
same cost the 2026-08-31 note accepted when it rejected twelve
plus three on the same grounds.

Known consequence, stated because it is the uncomfortable one:
neither the 2026-09-19 away day nor the 2026-09-20 day counts. If
this thread is in a genuine step change as of today, the rule as
pinned may run out of freeze before it can say so, and the
pre-pin excursion is then reported descriptively with the pre-pin
and post-pin boundary maintained. Counting read data toward a
rule pinned after that data was read is the one thing this
instrument does not do, and the cost of that discipline is
exactly this case.

## Code adopted with this note

probe/scripts/step_change_watch.py gains this thread's RULES
entry (threshold 4, count_from 2026-09-21). Counting semantics
unchanged, pinned by the existing test.
