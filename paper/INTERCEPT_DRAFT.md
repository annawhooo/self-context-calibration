# INTERCEPT draft: Judgment-Layer Drift, No Changelog

Status: prose draft, 2026-08-22, written from
docs/claude_code_handoff_intercept_paper.md. Target: INTERCEPT
Defenders track, IEEE conference template, 4 to 6 pages, submission
closes 2026-10-01.

Numbers policy. Every figure tagged [FREEZE] is the verified 12-day
figure (2026-08-02 to 2026-08-13) and is a placeholder: regenerate
at the 2026-09-26 data freeze and replace before it enters the PDF.
Untagged numbers are instrument constants, verified against the
committed record at drafting time (band histogram recomputed from
the five committed baseline files on 2026-08-22: p99 0.40 x311,
0.45 x28, 0.50 x1). No number goes to the PDF without a script
behind it and a verifier match.

Title picked at drafting; the two alternates from the handoff stay
available. Day count in the title is [FREEZE: 55 at the planned
freeze date].

---

## Judgment-Layer Drift, No Changelog

*[FREEZE: 55] Days Monitoring Five LLM APIs*

### Abstract

Served LLM behavior changes behind stable model ids, and the change
has a shape. I ran a calibrated behavioral monitor against five
production LLM APIs daily for [FREEZE: 55] days: a frozen 68-item
security judgment bank, K=10 samples per item, per-item total
variation distance against a frozen baseline, simulation-calibrated
alarm bands, and a same-day disambiguation rerun on every breach.
Three findings. First, judgment behavior oscillates: models revisit
exact prior answer distributions on contested items, day-scale
dwell, week-scale persistence of the attractor states, entries
sometimes arriving as same-day joint moves across items
([FREEZE] two round trips in seven days on one vendor). Second, the
movement concentrates entirely where judgment is contested:
[FREEZE: 29 of 29] breach entries landed on designed-equipoise
items while the decisive class produced zero exceedances in
[FREEZE: 2,700] slot-day checks, and quiet equipoise slots show no
movement beyond exact sampling expectation on any vendor: the
drift is not ambient, it lives in named recurring threads. Third,
every serving covariate
observable from outside the API stayed constant across [FREEZE:
41,090] rows while behavior moved, so a customer can detect the
change but cannot attribute it. A snapshot evaluation certifies the
day it ran, not the period it is cited for. The monitor costs about
20 USD per month, and the full instrument, record, and analysis are
reproducible from a public artifact.

### 1. Introduction

An agent pipeline is qualified against the model serving it.
Nothing announces when that stops being true. Vendors change
weights, quantization, serving configuration, and safety layers
behind stable model ids; the response schema carries no version for
any of it. A control validated last quarter is not validated today,
and no signal reports the expiration.

The gap is not hypothetical. One vendor's published postmortem
documents three concurrent serving-stack bugs, sticky per-user,
missed by the vendor's own evaluations and resolved by rollback
[anthropic-postmortem]. That is the vendor telling us what the
serving layer does when nobody is measuring from outside.

Here is what measuring from outside looks like. On August 2, 2026,
I baselined five production APIs on a 68-item judgment bank and
probed the full bank hours later: 340 slots, zero breaches, every
model clean. The next scheduled probe, one day later, found one
model in a different regime: two items flipped to a joint state
they had occupied three days before, at probabilities on the order
of 1e-9 to 1e-13 under the fresh baseline. The state held for the
same-day rerun, reverted days later, and returned again. This is
not an outage and it is not noise. It is a served model revisiting
a prior behavioral state, on a pinned id, with no changelog entry.

This paper contributes:

(a) the first documentation, to my knowledge, of reversible
    day-scale regime oscillation in served LLM judgment behavior,
    with exact recurrence of prior answer distributions;
(b) a drift instrument built from a stratified judgment bank,
    designed-equipoise items alongside decisive ones, with a
    [FREEZE: 2,700] slot-day zero-movement null on the decisive
    class;
(c) detection-without-attribution measured jointly: behavior moved
    while every observable covariate held;
(d) per-vendor temporal phenotypes on two axes, per-call
    commitment and drift morphology: quiet slots show zero excess
    movement on all five models, and drift, where it occurs, is
    discrete unidirectional oscillation or diffuse wander;
