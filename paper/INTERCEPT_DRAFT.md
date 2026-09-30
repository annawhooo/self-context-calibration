# INTERCEPT draft: Judgment-Layer Drift, No Changelog

Status: freeze-numbered master, revised 2026-09-28 after two
verification passes. First prose draft 2026-08-22 from
docs/claude_code_handoff_intercept_paper.md; every [FREEZE]
placeholder in that draft is resolved here against the 2026-09-26
data freeze, and the swap and its amendments are recorded line by
line in paper/FREEZE_2026-09-26.md. Target: INTERCEPT Defenders
track, IEEE conference template, submission closes 2026-10-01. The
submitted LaTeX lives in paper/intercept/ and follows this text.

Numbers policy. Every number below is printed by a committed script
run at the freeze (the ledger names the script and line for each),
or is an instrument constant verified against the committed record.
Numbers marked [rows] come from the raw per-call rows, which I
retain and do not publish; the paper says so at each use. The one
figure no script can print, the monthly cost, is labeled as vendor
billing. No number goes to the PDF without a script behind it and a
verifier match.

Blind review: no author name, no organization, no repository URL in
the PDF. First person is kept; it names no one. Vendor and model
names appear because they are the subject of measurement; that is
an operator judgment call recorded in SUBMISSION_FORM.md.

---

## Judgment-Layer Drift, No Changelog

*56 Days Monitoring Five LLM APIs*

### Abstract

The behavior of a served LLM changes behind a stable model id, and the
change has a shape. I ran a calibrated behavioral monitor against five
production LLM APIs daily for 56 days. The monitor is a fixed 68-item
security judgment bank, K=10 samples per item against a frozen
baseline, simulation-calibrated alarm bands, and a same-day rerun on
every breach. Three findings. First, judgment behavior oscillates
rather than drifts: models revisit exact prior answer distributions on
contested items, one item returning to the identical unanimous vector
on four of its five breach days. Second, the movement concentrates
where judgment is contested. All 75 breach entries landed only on the
23 items authored so that practitioners split; the 45 items with a
derivable riskiest option produced no breach in 11,057
model-item-days. The breach count is not the evidence: the null
expects 92 breaches in 56 days and the record holds 75. The structure
is. The breaches pile onto thirteen items where the null expects one,
and on ten of those thirteen every breach moved toward the same
option, where the null expects 1.6. That is the same items switching,
repeatedly, between the same two answer states. Third, every serving
covariate visible from outside held constant while behavior moved,
except the identity string itself: one vendor aliased the pinned id
mid-study with no signal at the API surface, and only the
response-side echo caught it. Even that was a detection, not an
explanation. From outside the API, a customer can detect that a served
model changed, but they cannot say why. A snapshot evaluation
certifies the day it ran, not the period it is cited for. The monitor
bills about 20 USD per month, and everything but the row-level figures
marked in the text is reproducible from a public artifact.

### 1. Introduction

An agent pipeline is qualified against the model serving it.
Nothing announces when that stops being true. Vendors change
weights, quantization, serving configuration, and safety layers
behind stable model ids; the response schema carries no version for
any of it. A control validated last quarter is not validated today,
and no signal reports the expiration.

The gap is not hypothetical. One vendor's published postmortem
describes three overlapping serving-stack bugs, one of them sticky
across follow-up requests, all three missed by the vendor's own
evaluations, two of them resolved by rollback [anthropic-postmortem].
This paper measures from outside.

Here is what measuring from outside looks like. On August 2, 2026, I
baselined five production APIs on a 68-item judgment bank and probed
the full bank hours later: 340 model-item slots, zero breaches, every
model clean. The next scheduled probe, one day later, found one model
in a different regime, and a second model with a single-item EVENT the
same day, a breach that held on its rerun. On the first model, two
items flipped to a joint state they had occupied four days before, in
the pre-baseline collection runs. The flip carries probabilities on
the order of 1e-5 to 1e-13 under the smoothed null on the fresh
baseline. The state held for the same-day rerun, came apart over the
next two days, and was back in full on the third. This is not an
outage and it is not noise. It is a served model revisiting a prior
behavioral state, on a pinned id, with no changelog entry. At the
close of the 56-day record it holds 75 breach entries on 17 slots, and
not one on a decisive item.

This paper contributes:

(a) the first documentation, to my knowledge, of exact recurrence
    of prior answer distributions on pinned model ids in judgment
    behavior: reversible, day-scale, and on one thread week-scale;
(b) a drift instrument built from a stratified judgment bank,
    designed-equipoise items alongside decisive ones, with an
    11,057 slot-day zero-breach null on the decisive class;
(c) detection-without-attribution measured jointly: behavior moved
    while every observable covariate held, and the one covariate
    that moved carried no explanation either;
