# Code handoff: INTERCEPT submission, the drift monitor as a paper

Context: INTERCEPT is AARM's runtime-security venue (San Francisco,
Feb 2027). Submissions close 2026-10-01, notification 2026-10-31,
IEEE conference PDF under 4 MB via their Overleaf template, blind
review (organizers strip author and company names), three
evaluators. Tracks: Builders, Breakers, Defenders. The CFP's stated
preference: real systems, data, demos, and honest failure over
theoretical proposals. CFP fetched 2026-08-14 from
aarm.dev/intercept/call-for-papers; re-verify details at submission
time.

Target: DEFENDERS track. The submission is the drift monitor as an
operational runtime control: live since 2026-08-02, about 20 USD per
month, committed longitudinal record, roughly 60 days of data by the
deadline. The honest-failure requirement is our comparative
advantage: DESIGN_LIMITATIONS.md, the corrected false-breach
arithmetic, and the declined-then-vindicated K=30 upgrade are all
dated, committed, public history.

Working title candidates (pick at drafting):
- Commit and Flip: Reversible Regime Oscillation in Served LLM
  Judgment Behavior
- The Motion Detector: Continuous Behavioral Monitoring of LLM APIs
  as an Operational Runtime Control
- Judgment-Layer Drift, No Changelog: Sixty Days Monitoring Five
  LLM APIs

## Paper skeleton (IEEE short, target 4-6 pages)

1. INTRODUCTION. The runtime-control problem: agents perform
   judgment calls; the model substrate under the agent moves; a
   clean snapshot certifies the day of the test, not the period.
   Open with the Aug 2 exhibit: full 68-item bank clean on all five
   models hours after baselining; first regime flip the next day.
   Contributions paragraph: (a) first documentation of reversible
   day-scale regime oscillation in served LLM judgment behavior;
   (b) the equipoise/clear-cut stratified bank as a drift
   instrument, with a 2,700 slot-day zero-movement null on the
   clear-cut class; (c) detection-without-attribution measured
   jointly; (d) per-vendor temporal phenotypes; (e) the instrument
   itself, reproducible at 20 USD per month.
2. INSTRUMENT. 68-item forced-choice enterprise security judgment
   bank, 23 designed-equipoise + 45 decisive; five models, one
   pinned arm each; K=10 samples per item daily at 13:00 UTC;
   per-item TVD vs a frozen n=20 baseline against
   simulation-calibrated p99 bands (0.40 x311, 0.45 x28, 0.50 x1);
   same-day disambiguation rerun on breach; echo tripwire; verdict
   grammar (CLEAN/EVENT/TRANSIENT/UNSTABLE/ECHO_CHANGE/ERROR).
   Exact-enumeration null (expected_false_breaches.py): 1.64
   expected false breaches/day smoothed truth, 0.05 empirical.
   Everything regenerable from the committed repo.
3. FINDINGS. All headline numbers below are the verified 12-day
   figures and are PLACEHOLDERS tagged [FREEZE]: regenerate every
   one at the data freeze (section: Data plan) and replace.
   3.1 Regime oscillation. Exact recurring states ([FREEZE]:
       sonnet fraud 10/0/0/0 on Aug 3,4,6,10; gpt offboarding
       8/0/2/0 x3, 9/0/1/0 x2; haiku 0/6/0/4 x2). Dwell 1-2 daily
       observations, irregular; attractors persist weeks. Sub-hour
       reversion bound from rerun windows. Haiku step-change
       resolution per the committed decision rule (see below):
       report whichever way it resolved.
   3.2 Concentration. [FREEZE] 29/29 breaches on equipoise items;
       zero in 2,700 decisive slot-day checks; honest eq null share
       0.381; P(all-eq) 7.3e-13, distinct-slot 3.6e-6.
   3.3 Structure vs the honest null. Count is weak (29 obs vs 19.7
       exp, p=0.029): say so plainly, it buys credibility for the
       rest. Recurrence: slots >=3 breaches 5 obs vs 0.0101 exp,
       P=8.0e-13; direction-stable 5 of 5, combined P=1.3e-16;
       count-calibrated survival 2.3e-10. Independence caveat in
       the same breath.
   3.4 Detection without attribution. Covariates constant across
       all [FREEZE] 41,090 rows; echo never moved. EVENT statistic
       demoted honestly: certifies 0.4-5.3 min persistence
       (median 2.4), degrades to p=0.68 under serving-state
       correlation. Cross-day recurrence is the real persistence
       evidence.
   3.5 Phenotypes. The 2x2: per-call consistency x temporal
       stability. Gemini frozen-committed; deepseek honest-noise;
       claude/gpt commit-and-flip. Per-call determinism is not
       temporal stability; the most confident-looking style is the
       least snapshot-auditable. Format signal as independent
       observable (sonnet vuln lockstep 148/150; sonnet fraud flips
       with zero length change).