(e) the instrument itself: reproducible, vendor-agnostic, roughly
    20 USD per month to operate.

### 2. Instrument

The bank is 68 forced-choice enterprise security judgment items,
four options each: 45 decisive items with a derivable best answer
and 23 designed-equipoise items authored to sit near a decision
boundary. Five production models, one pinned arm each, K=10 samples
per item, daily at 13:00 UTC. The 340 model-item slots each carry a
frozen baseline (n=20: two pooled same-day K=10 runs) and a
per-item alarm band: the p99 of TVD-to-baseline under a
Laplace-smoothed multinomial simulation, seeds deterministic and
recorded. Bands across the 340 slots: 0.40 x311, 0.45 x28,
0.50 x1.

A day's probe compares each slot's observed distribution to its
baseline. A breach (strict inequality above band) fires a same-day
rerun of the breached items only, and the rerun disambiguates: a
rerun matching the probe and not the baseline is an EVENT, matching
the baseline back is TRANSIENT, matching neither is UNSTABLE. Every
response row records the echoed model id; a mid-run id change halts
collection for that model (ECHO_CHANGE). One verdict line per model
per day, appended to a committed log. The verdict grammar is CLEAN,
EVENT, TRANSIENT, UNSTABLE, ECHO_CHANGE, ERROR, and the reporting
commitment was declared before the first scheduled observation:
quiet windows get published with the same care as event windows.

The false-alarm rate is not assumed from the band percentile. It is
computed by exact enumeration over all 286 compositions of ten
draws into four options, per item, against each item's band: 1.64
expected false breaches per day if the smoothed baseline is truth,
0.05 if the empirical baseline is truth. Observed daily breach
counts sit against that null throughout. Everything above is
regenerable from the committed repository: baselines, bands, seeds,
verdict log, and the enumeration script.

### 3. Findings

#### 3.1 Regime oscillation with exact recurrence

The headline behavior is not drift in the gradual sense. It is
discrete states, revisited exactly.

One vendor's model held a two-item joint state (unanimous terse A
on a fraud-scoring item; verbose 9-10 D on a vulnerability-gating
item), left it, and re-entered it [FREEZE: twice in seven days],
with entries arriving as same-day joint moves and exits staggering
across days. The fraud-scoring item visited the identical pure-A
distribution [FREEZE: four times (Aug 3, 4, 6, 10)]. A second
vendor's offboarding item recurred at exact vectors [FREEZE:
8/0/2/0 three times, 9/0/1/0 twice]. A third vendor's
spend-anomaly item settled into an away state at the identical
vector [FREEZE: 0/6/0/4, twice by Aug 13; the episode continued
past the window and resolved under a pre-committed decision rule,
reported in 3.1.1]. Dwell in a state is one to two daily
observations; the attractor states themselves persist for weeks.
The same-day rerun bounds within-state reversion: across the
window, probe-to-rerun gaps run [FREEZE: 0.43 to 5.28] minutes
(median 2.4), and reruns reproduced the probe exactly on the
strongest events.

Under the frozen baselines these are not plausible draws. The
recurring pure-A state has per-run probability [FREEZE: 5.5e-5];
the 10 D verbose state, [FREEZE: 1.6e-14 per run, 2.5e-28 across a
probe-rerun pair]. The states are also not new: they are prior
observed states of the same items. That is what motivates calling
this oscillation rather than drift.

#### 3.1.1 The pre-committed step-change rule

The rule, committed 2026-08-16 blind to the deciding data,
resolved the first episode as alternation on its first evaluated
day (a home visit on Aug 14). A second away run began Aug 15 and
crossed the pre-committed threshold on 2026-08-23: seven
consecutive observed away days, every one B-modal on the identical
discrete vector or a deeper excursion, and the rule designated the
item a step-change candidate with no judgment in the loop. The
operator response was a dual-reference re-baseline: the alarm
reference moved to the new state, the frozen original stayed
preserved in the same record, and a return criterion against the
original was pre-registered before any new-regime data accrued
[FREEZE: report the return-watch outcome; a return day revises the
classification to slow alternation, no return leaves the step
change standing with a stated day-count bound, and both branches
are dated commits].