(d) per-model temporal phenotypes on two axes, per-call commitment
    and drift morphology. Quiet slots move within 0.011 mean TVD of
    what sampling arithmetic predicts on all five models. Where drift
    occurs, it is discrete unidirectional oscillation on three models
    (two vendors), mixed with wander on a fourth, and absent on the
    fifth, which sat near-frozen;
(e) the instrument itself: reproducible, vendor-agnostic, about 20
    USD per month in vendor billing, with a 56-day record carrying
    pre-registered decision rules, corrections, and one full
    re-baseline loop in its public history.

### 2. Instrument

The bank is 68 forced-choice enterprise security judgment items,
four options each: 45 decisive items with a derivable riskiest option
and 23 designed-equipoise items authored to sit near a decision
boundary.

Every item is sent as its scenario text followed by the same question,
verbatim: "Which single option carries the highest risk? Answer with
one line in exactly this form: ANSWER: X, where X is one of A, B, C,
D." One decisive item, verbatim:

> A small app needs to store a third party API secret. A: a managed
> secrets service with rotation and audit logs. B: an encrypted file on
> disk decrypted at process start. C: an environment variable set in the
> deploy config. D: a constant committed to a private source repository.

One equipoise item, verbatim, the fraud-scoring item of F2:

> A fraud team is setting the review policy for a transaction scoring
> model. A: a low threshold routing many transactions to manual review.
> B: auto-decline the highest scores and manually review the middle
> band. C: dynamic thresholds that adapt to observed fraud volume. D:
> fixed thresholds retuned each quarter from chargeback data.

The first has one option a practitioner can derive as the riskiest.
The second was authored so that practitioners split, and the monitor
records where each model lands, not which option is right.

Five production models, one pinned arm each, K=10 samples per item,
scheduled daily at 13:00 UTC. The 340 model-item slots each carry a
frozen baseline (n=20: two pooled same-day K=10 runs on 2026-08-02)
and a per-item alarm band: the p99 of TVD-to-baseline under a
Laplace-smoothed multinomial simulation, seeds deterministic and
recorded. Bands across the 340 slots: 0.40 x311, 0.45 x28, 0.50 x1.
One slot in full: the fraud-scoring item of section 3.1 carries the
frozen baseline 8/12/0/0 over options A to D. One slot's alarm
reference was re-baselined on 2026-08-23 from two pooled same-day K=10
runs, with the original preserved (section 3.1.1).

Vocabulary, used throughout. A slot is one model-item pair. An
entry is one breach of one slot on one day. A thread is a slot with
repeated entries. A slot-day is home when it is inside band with the
baseline's modal answer, and away otherwise. Dwell is a run of
consecutive observed days in one state.

A day's probe compares each slot's observed distribution to its
baseline. TVD is half the sum of absolute differences in option share;
the halving is because share that leaves one option arrives at
another, so the raw sum counts every move twice. Against the
fraud-scoring baseline 8/12/0/0 (shares 0.4, 0.6, 0, 0), the Aug 3
probe of 10/0/0/0 (shares 1, 0, 0, 0) gives 0.5(0.6 + 0.6) = 0.6: six
of ten answers moved, above that slot's 0.40 band, a breach. A breach
(strict inequality above band) fires a same-day rerun of the breached
items only, and the rerun disambiguates: matching the probe and not
the baseline is an EVENT, matching the baseline back is TRANSIENT,
matching neither is UNSTABLE. Every response row records the echoed
model id; a divergent echo halts collection for that model at the
first call (ECHO_CHANGE, exercised from day 40 of the record onward;
section 3.4). One verdict line per model per day, appended to a
committed log. Each line carries the day verdict and, per breached
item, the observed TVD, the band, the rerun's TVD to the probe and to
the baseline, and the item verdict. The verdict grammar is CLEAN,
EVENT, TRANSIENT, UNSTABLE, ECHO_CHANGE, ERROR. I declared the
reporting commitment before the first scheduled observation: quiet
windows get published with the same care as event windows.

The false-alarm rate is not assumed from the band percentile. It is
computed by exact enumeration over all 286 compositions of ten
draws into four options, per item, against each item's band: 1.65
expected false breaches per day if the smoothed baseline is truth,
0.05 if the empirical baseline is truth. Observed daily breach
counts sit against that null throughout. The comparison is a strict
inequality implemented in floating point, and section 4 reports
what that decided.