4. HONEST FAILURE (name the section approximately this; the CFP
   asks for it and nearly no one delivers). Four items, all dated
   in public history: (a) the naive 3.4/day false-breach estimate,
   corrected to 1.64 by exact enumeration, correction committed;
   (b) K=30 upgrade approved, built, then declined the same day
   when analysis showed narrowed bands amplify unmodeled
   between-day variance; vindicated empirically two weeks later
   (measured eq between-day p99 0.35 sits above the proposed
   0.267-0.317 bands: 1.5-2.5 false alarms/day avoided); (c) the
   baseline-as-excursion sign inversion: 82/115 equipoise slots
   unanimous at baseline, so for some items the frozen reference
   may be the anomalous state; the instrument says "changed," never
   "degraded"; (d) EVENT gate certifies minutes, not the ~20 the
   design assumed.
5. OPERATIONAL GUIDANCE (Defenders payload). Class-split bands
   (decisive can tighten to 0.20 with zero observed exceedances or
   run K=30 safely; equipoise stays >=0.40 at K=10; sqrt-K scaling
   empirically wrong for eq). Snapshot certification vs period
   assurance. The compensating-control pattern: route flagged
   periods to secondary review; spec the observable in contracts,
   not the cause. What the tool cannot do: attribute. Detection
   tells you when to stop trusting your own automation, not whom
   to blame.
6. RELATED WORK. Differentiate against the Chauvin cluster
   explicitly: their instruments require persistence (>=4-day
   filter; one-way changepoints), so the oscillation class is
   discarded by construction; ours kept it. Tschisgale/Wulff
   periodicity as the reversible-but-continuous cousin. Chen et
   al. as field anchor. Casper/Cai for the attribution ceiling
   being structural. MD3 as the pre-LLM boundary-sensor lineage
   the LLM literature never cites. Full citation set below. Avoid
   the term "audit gap" in this paper: keep it self-contained;
   the detection-attribution asymmetry needs no branded term.
7. LIMITATIONS AND REPRODUCIBILITY. One bank, five models, one
   scaffold, N days; phenotypes are observed styles; independence
   caveat; detection floor (~4-5 of 10 answer shift at K=10);
   strict-> at the band is load-bearing (>= raises null mass
   4.8x). Repo link for full reproduction (see blind-review note).

## Figures and tables

- F1 Regime map: cross-thread state timeline (threads x days,
  baseline/drifted/breach marks). The 12-day version exists in the
  deep-read tables; regenerate at freeze. This is the money figure.
- F2 Exact recurrence strip: sonnet fraud daily distributions as
  stacked bars; annotate the four identical pure-A visits.
- F3 False-alarm curve: empirical quiet-slot exceedance vs band
  width, with deployed bands and the declined K=30 bands marked.
- F4 Phenotype 2x2: per-call consistency x temporal stability,
  five models placed.
- T1 Structure vs null: observed / expected / P for count,
  recurrence tiers, direction, cross-model.
- T2 Instrument summary: bank composition, cadence, bands, cost.

## Data plan

- The monitor keeps running unchanged at K=10. No band changes, no
  re-baselines before submission unless the committed haiku rule
  triggers one; if it does, that is a finding, not a disruption:
  document, do not suppress.
- PREREQUISITE, DO FIRST: commit the haiku step-change decision
  rule as a dated note (probe/ or docs/) BEFORE more deciding data
  arrives. Rule as agreed: sustained hold at/near the new state
  with no clean home visits = step change, open re-baseline
  discussion as a dated operator decision; clean home visits
  resume = alternator, frozen baseline stays. Pre-registering this
  is both good practice and paper material.
