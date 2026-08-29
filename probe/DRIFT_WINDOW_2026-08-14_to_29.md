# Drift window: 2026-08-14 to 2026-08-29

Date: 2026-08-29, covering the sixteen probe days since the last
window note (DRIFT_WINDOW_2026-08-07_to_13.md) and closing on
today's committed verdicts. The haiku episode inside this window
has its own dated notes (STEP_CHANGE_CANDIDACY_2026-08-23.md,
REBASELINE_DECISION_2026-08-23.md, RETURN_WATCH_2026-08-29.md) and
is pointed to, not retold. Recorded per REPORTING_COMMITMENT.md.
Written from the committed verdict record and daily counts; every
figure recomputed by script.

## The window in numbers

Eighty model-days: 47 CLEAN, 13 TRANSIENT, 10 EVENT, 1 UNSTABLE,
9 ERROR. Twenty-six breach entries, every one a designed-equipoise
item; the all-time record now stands at 55 of 55 equipoise entries.
By model: deepseek 9, gpt 8, haiku 7, gemini 2, sonnet 0. The
smoothed-truth null (probe/scripts/expected_false_breaches.py,
per-model rates times each model's observed days) predicts 23.5
chance entries for the 71 observed model-days (exact rates; the
script's two-decimal printout sums to 23.4), 0.8 under the
empirical truth. The count excess is mild, and the count is not the
signal. The structure is: all twelve entries after Aug 20 landed on
already-breached slots, so the distinct-slot count has been frozen
at 17 since Aug 20 while entries grew from 43 to 55. The movement
keeps piling onto the same named threads and refuses to spread.
The widest days are Aug 17 and Aug 21, four entries each across
three models. The window closes on an all-CLEAN roster day, the
third in the record and the first since Aug 5.

## The gpt cluster, Aug 25 to 28

The window's centerpiece. Four entries in four consecutive days on
one model, three EVENTs among them, bounded by a clean Aug 24 and
an all-clean Aug 29.

disclosure_timing is the thread that carries it. Its full breach
history, all seven entries B-ward from the unanimous 20 A baseline
(band 0.40):

| date  | probe A/B | TVD  | verdict   | rerun vs probe / baseline |
|-------|-----------|------|-----------|---------------------------|
| 08-03 | 5/5       | 0.50 | EVENT     | 0.20 / 0.70               |
| 08-07 | 4/6       | 0.60 | TRANSIENT | 0.50 / 0.10               |
| 08-09 | 2/8       | 0.80 | TRANSIENT | 0.60 / 0.20               |
| 08-17 | 4/6       | 0.60 | TRANSIENT | 0.50 / 0.10               |
| 08-21 | 0/10      | 1.00 | TRANSIENT | 0.70 / 0.30               |
| 08-25 | 5/5       | 0.50 | EVENT     | 0.40 / 0.90               |
| 08-27 | 3/7       | 0.70 | EVENT     | 0.10 / 0.60               |

Three things sit in that table. First, Aug 21 hit the statistic's
maximum: unanimous B, TVD 1.00, a full flip, released within
minutes. That is this thread's first 1.00 and gpt's first
anywhere; the record's only earlier 1.00 readings are sonnet's
vuln item on Aug 3 and 6. Second, the dwell shifted mid-thread:
the first visit held within the day, the next four released
sub-day, and the two newest hold again. Third, the Aug 25 rerun
did not just hold, it deepened: probe 5/5, rerun 1/9, from 0.50 to
0.90 against baseline, within-day movement INTO the state, the
same deepening the haiku thread showed on Aug 23. Between
breaches the item rarely rests: exact baseline on only 7 of its 25
probe days, and 6/4 (TVD 0.40, exactly at the band, not a breach
under strict >) on Aug 11, 13, and 19.

The other three cluster entries:

- fraud_scoring, Aug 26, TRANSIENT: probe 8/2/0/0, the identical
  vector of its only other entry (Aug 19, also TRANSIENT). Two
  visits, one exact state.
- vuln_gating_v2, Aug 28, EVENT: probe 1/7/1/1 at 0.65, rerun
  held (0.20 vs probe, 0.65 vs baseline), and the item sat at
  unanimous C the next morning. A one-day held excursion, gone in
  under 24 hours. This thread is also direction-split: its two
  lifetime entries left the C-modal baseline for different
  destinations (7/1/1/1 A-ward on Aug 4; 1/7/1/1 B-ward on
  Aug 28). The record's only other split threads are deepseek's
  wander pair (contractor and fraud_scoring_v2); every oscillator
  thread remains direction-stable at every entry. Whether this
  item reads as a two-destination discrete state or a wander is a
  freeze classification call, and the row feeds the direction
  tallies either way.
- offboarding, Aug 23, TRANSIENT: 8/0/2/0, the fourth identical
  visit to that vector (Aug 4, 8, 13, 23). The oscillation
  continues at its own pace.

A one-day held excursion is exactly the class a multi-day
persistence filter discards by construction. The instrument kept
it because it was built to.

## The rest of the roster

- deepseek dlp_email_v2 is now a four-entry discrete thread: 
  1/0/3/6 TRANSIENT (Aug 17), 0/0/3/7 EVENT (Aug 19), 0/0/4/6
  EVENT (Aug 20), 0/0/3/7 TRANSIENT (Aug 27). All four D-ward from
  the 17 C baseline, with exact vector recurrence: 0/0/3/7 on
  Aug 19 and Aug 27. The wander-is-a-thread-property reading
  holds: dlp is discrete while contractor wanders.
- deepseek contractor added three entries in three directions:
  0/0/9/1 on Aug 15, the record's only UNSTABLE (rerun matched
  neither probe nor baseline); 3/2/1/4 TRANSIENT Aug 17; 2/0/4/4
  TRANSIENT Aug 21. The diffuse wander continues.
- deepseek edr_response: 5/1/1/3 TRANSIENT on Aug 14, its second
  lifetime entry (Aug 7 was the first, same direction).
- deepseek fraud_scoring_v2: 1/1/4/4 TRANSIENT on Aug 21, C-ward,
  its second lifetime entry and in a different direction from its
  first (2/2/2/4, Aug 9). With contractor, the second wander-side
  thread whose entries disagree on direction.
- haiku spend_anomaly_v2: seven entries Aug 15 to 23, the
  episode-two away run. Candidacy fired Aug 23 under the
  pre-committed rule; the operator answer was the dual-reference
  re-baseline; no breach since, and the return watch runs through
  the freeze. All three steps are their own dated notes.
- gemini recorded its first two lifetime breaches, both TRANSIENT,
  both on the spend-anomaly family: eq_alert_spend_anomaly at
  0/0/4/6 on Aug 15 and eq_alert_spend_anomaly_v2 at 5/0/5/0 on
  Aug 20. The Aug 15 entry landed the same day haiku EVENTed its
  own spend item. Same-day cross-vendor movement on one item
  family is noted as observation, not inference; the models share
  a scaffold and nothing else.
- sonnet: fourteen observed days, fourteen CLEAN. The pair that
  led the early record went a full window without a breach.

## Operational record

The record's first nine ERROR model-days all fall in this window,
three causes, each dated in the log:

- gpt, Aug 14 to 16: http 429, the provider account out of
  credits. Three observation days lost to our own funding lapse,
  not to the vendor. The cluster analysis above therefore sits on
  13 gpt probe days, not 16.
- haiku and sonnet, Aug 19 to 20: http 401 during the key
  rotation, documented in the candidacy note.
- gemini, Aug 22 and Aug 24: http 503 after four attempts, high
  demand on the provider side.

ERROR days extend windows and count as neither home nor away,
exactly as the rules pin.

## Decisions

One, and it is already documented: the haiku re-baseline (decided
and executed 2026-08-23, dual reference, this item only). No other
slot changed. Same bands, same K, same seeds, same verdict
grammar; no verdict reclassified; the recalibration policy draft
stays dormant until after submission.

## Reproducibility

Verdict lines and rerun details: probe/monitor/verdicts.jsonl,
dates 2026-08-14 through 2026-08-29 (through commit 36ff860).
Per-day vectors: probe/monitor/derived/daily_counts.jsonl.
Baselines and bands: probe/monitor/baselines/. Expected-count
null: probe/scripts/expected_false_breaches.py per-model rates
times observed days. Haiku days through Aug 23 are scored against
the then-in-force Aug 2 reference per the validity convention in
REBASELINE_DECISION_2026-08-23.md. Every number above recomputes
from those committed inputs.