The record at the freeze is 56 calendar days, 2026-08-02 to
2026-09-26, with 166,006 calls in the verdict log and at least one
probe on 55 of the days. Availability gaps, all recorded in the log
and none a behavioral observation: one vendor arm lost three days
to account credit exhaustion (HTTP 429). The two arms on a second
vendor lost two days to a credential rotation on my side (HTTP 401).
A third vendor's arm returned HTTP 503 "high demand" on nine days,
seven of them in the eight ending at the freeze. One day failed on
all five arms from a local network outage. Separately, and not an
availability gap: a fifth arm halted itself on day 40 by its own
tripwire and stayed halted (section 3.4). Everything above is
regenerable from the committed repository: baselines, bands, seeds,
verdict log, derived daily counts, and every analysis script behind
a number in this paper. Numbers marked [rows] come from the raw
per-call rows, which embed full model replies and which I retain
rather than publish.

### 3. Findings

#### 3.1 Regime oscillation with exact recurrence

The headline behavior is not drift in the gradual sense. It is
discrete states, revisited exactly.

One model held a two-item joint state (terse 9 or 10 of 10 A on a
fraud-scoring item; verbose 8 to 10 of 10 D on a vulnerability-gating
item), left it, and re-entered it three days later. Both items
breached together on three of the five breach days, and the exits
staggered across days. The fraud-scoring item produced the identical
pure-A vector, 10/0/0/0, on four of its five breach days (Aug 3, 4, 6,
10). All five entries on that slot are EVENTs; the fifth breach day
(Aug 7) carried 9/1/0/0. A second model's offboarding item produced
the identical 8/0/2/0 on five of its seven breach days. A third
model's spend-anomaly item produced the identical 0/6/0/4 on seven of
its ten. These are the vectors on which the alarms fired; the same
items also sat away from baseline inside band on many more days, at
vectors that recur too (the offboarding item at 6/0/4/0 and 7/0/3/0
five days each).

Under the frozen baselines these are not plausible draws. The
recurring pure-A state has per-day probability 1.0e-4 under the
empirical baseline and 5.5e-5 under the smoothed one; the 0/0/0/10
verbose state on the vulnerability item, 1.6e-14 smoothed and zero
empirical; the 0/6/0/4 state, 1.7e-6 empirical. Point probabilities
are quoted for scale; the evidence is the recurrence of the same
vector on the same slot, and the tail probabilities of section 3.3,
which are computed over all 340 slots. Against each item's own pooled
record rather than the frozen baseline, the fraud-scoring recurrence
stays out of reach of any single multinomial: P(at least four pure-A
days in 53) = 2.3e-13 under the pooled 187 A to 343 B, which gives a
pure-A day probability of 3.0e-5. The offboarding 8/0/2/0 (P = 0.009
for at least five of 52) and the spend-anomaly 0/6/0/4 (P = 0.09 for
at least eleven of 53) are within reach of one broad stationary
distribution. Their evidence is the dwell and the direction, not the
vector. The states are also not new: they are prior observed states of
the same items. That is what motivates calling this oscillation rather
than drift. Away days are not, in general, temporally clustered beyond
exchangeability (runs test on the home/away sequence: |z| < 1.6 on
eleven of thirteen threads, z = -0.11 on the fraud-scoring item); two
threads cluster (z = -2.3). Week-scale dwell in a breaching state was
demonstrated under a pre-committed rule on the haiku thread alone
(section 3.1.1). That thread also holds the record's longest away run,
sixteen observed days against the frozen reference; four other threads
carry away runs of 8 to 12 observed days that breached on at most two
days each. Short dwell is the norm: the gpt disclosure-timing item,
unanimous at baseline, never held an excursion past a single day in 52
observed, and its unanimous patch-timing sibling never past two. The
same-day rerun gives a lower bound on within-state persistence. Across
the record the gap from the last probe sample of a breached item to
its first rerun sample is 0.34 to 10.15 minutes, median 1.86 [rows].
The rerun reproduced the probe vector exactly on 8 of the 75 entries.

#### 3.1.1 The pre-committed step-change rule, and one full loop

The rule, committed 2026-08-16 blind to the deciding data, resolved
the first episode on the haiku spend-anomaly item as alternation on
its first evaluated day (a home visit on Aug 14). A second away run
began Aug 15 and crossed the pre-committed threshold on 2026-08-23:
seven consecutive observed away days. The rule designated the item a
step-change candidate with no judgment in the loop. I responded with a
dual-reference re-baseline: the alarm reference moved to the new
state, the frozen original stayed preserved in the same record, and a
return criterion against the original was pre-registered before any
new-regime data accrued. The criterion fired on post-rebaseline day
10. On 2026-09-02, after sixteen consecutive observed away days
spanning the re-baseline, the item revisited the original reference:
inside the superseded band, modal restored, on a vector identical to
two of its early home-dwell days four weeks prior. The pre-registered
branch executed as a dated commit the same day, merged the following
morning before the next probe day landed. I revised the classification
to slow alternation with week-scale dwell. The candidacy stands as a
correctly fired rule; the revision changes the classification, not the
firing. I re-examined the re-baseline as pre-committed and kept it:
the item rests in the new state and visits the old one, and the
preserved original is what made the return visible at all. From the
return day on, the item sat at the original reference on seven days
through Sep 18 (Sep 2, 6, 9, 10, 13, 16, 18) and then sat away for the
seven observed days ending at the freeze. Against the frozen reference
it was home on 16 of 53 observed days. This was not a step change. It
is the longest-dwell alternation in the record. Every step of the loop
(rule, candidacy, re-baseline, return criterion, revision) ran on
machinery pinned before its deciding data was read. The first rule was
committed with three unread probe days already on disk, as its note
records, and every later step's data postdates its pin.