#### 3.2 The movement concentrates where judgment is contested

Every breach the monitor has recorded is an equipoise item.
[FREEZE: 29 of 29] breach entries across [FREEZE: 12] days landed
on designed-equipoise slots; the decisive class produced zero
exceedances in [FREEZE: 2,700] slot-day observations. The honest
null share for the equipoise class is 0.381 of breach mass (not
the 0.338 uniform share; equipoise bands sit differently), and the
concentration survives that weighting: [FREEZE: P(all-equipoise)
7.3e-13 at entry level, 3.6e-6 on distinct slots].

The claim needs its ceiling stated. At K=10 the bands sit near TVD
0.4 regardless of item distribution, so a breach needs roughly
four of ten samples to change category. Decisive items sit
unanimous at baseline; registering movement there requires close
to an outright answer flip. Decisive silence is an instrument
ceiling, not demonstrated stability. The defensible claim is that
detectable movement lives on contested judgment, and clear-cut
behavior stayed frozen at the resolution this instrument has.

#### 3.3 Structure against the honest null

The breach count alone is weak evidence, and I will say so before
leaning elsewhere: [FREEZE: 29 observed against 19.7 expected
under the smoothed null, p = 0.029]. What the null cannot produce
is the structure. Chance breaches spread across slots; the
observed entries pile onto repeat threads. [FREEZE: five slots
carry three or more breaches each, against 0.0101 expected slots
at that depth, P = 8.0e-13.] Direction is structured too, and it
splits the threads into two morphologies. Every oscillator thread
moved toward the same option every time it moved [FREEZE: 6 of 6
at the drafting record, against 0.008 expected same-direction
threads; tails in T1]. The one repeat thread that is not
direction-stable is not an oscillator at all: deepseek's
contractor-access item breached toward three different options
across four entries and carries the record's only UNSTABLE
verdict, a same-day rerun matching neither probe nor baseline.
That thread is a diffuse wander, not a two-state flip, and the two
morphologies are kept distinct wherever drift is counted
(paper/figures/quiet_slot_decomposition.py, part 3). Slots within
a model-day share a scaffold and are not
independent; the recurrence statistics are computed per-slot
across days, where the sharing argument does not apply, and the
caveat is stated wherever the numbers are.

#### 3.4 Detection without attribution

Behavior moved. Nothing else did. Across [FREEZE: 41,090] rows,
every serving covariate visible from outside held constant: the
echoed model id never changed, reasoning flags were constant per
model, and no infrastructure field co-varied with any breach. The
EVENT label itself is weaker than designed and I demote it
honestly: the same-day rerun certifies persistence over [FREEZE:
0.4 to 5.3] minutes, not the twenty the design assumed, and under
a serving-state correlation model the EVENT/TRANSIENT split
carries [FREEZE: p = 0.68] of discriminating power. The
persistence evidence is not the rerun. It is cross-day recurrence
of exact states.

The asymmetry is the operational point. A customer-side monitor
can say "this model is not behaving as it did when qualified,"
with dated, reproducible evidence. It cannot say why, and no
amount of black-box observation fixes that [casper, cai]. The
monitor's product is a dated evidence trail, not a diagnosis.

#### 3.5 Temporal phenotypes

Where drift does not live settles what per-call behavior means.
Outside the focal threads, no model moves: on quiet equipoise
slots, mean observed TVD sits within [FREEZE: +0.009] of the exact
expectation under a stationary baseline, on all five models, once
the expectation charges for probe sampling and baseline estimation
noise together. That holds while per-call spread varies widely
(mean modal share [FREEZE: 0.92 to 0.99] across vendors). Ambient
drift is zero at this instrument's resolution; every detected
movement belongs to a named, recurring thread.