- Freeze: 2026-09-26 (55 days of data). Re-run the deep-read
  analysis lanes at the freeze (the four-lane workflow pattern with
  adversarial verification of the two load-bearing lanes; scripts
  from the 12-day run are the template). Replace every [FREEZE]
  number. No number enters the PDF without a script behind it and
  a verifier match.
- Timeline: by Sep 1, prose draft in a FRESH session from this
  handoff (12-day numbers as placeholders); Sep 26 freeze and
  regenerate; Sep 27-29 number swap + verification fan-out (every
  figure in prose diffed against script output) + IEEE template +
  blind pass; submit no later than Sep 30.

## Citation set (all primary-verified 2026-08-13/14 unless tagged)

- Chauvin et al., Log Probability Tracking of LLM APIs,
  arXiv:2512.03816, ICLR 2026.
- Chauvin et al., Token-Efficient Change Detection in LLM APIs
  (B3IT), arXiv:2602.11083, ICML 2026.
- Tschisgale, Wulff, Daily and Weekly Periodicity in LLM
  Performance, arXiv:2602.15889.
- Chen, Zaharia, Zou, How Is ChatGPT's Behavior Changing over
  Time?, arXiv:2307.09009 (cite arXiv; HDSR venue detail is
  secondary-corroborated only).
- Casper et al., Black-Box Access is Insufficient, arXiv:2401.14446.
- Cai et al., arXiv:2504.04715 (software-only verification brittle;
  TEE direction).
- Sethi, Kantardzic, MD3 margin-density drift detection,
  arXiv:1704.00023.
- Anthropic, A postmortem of three recent issues (2025),
  anthropic.com/engineering/a-postmortem-of-three-recent-issues.
  Two of three issues rollback-resolved, one code-fixed; sticky
  per-user; missed by vendor evals.
- Thinking Machines batch-invariance deep-dive (2025), for the
  numerics mechanism.
- Optional, only if the asymmetry framing needs an anchor: Seth,
  Sankarapu, arXiv:2605.15164 (position; pre-deployment access
  intervals). Their [Vi, Ai] wording still carries a
  check-against-PDF-before-quoting tag.
Precision notes: arXiv:2603.01919 audited THREE shadow APIs, not
17. arXiv:2506.23706 is an ICML TAIG workshop paper.

## Blind-review handling

Organizers strip author and company names, but the paper cites its
own public repo, which deanonymizes. Options, in preference order:
(1) ask the organizers (a community venue may not care; the CFP
emphasizes real systems); (2) cite an anonymized artifact mirror
for review and swap the real link at camera-ready; (3) omit the
link at submission and state "public artifact, link on
acceptance." Decide before drafting the reproducibility section.
Also: scrub the paper of first-person references to prior named
work of ours that would identify the author chain; the related-work
differentiation must not say "our earlier repo."

## Submission form (CFP asks three short sections)

- Core topics: continuous behavioral monitoring of LLM APIs as a
  runtime control; reversible day-scale regime oscillation in
  judgment behavior; boundary-item instrumentation; false-alarm
  calibration; the detection/attribution ceiling of customer-side
  monitoring.
- Key takeaways: snapshot evals certify a day, not a period;
  judgment calls drift while clear-cut behavior stays frozen;
  per-call consistency is not temporal stability; a calibrated
  monitor costs 20 USD/month; detection tells you when to distrust
  your automation, not whom to blame.
- Significance/audience: teams operating agents on frontier APIs
  in controlled processes (security operations, compliance,
  ICFR-adjacent automation); vendors of runtime-security tooling;
  anyone writing model-stability language into contracts.

## Style and process constraints

- Anna's voice (anna-voice skill in the drafting session): lead
  with the finding, negation-then-assertion, short declaratives,
  first-person ownership, no em dashes, contractions kept.
- 76-char wrap in any repo-committed markdown; the PDF follows the
  IEEE template instead.
- Counting rule: no number in prose without a script behind it.
- This handoff is same-repo (self-context-calibration) and may be
  committed per the repo's handoff-doc precedent.