I pinned four more rules on gpt threads, three after a held EVENT on
the thread and one from home ahead of any away run. Their thresholds
were 12, 8, 3, and 4 consecutive observed away days, each the thread's
own longest returned-from dwell plus two days of clearance. None
fired. The longest count any reached was 4 of 12. A fifth rule, on the
deepseek data-loss item, stood at 2 of 5 when the arm's identity
changed; the rule is suspended, not resolved. Of the six pins, two
carry a registration caveat and one a process note. The first pin was
committed with unread probe days on disk, and its blindness rests on a
same-day attestation. One was merged after post-pin data existed, and
its blindness rests on a retrospective attestation. The process note:
two sessions drafted the same rule under one filename; the merged
draft met its validity condition and the duplicate was closed
unmerged. I report the grades rather than hide them.

#### 3.2 The movement concentrates where judgment is contested

Every breach the monitor recorded is an equipoise item. All 75
breach entries across 56 days landed on designed-equipoise slots,
17 distinct slots in all. The decisive class produced zero breaches
in 11,057 slot-day observations. (140 of the window's 16,664
slot-days fall on model-days whose run did not complete and were
never gated; none of them exceeded a band in either arithmetic.)
The concentration reads differently under the two nulls, and I give
both. Under the smoothed null the equipoise share of breach mass is
0.383 and P(all 75 entries on equipoise) = 5.1e-32. Under the
empirical null, where 221 of 225 decisive slots cannot breach at
all, the share is 0.968 and the same probability is 0.087. The
concentration is a description of where this instrument can see
movement, not a significance claim.

The claim needs its ceiling stated. At K=10 the bands sit near TVD 0.4
regardless of item distribution. A breach therefore needs five of ten
samples to change category on 339 of the 340 slots under the written
strict-inequality rule (the one slot with a 0.50 band needs six); the
float path breaches at a lower lattice TVD on 24 mixed-baseline slots
(section 4, item f). All but four of the 225 decisive slots sit
unanimous at baseline (the four are one vendor's 16-of-20 and 19-of-20
splits); registering movement there requires close to an outright
answer flip. Decisive silence is an instrument ceiling, not
demonstrated stability. What the decisive record does show is how
little those slots move. The maximum decisive slot-day TVD in 11,057
was 0.30, reached twice, and no other slot-day exceeded 0.20 in exact
arithmetic; 28 sat exactly at 0.20, five of which the float path reads
as above. The defensible claim is that detectable movement lives on
contested judgment, and clear-cut behavior stayed frozen at the
resolution this instrument has.

#### 3.3 Structure against the honest null

The breach count is not evidence, and I will say so before leaning
elsewhere. The smoothed null expects 92.1 entries in 56 days, and the
pooled comparison with the observed 75 (P(at least 75) = 0.97) hides a
cancellation: the null puts 56.9 of its entries on decisive slots that
produced none (P(zero) = 1.7e-25) and 35.3 on equipoise slots that
produced 75 (P(at least 75) = 3.5e-9). The null overcharges unanimous
slots for a prior that their frozen distributions may not deserve, and
the empirical null, which treats an n=20 estimate as exact, expects
3.0 entries in all. Neither is the truth. I report the split and lean
on structure.

What neither null can produce is the structure. Chance breaches spread
across slots; the smoothed null expects its 92 entries on about 80
distinct slots. The observed 75 entries pile onto 17. Thirteen slots
carry three or more entries each, against 1.04 expected slots at that
depth (P = 6.7e-11); seven carry five or more, against 0.0063 (P =
4.4e-20). Direction is structured too. Given the thirteen threads and
their entry counts, the smoothed null expects 1.6 of them to move
toward the same option at every breach; ten do (P = 6.8e-10), and five
of the seven deepest do against 0.7 expected (P = 3.3e-7). The three
threads that are not direction-stable all belong to one vendor, and
section 3.5 returns to them. Two caveats travel with every number
here. Slots within a model-day share a scaffold (the same prompt
wrapper, request path, and scheduled hour) and are not independent;
the recurrence statistics are computed per-slot across days, where the
sharing argument does not apply. And the smoothed null charges every
arm for all 56 days, including the 37 model-days whose run did not
complete and were never gated, which inflates its expectations and
makes each upper tail conservative; the one lower tail, P(zero) on
decisive slots, moves the other way (3.7e-22 under probed days only).
Under exact rather than floating-point arithmetic (section 4, item f)
the record reads 65 entries on 16 slots, still all equipoise, ten
threads at three or more entries (eight unidirectional) and five at
five or more (four unidirectional). The concentration and direction
findings survive in kind; the tail probabilities above are computed
under the as-recorded semantics only.

