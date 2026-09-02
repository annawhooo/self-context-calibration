# Step-change candidacy: haiku spend_anomaly_v2, episode two

Notice, 2026-08-30: the depth claim below ("the deepest single
reading for this item in the record") is wrong; the Aug 12 rerun
was deeper. See CORRECTIONS_2026-08-30.md, E1. Original text
preserved unedited.

Notice, 2026-09-02: the step-change candidate designation below is
revised. The item returned to the superseded reference on
2026-09-02 after a sixteen-observed-day away dwell, and episode
two is closed as slow alternation. See
SLOW_ALTERNATION_REVISION_2026-09-02.md. Original text preserved
unedited.

Date: 2026-08-23. Companion to STEP_CHANGE_DECISION_RULE_2026-08-16.md
(the rule applied here), STEP_CHANGE_RESOLUTION_2026-08-16.md (which
closed episode one as alternation and declared any later sustained
away run a new episode under the same definitions), and
DRIFT_WINDOW_2026-08-07_to_13.md. Recorded per
REPORTING_COMMITMENT.md. This note is the mechanical application of
a rule pinned before the deciding data existed; no judgment sits
between the definitions and the outcome. The one decision the rule
opens is explicitly NOT taken here.

## Outcome

Clause 1 of the committed rule fires today: the item accumulated
seven consecutive observed AWAY days. eq_alert_spend_anomaly_v2 on
claude-haiku-4-5-20251001 is designated a STEP CHANGE CANDIDATE,
and the re-baseline discussion for this item only is now open as a
dated operator decision. Per the rule, re-baselining is never
automatic: the frozen Aug 2 baseline stays in force until that
decision is recorded in its own dated commit.

## The classified days

Baseline (2026-08-02, n=20): 2 A / 1 B / 17 D, D-modal, band
p99 = 0.45. Episode one ended with the Aug 14 home visit
(STEP_CHANGE_RESOLUTION_2026-08-16.md); the days below are episode
two. AWAY is any day that is not (no breach AND D-modal); ERROR
days count as neither home nor away and extend the window without
resetting it, exactly as the rule pinned.

| date  | probe A/B/C/D | TVD  | modal | verdict | class |
|-------|---------------|------|-------|---------|-------|
| 08-15 | 0/6/0/4       | 0.55 | B     | EVENT   | AWAY 1 |
| 08-16 | 0/6/0/4       | 0.55 | B     | EVENT   | AWAY 2 |
| 08-17 | 0/6/0/4       | 0.55 | B     | TRANSIENT | AWAY 3 |
| 08-18 | 0/7/0/3       | 0.65 | B     | TRANSIENT | AWAY 4 |
| 08-19 | no probe (http 401) | | |  ERROR  | neither |
| 08-20 | no probe (http 401) | | |  ERROR  | neither |
| 08-21 | 0/6/0/4       | 0.55 | B     | EVENT   | AWAY 5 |
| 08-22 | 0/7/0/3       | 0.65 | B     | EVENT   | AWAY 6 |
| 08-23 | 0/6/0/4       | 0.55 | B     | EVENT   | AWAY 7 |

Every away day is B-modal and every breach moves toward B; the
thread remains unidirectional at every observation.

## What the away state looks like now

It is discrete and it is deepening. The probe vector 0/6/0/4 has
now occurred seven times identically (Aug 12, 13, 15, 16, 17, 21,
23), with depth excursions to 0/7/0/3 (Aug 18, 22) and, in today's
same-day rerun, 0/8/0/2 at TVD 0.75 against baseline, the deepest
single reading for this item in the record. The reruns confirm the
away state within the day on every EVENT. The item's last home
visit was Aug 14 (0/4/0/6, D-modal); its only other home day since
Aug 8 was Aug 10. The dwell asymmetry of the episode-one
classification has fully inverted: this item now rests away and no
longer visits home.

## Stated plainly, for evidential weight

The seven-day count crossed its threshold with two unobserved days
(the Aug 19-20 credential outage) inside the window. The rule
pinned that treatment on 2026-08-16, before any of the deciding
days existed, so applying it is not a post-hoc choice; but a reader
should know the seven observed days span nine calendar days.

## The open decision, and what bears on it

To re-baseline this item is to declare the B-state the new
reference. Two committed considerations pull in opposite
directions, and the decision belongs to the operator, in a dated
commit, not to this note:

- Monitor-side (DRIFT_EVENT_2026-08-06.md, decision 1): the frozen
  reference is what makes a return visible. Re-baselining onto an
  attractor blinds the monitor to the flapping if the item is
  still, on a longer dwell, an alternator.
- Paper-side (docs/claude_code_handoff_intercept_paper.md, data
  plan): the instrument stays unchanged through the 2026-09-26
  freeze unless this rule triggers a re-baseline; if it does, that
  is a finding to document, not a disruption to suppress. Either
  choice is compatible with the paper; silence about the choice is
  not.

Until the decision is recorded, nothing changes: same baseline,
same bands, same K, same seeds, same alarm set.

## Reproducibility

Verdict lines: probe/monitor/verdicts.jsonl, dates 2026-08-15
through 2026-08-23 for claude-haiku-4-5-20251001 (committed; the
Aug 23 line landed via the first automated record push). Per-day
vectors: probe/monitor/derived/daily_counts.jsonl. Baseline and
band: probe/monitor/baselines/claude-haiku-4-5-20251001.json. The
rule and its definitions: STEP_CHANGE_DECISION_RULE_2026-08-16.md,
applied unmodified.