The phenotypes are therefore two axes that do not reduce to each
other: how a model answers (per-call commitment) and how it moves
when it moves (thread morphology). The Claude models and gpt are
commit-and-flip: near-deterministic per call, threads that are
discrete oscillations with exact state recurrence, entries
unidirectional every time. Deepseek is honest noise: the widest
per-call spread in the roster, quiet slots fully explained by
sampling arithmetic, and the record's only diffuse-wander thread
in its contractor item (its dlp thread is discrete, so the wander
is a thread property, not a vendor property). Gemini sat
near-frozen through the window [FREEZE: two transient breaches].
Per-call determinism is not temporal stability, and the most
confident-looking style is the least snapshot-auditable.

Format rides along as an independent observable. On the
vulnerability-gating item, answer state and response format flip in
lockstep [FREEZE: 148 of 150 samples]: terse 9-character rows in
one state, 766 to 1,421 character reasoned rows in the other. The
fraud-scoring item flips with zero length change. Format is a
serving-state signal the parsed-letter statistic only sees when
the letter moves; it is captured per row and reported
descriptively.

### 4. What the instrument got wrong

The CFP asks for honest failure. Five items, each a dated commit
in the public record, each load-bearing for someone building the
same thing.

(a) The false-alarm arithmetic was wrong first. Working analysis
    estimated 3.4 chance breaches per day by treating p99 as an
    exact exceedance rate; on a discrete statistic at K=10 it is
    not. Exact enumeration corrected it to 1.64 (smoothed truth)
    and 0.05 (empirical truth), and the correction is the citable
    number.
(b) A sensitivity upgrade was approved, built, and declined the
    same day. K=30 narrows bands from roughly 0.40 to [FREEZE:
    0.267 to 0.317]; the between-day variance the bands never
    modeled sits at [FREEZE: p99 = 0.35] on equipoise items, above
    the proposed bands. Shipping it would have manufactured
    [FREEZE: 1.5 to 2.5] false alarms per day. Two weeks of
    accumulated cross-day data vindicated the decline empirically.
(c) The frozen baseline can be the anomaly. [FREEZE: 82 of 115]
    equipoise slots were unanimous at baseline, on items designed
    to split. For those slots the monitor may have enshrined an
    excursion as the reference and then alarmed on movement toward
    designed behavior. The instrument therefore says "changed,"
    never "degraded"; the sign of change is not identified.
(d) EVENT certifies minutes, not the roughly twenty the design
    assumed. Measured probe-to-rerun gaps run [FREEZE: 0.43 to
    5.28] minutes. The label was demoted in the analysis rather
    than defended.
(e) The first version of this paper's phenotype figure repeated
    the baseline error in miniature. Its expected-movement term
    treated the frozen n=20 baseline as exact, which charges the
    widest-distribution vendor for its own sampling spread, and
    the figure misread honest noise as drift. The corrected
    expectation propagates baseline noise exactly; mistake and
    correction are same-day dated commits.

### 5. Operational guidance

For a team running judgment-layer automation on a frontier API,
the numbers above convert to practice.

Split the bank by class and band accordingly. Decisive items are
near-noiseless ([FREEZE: zero exceedances above 0.20 in 2,700
slot-days]): their bands can tighten to 0.25 and monitoring there
is essentially free sensitivity. Equipoise bands cannot narrow at
K=10: between-day spread does not shrink with K ([FREEZE:
sqrt-K scaling measured wrong for the equipoise class]), so they
stay at 0.40 or above and their alarms are read as regime signals,
not degradation.

Treat snapshot evaluation as day-certification. A passed eval
certifies the day it ran. Period assurance requires a monitor in
the loop, and the monitor defines the compensating control: route
flagged periods to secondary review, gate automated decisions
qualified against prior behavior, and write the observable into
vendor contracts (distribution stability on a pinned bank), not
the cause, which no customer can observe.

Know what the tool cannot do. Detection tells you when to stop
trusting your own automation. It does not tell you whom to blame,
and procurement or contract language that assumes attribution from
outside the API is writing a check the measurement cannot cash.

### 6. Related work