#### 3.4 Detection without attribution

Behavior moved. No recorded covariate did. The rows carry the echoed
model id and the reasoning flag on every arm, and the host field and
the sent temperature on the one arm whose SDK exposes them. Across
174,033 rows [rows], each recorded covariate took one value per model
on every row that entered a behavioral verdict. No covariate co-varied
with any breach, because none took a second value while behavior was
being measured. The EVENT label itself is weaker than designed, and I
demote it: the same-day rerun certifies persistence over minutes (0.34
to 10.15, median 1.86 [rows]), not the twenty the early record
estimated. The persistence evidence is not the rerun. It is cross-day
recurrence of exact states.

Then the one covariate that had held did move, and it was the identity
itself. On 2026-09-10 the deepseek arm's first call echoed
deepseek-flash against the pinned deepseek-v4-flash. The tripwire
halted collection at one call; the single reply under the ambiguous
identity was logged and no distribution was sampled under it. On every
day since then on which a call returned, the first contact recorded
the same divergent echo: 16 halted days at the freeze. The vendor
surface, checked two days later with the response bodies committed
verbatim, shows an alias that is silent at the API surface (no vendor
notice was checked). The pinned id is gone from the model list, yet a
request for it still serves, answered under the new name, with the
same system fingerprint behind both names. No request for the pinned
id was refused. This is not an outage, and it did not present as a
deprecation; a customer pinning by request string would have seen
nothing at all. The sequence on the record, stated without
attribution: the arm's data-loss item ran nine breach days from Aug
17, five of them being held EVENTs, its excursions deepest in the four
days before the name moved. Then the behavioral record ends at
2026-09-09 with a pinned step-change counter suspended at two of five.
Outside observation cannot say whether that escalation was a staged
rollout.

The asymmetry is the operational point. A customer-side monitor
can say "this model is not behaving as it did when qualified," with
dated, reproducible evidence. It cannot say why, and no amount of
black-box observation fixes that [casper, cai]. The monitor's
product is a dated evidence trail, not a diagnosis.

#### 3.5 Temporal phenotypes

Outside the focal threads, no model moves. On quiet equipoise slots,
mean observed TVD sits within +0.011 of the exact expectation under a
stationary baseline on all five models, once the expectation charges
for probe sampling and baseline estimation noise together. Per model:
haiku +0.000, sonnet +0.005, gpt +0.006, gemini +0.009, deepseek
+0.011. On the breached threads the same excess runs +0.086 to +0.137.
That holds while per-call spread varies: mean modal share runs 0.91 to
0.99 across vendors. Ambient drift is zero at this instrument's
resolution; every detected movement belongs to a named, recurring
thread.

The phenotypes are two axes that do not reduce to each other: how a
model answers (per-call commitment) and how it moves when it moves
(thread morphology). The two Claude models and gpt are
commit-and-flip: near-deterministic per call (modal share 0.97 to
0.99), threads that are discrete oscillations with exact state
recurrence, and every one of their eight threads with three or more
entries is unidirectional. The haiku thread is commit-and-flip at week
scale: a seven-observed-day rest, a sixteen-observed-day away dwell,
and a return to a vector it had produced four weeks earlier. Deepseek
is sampling noise with wander. It has the widest per-call spread in
the roster (modal share 0.91), quiet slots within +0.011 of sampling
arithmetic, and the record's only mixed-direction threads, three of
its six. Those three breach toward two or three different options, two
of them from split baselines and the data-loss item from a 17-of-20
reference. Its two other threads with three or more entries are
unidirectional (the sixth slot breached once), so the wander is a
thread property that this vendor alone exhibits. Gemini sat
near-frozen through its 46 probe days: two transient breaches on two
different items and nothing held. The same 23 items, on the same 56
days, produced no thread on this arm: the flipping belongs to the
model-item pair, not to the item. Per-call determinism is not temporal
stability. Of the four models that answer most consistently within a
day (modal share 0.97 to 0.99), three flipped between days; the other,
gemini at 0.99, sat near-frozen.

Format rides along as an independent observable. On the
vulnerability-gating item, answer state and response format flip in
lockstep: 567 of 580 rows are either a terse 9-character A or a
687-to-1,421-character reasoned D [rows]. The fraud-scoring item
flips with zero length change: 600 rows, every one 9 characters
whatever the letter [rows]. Format is a serving-state signal the
parsed-letter statistic only sees when the letter moves; it is
captured per row and reported descriptively.

### 4. What the instrument got wrong

The CFP asks for honest failure. Seven items, each a dated commit
in the public record, each load-bearing for someone building the
same thing.

(a) The false-alarm arithmetic was wrong first. I estimated 3.4 chance
    breaches per day by treating p99 as an exact exceedance rate; on a
    discrete statistic at K=10 it is not. Exact enumeration corrected
    it to 1.64 (smoothed truth) and 0.05 (empirical truth); the
    correction is the citable number, and it moved to 1.65 when one
    slot was re-baselined.
(b) I approved a sensitivity upgrade on 2026-08-06, scored it
    against the committed baselines, and did not land it before the
    next scheduled run; the decline was recorded on 2026-08-13.
    K=30 narrows the bands from 0.40 to 0.267 on most slots and to
    at most 0.317 (recomputed from the committed baselines under
    the stored seeds). The between-day variance the bands never
    modeled sits at p99 0.30 on quiet equipoise slots at the
    freeze, inside that range and above its floor (it was 0.35 on
    the first twelve days). At K=10 exceedance rates, an upper bound
    on what those bands would have manufactured is 0.7 to 1.5 false
    alarms per full probe day from the 98 quiet equipoise slots
    alone. The reason is measured, not assumed. The mean daily TVD
    over the 98 quiet equipoise slots decomposes into a sampling
    term (0.0205) and a between-day excess (0.0096). A K=30
    projection shrinks the mean to 0.71 of its K=10 value, not the
    0.58 that square-root scaling predicts, because the excess does
    not shrink with K.
(c) The frozen baseline can be the anomaly. 82 of 115 equipoise
    slots were unanimous at baseline, on items designed to split. For
    those slots the monitor may have enshrined an excursion as the
    reference and then alarmed on movement toward designed behavior;
    three of the 82 breached. The instrument therefore says "changed,"
    never "degraded"; the sign of change is not identified.
(d) EVENT
    certifies minutes, not the roughly twenty that the early record
    estimated for the probe-to-rerun gap. Measured item-level gaps run
    0.34 to 10.15 minutes [rows]; from run start to rerun start, 7.6
    to 38.8, median 10.7. I demoted the label in the analysis rather
    than defend it.
(e) The first version of this paper's phenotype figure repeated
    the baseline error in miniature: its expected-movement term
    treated the frozen n=20 baseline as exact and so misread the
    widest-distribution vendor's sampling spread as drift. The
    corrected expectation propagates baseline noise exactly;
    mistake and correction are same-day dated commits.
(f) The breach comparison ran in floating point on quantities that
    are exact rationals, and the summation path decided real verdicts.
    A bit-faithful census (committed script) finds 10 of the 75
    entries fired on exact at-band equalities the float path read as
    strictly above, from both sides of the comparison. Zero breaches
    were missed. One item verdict flipped at the rerun gate, an EVENT
    that is a TRANSIENT under exact arithmetic. Six of the day
    verdicts change: five TRANSIENT to CLEAN and the record's only
    UNSTABLE to CLEAN. The verdict log stands as recorded. Every
    headline claim survives both semantics in kind (65 entries on 16
    slots, all equipoise; ten threads at three or more entries, eight
    unidirectional), and the false-breach null moves in step (1.65 to
    1.55 expected false breaches per day, smoothed truth). The
    instrument moves to exact integer comparison after submission, no
    earlier than a pre-registered date.
(g) The monitor had gaps of its own. Twenty-one model-days in 56
    failed on availability: three to exhausted API credit, four to
    a credential rotation (two arms, two days), nine to one
    vendor's HTTP 503 responses, five to a local network outage on
    a single day. After the first two losses I added a pre-probe
    live-request check (one call per vendor, hours before the
    probe); it tests keys by calling and would have caught both. It
    did not catch the vendor 503s, because the bank ran four
    attempts at one hour and then nothing until the next day; a
    monitor that matters should retry at a second scheduled hour,
    and this one did not.

### 5. Operational guidance

For a team running judgment-layer automation on a frontier API,
the numbers above convert to practice.

Split the bank by class and set bands accordingly. Decisive items are
near-noiseless: in 11,057 slot-days the maximum TVD was 0.30, seen
twice, and nothing else exceeded 0.20 in exact arithmetic. A decisive
band of 0.25 would have fired twice in 56 days under either
arithmetic; 0.30 would never have fired under exact comparison and
twice under the monitor's float path (item f). Either band is a gain
over the deployed 0.40 to 0.45, and monitoring there is free
sensitivity, provided a pre-registered rollback rides along (the
drafted, not yet adopted, recalibration policy reverts if the
tightened class produces more than three entries in its first fourteen
days). Equipoise bands cannot narrow at K=10: between-day spread does
not shrink with K (item b), so they stay at 0.40 or above and their
alarms are read as regime signals, not degradation.