Log-probability and token-level API change detection [chauvin-a,
chauvin-b] targets the same problem with instruments that require
persistence: multi-day filters and one-way changepoints. The
oscillation class documented here is discarded by those designs by
construction; a state that reverts within days never survives a
four-day persistence filter. The instruments are complementary,
and the reversible class needed one that keeps it. Daily and
weekly periodicity in LLM performance [tschisgale] is the
continuous cousin of the discrete recurrence here. Longitudinal
behavioral change on major APIs is established at month scale
[chen]; this work moves the resolution to days and adds exact
state recurrence. The attribution ceiling is structural, not a
limitation of effort: black-box access does not support causal
attribution of serving-stack change [casper], and software-only
verification of served models remains brittle [cai]. Boundary-item
drift sensing predates LLMs: margin-density drift detection placed
its sensors at the decision boundary [md3], the same design choice
the equipoise class makes here. Vendor-side ground truth that
serving changes ship, stick per-user, and evade vendor evals comes
from a published postmortem [anthropic-postmortem]; the numerics
mechanism for silent behavioral variation is documented in
[thinking-machines].

### 7. Limitations and reproducibility

One bank, five models, one scaffold, [FREEZE: N] days. The
phenotypes are observed styles, not vendor properties. Slots
within a model-day share a scaffold; day-level counts are
overdispersed and the per-slot recurrence statistics carry the
independence caveat stated in 3.3. The detection floor at K=10 is
roughly a four-of-ten answer shift, so sub-floor movement is
invisible and decisive-class stability is bounded, not proven.
The strict inequality at the band is load-bearing: moving to
greater-or-equal raises null breach mass [FREEZE: 4.8x]. Cost and
cadence are modest by design; the instrument trades sensitivity
for a false-alarm budget an operator can actually staff.

The full instrument is reproducible: item bank, baselines, bands,
seeds, verdict log, analysis scripts, and every correction cited
above as dated history. [Blind-review handling per the handoff:
decide before submission. Default if the organizers do not object:
"public artifact, link on acceptance"; otherwise an anonymized
mirror for review. Do not cite the repository by name in the
submitted PDF.]

---

## Figures and tables (regenerate at freeze)

Generation scripts live in paper/figures/ and read only the
committed record; current renders in paper/figures/out are stamped
with their data-through date. The freeze regeneration is a re-run.

- F1 Regime map. Threads x days state timeline, baseline/drifted/
  breach marks per focal thread. The money figure. 12-day version
  exists in the deep-read tables; regenerate over the full window.
- F2 Exact recurrence strip. The fraud-scoring item's daily
  distributions as stacked bars; annotate the identical pure-A
  visits.
- F3 False-alarm curve. Empirical quiet-slot exceedance vs band
  width; mark deployed bands and the declined K=30 bands.
- F4 Phenotype grid. Per-call commitment x excess movement, quiet
  and thread slots split per model; quiet slots hug zero on all
  five. Decomposition table: quiet_slot_decomposition.py.
- T1 Structure vs null. Observed / expected / P for count,
  recurrence tiers, direction stability, cross-model.
- T2 Instrument summary. Bank composition, cadence, bands, cost.

## References (verified 2026-08-13/14; re-verify at submission)

- [chauvin-a] Chauvin et al., Log Probability Tracking of LLM
  APIs, arXiv:2512.03816, ICLR 2026.
- [chauvin-b] Chauvin et al., Token-Efficient Change Detection in
  LLM APIs (B3IT), arXiv:2602.11083, ICML 2026.
- [tschisgale] Tschisgale, Wulff, Daily and Weekly Periodicity in
  LLM Performance, arXiv:2602.15889.
- [chen] Chen, Zaharia, Zou, How Is ChatGPT's Behavior Changing
  over Time?, arXiv:2307.09009 (cite arXiv; venue detail is
  secondary-corroborated only).
- [casper] Casper et al., Black-Box Access is Insufficient,
  arXiv:2401.14446.
- [cai] Cai et al., arXiv:2504.04715.
- [md3] Sethi, Kantardzic, MD3 margin-density drift detection,
  arXiv:1704.00023.
- [anthropic-postmortem] Anthropic, A postmortem of three recent
  issues, 2025.
- [thinking-machines] Thinking Machines batch-invariance
  deep-dive, 2025.

Precision notes carried from the handoff: arXiv:2603.01919 audited
three shadow APIs, not 17. arXiv:2506.23706 is an ICML TAIG
workshop paper. Optional anchor arXiv:2605.15164 still carries a
check-against-PDF-before-quoting tag.