Treat snapshot evaluation as day-certification. A passed eval
certifies the day it ran. Period assurance requires a monitor in the
loop, and the monitor defines the compensating control. When a slot
flags, five actions follow. Re-run the acceptance tests of every
pipeline that depends on that model. Gate or freeze automated
decisions qualified against prior behavior. Fail over to a pinned
alternative where one exists. Open a vendor ticket with dated evidence
rather than a hunch. Record a control-effectiveness event. Write the
observable into vendor contracts, not the cause, which no customer can
observe. The observable is distribution stability on a pinned bank,
for example no decisive-class breach at a 0.30 band over a rolling 30
days. The alarm load at K=10 and the deployed bands was 1.4 breached
items per probe day across five arms, 24 percent of probed model-days
non-CLEAN, and 3.7 EVENT model-days per seven probe days. Every entry
landed on one of 17 slots, 14 of which repeated, so triage cost is
dominated by known threads, not new ones.

Re-baseline without discarding. When a monitored slot settles into
a new state and the alarm channel turns into a daily repeat of the
same event, do not choose between the old reference and the new
one; keep both. Move the alarm to the new reference, preserve the
original in the same record, and pre-register the return criterion
before any new-regime data accrues. Mechanically: two same-day K
samples of the one item (20 calls), accepted only if the run pair
sits inside its own band and the new reference sits outside the old
one; the old reference governs through the re-baseline day, the new
one from the next. The first use of this pattern ran its full loop
inside the record: rule fired, re-baseline the same day, return
detected on post-rebaseline day 10, pre-registered revision
committed the same day as detection, six more return days after
that (3.1.1). A bare re-baseline would have converted a slow
alternator into a permanent misclassification. The preserved
reference is what caught the return.

Pin by served identity, not by request string. The request id is an
input; the identity that answers is an observation, and they can
diverge without any request failing. When the name that the deepseek
flash tier answered under changed mid-study, the pinned id kept
serving as a silent alias, and only the response-side echo
distinguished the qualified model from whatever now answered to its
name. Record the echo on every row, halt on divergence, and treat the
halt as an event: that converted a silent alias into a dated detection
at first contact. On divergence, re-qualify the new identity as a new
arm with its own baseline and bands, never as a continuation, and
re-verify every pinned request flag (reasoning mode, temperature)
against the new name. A rename can carry a configuration change the
request no longer binds. I left the arm halted through the freeze to
keep the instrument byte-constant for this paper.

Budget for the monitor's own gaps. Credit, credentials, vendor
availability, and my own network each took days out of this record
(item g). Alarm on a missing probe the way you alarm on a breach. A
monitor that did not run observed nothing, and a day with no
observation is an ERROR line, not a CLEAN one.

Know what the tool cannot do. Detection is not attribution. It tells a
team when to stop trusting automation qualified against prior
behavior; it does not identify what changed on the serving side. When
procurement or contract language assumes attribution from outside the
API, that language promises something the measurement cannot deliver.

### 6. Related work

Log-probability tracking of LLM APIs [chauvin-a] samples hourly and
flags change on a rolling-window statistic over single-token log
probabilities, a grey-box observable this instrument does not use. Its
token-efficient successor [chauvin-b] filters in-vivo changes with a
four-day persistence rule, and a state that reverts within days never
survives that filter. The oscillation class documented here needed an
instrument that keeps such states; the instruments are complementary.
Daily and weekly periodicity in LLM performance [tschisgale] is the
continuous cousin of the discrete recurrence here. Longitudinal
behavioral change on major APIs is established at month scale [chen];
this work moves the resolution to days and adds exact state
recurrence. The attribution ceiling is structural, not a limitation of
effort: black-box access does not support causal attribution of
serving-stack change [casper], and black-box audits of model
substitution can be evaded, which points toward hardware attestation
rather than more observation [cai]. Boundary-item drift sensing
predates LLMs: margin-density drift detection placed its sensors at
the decision boundary [md3], the same design choice the equipoise
class makes here. A published postmortem [anthropic-postmortem]
supplies vendor-side ground truth that serving changes ship, can stick
across follow-up requests, and evade vendor evals; the numerics
mechanism for silent behavioral variation is documented in
[thinking-machines].

### 7. Limitations and reproducibility

One bank, five models, one scaffold, 56 days. The phenotypes are
observed styles, not vendor properties. Slots within a model-day share
a scaffold; day-level counts are overdispersed and the per-slot
recurrence statistics carry the independence caveat stated in 3.3. The
detection floor at K=10 is a five-of-ten answer shift, so sub-floor
movement is invisible and decisive-class stability is bounded, not
proven. The baseline is one day. A multi-day baseline would have
characterized two-state items before the bands were pinned; the
pooled-record tails in section 3.1 are the check that the finding does
not depend on which state the baseline day caught. The instrument
reports change, not degradation: 82 of 115 equipoise slots were
unanimous at baseline, so the frozen reference may itself be the
excursion (section 4, item c). The strict inequality at the band is
load-bearing, and its float implementation decided ten at-band entries
(item f); the entry, slot, thread, and direction counts carry their
exact-arithmetic companions from the committed census, and the null
tails are reported under the as-recorded semantics only. The null is a
choice, not a fact: the smoothed and empirical baselines put the same
concentration at 5.1e-32 and 0.087, and the direction rows condition
on the observed threads (section 3.3, T1). One arm's behavioral record
ends on day 39 by its own tripwire, and another arm's availability
failed for the last eight days of the window; the per-model probe-day
counts are 53, 53, 52, 46, and 39. The per-call rows that carry
response text are retained but not published, and therefore so are the
rerun-gap, format, and covariate constancy numbers marked [rows];
everything else is published. Cost and cadence are modest by design;
the instrument trades sensitivity for a false-alarm budget one person
can staff. Of the six pre-registered rules one fired, four never did,
and one is suspended; two pins carry a registration caveat (section
3.1.1). Covariate constancy is claimed over the recorded fields only:
echoed id and reasoning flag on every arm, host and sent temperature
on one.

The full instrument is reproducible: item bank, baselines, bands,
seeds, verdict log, derived daily counts, analysis scripts, and
every correction cited above as dated history. The artifact is
public; the link is withheld from this submission for blind review
and supplied on acceptance.

---

## Figures and tables (regenerated at the freeze, data through 2026-09-26)

Generation scripts live in paper/figures/ and read only the
committed record; with PAPER_DATA_THROUGH=2026-09-26 they draw the
frozen window. Current renders in paper/figures/out are stamped
with their data-through date and embed TrueType fonts.

- F1 Regime map. Fourteen focal threads (slots with two or more
  entries) x 56 days, state per cell (home, away, breach with
  verdict letter), hatched no-probe days, dotted echo-halt days,
  and the first day the haiku re-baselined reference governs
  marked.
- F2 Exact recurrence strip. The sonnet fraud-scoring item's daily
  distributions as stacked bars; the four identical pure-A visits
  annotated.
- F3 False-alarm curve. Quiet-slot exceedance vs band width by
  class under the monitor's float comparison; deployed bands and
  the declined K=30 bands marked.
- F4 Phenotype grid. Per-call commitment x excess movement, quiet
  slots and all 17 breached slots split per model; quiet slots hug
  zero on all five. Decomposition table:
  quiet_slot_decomposition.py.
- T1 Structure vs null. Observed / expected / P for count,
  distinct slots, recurrence tiers, concentration, direction (joint
  rows from the null script, conditional rows from
  freeze_numbers.py).
- T2 Instrument summary. Bank composition, cadence, bands, billing.

## References (primary-source verified 2026-09-28)

- [chauvin-a] Chauvin, Le Merrer, Taiani, Tredan, Log Probability
  Tracking of LLM APIs, arXiv:2512.03816, ICLR 2026.
- [chauvin-b] Chauvin, Lalanne, Le Merrer, Loubes, Taiani, Tredan,
  Token-Efficient Change Detection in LLM APIs, arXiv:2602.11083,
  ICML 2026.
- [tschisgale] Tschisgale, Wulff, Daily and Weekly Periodicity in
  Large Language Model Performance and Its Implications for
  Research, arXiv:2602.15889.
- [chen] Chen, Zaharia, Zou, How is ChatGPT's behavior changing
  over time?, arXiv:2307.09009.
- [casper] Casper et al., Black-Box Access is Insufficient for
  Rigorous AI Audits, arXiv:2401.14446, FAccT 2024.
- [cai] Cai, Shi, Zhao, Song, Are You Getting What You Pay For?
  Auditing Model Substitution in LLM APIs, arXiv:2504.04715.
- [md3] Sethi, Kantardzic, On the Reliable Detection of Concept
  Drift from Streaming Unlabeled Data (MD3), arXiv:1704.00023.
- [anthropic-postmortem] Anthropic, A postmortem of three recent
  issues, Anthropic Engineering, Sep 2025.
- [thinking-machines] He and Thinking Machines Lab, Defeating
  Nondeterminism in LLM Inference, Sep 2025.

Precision notes carried from the handoff: arXiv:2603.01919 audited
three shadow APIs, not 17. arXiv:2506.23706 is an ICML TAIG
workshop paper. Optional anchor arXiv:2605.15164 still carries a
check-against-PDF-before-quoting tag.
