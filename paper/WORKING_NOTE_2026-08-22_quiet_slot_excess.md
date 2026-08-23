# Working note: quiet-slot excess, and the wanderer

Date: 2026-08-22. Paper-side working analysis for the INTERCEPT
draft (paper/INTERCEPT_DRAFT.md). Records a same-day metric
correction to the first committed version of figure F4, and the
direction analysis that reclassified the one non-direction-stable
repeat thread. Analysis of record:
paper/figures/quiet_slot_decomposition.py, exact enumeration
throughout, committed inputs only (verdict log, derived daily
counts, qualified baselines), record through 2026-08-20 at
writing. Recorded in the correction pattern of NOISE_FLOOR.md and
DESIGN_LIMITATIONS.md: the mistake is part of the record.

## The mistake

The first committed F4 (same day, earlier commit) plotted mean
equipoise slot-day TVD against baseline, minus the exact expected
TVD of a K=10 draw under a stationary truth, as its movement axis.
That expectation treats the frozen n=20 baseline as exact. For a
model whose true per-item distributions are wide, the baseline is
a noisy estimate of a wide distribution, so observed TVD carries
baseline estimation error the expectation never charges for. The
figure therefore penalized exactly the vendor with the widest
per-call spread and read deepseek as the most-moving model
(model-level excess +0.050 against haiku's +0.012). This is
DESIGN_LIMITATIONS.md Limitation 3, unpropagated baseline sampling
error, reproduced in miniature inside the paper's own tooling.

## The correction

Two changes, both in figdata.expected_tvd_pair and the rebuilt F4.

1. The expectation redraws BOTH sides: the probe at K=10 and the
   reference at n=20 from the same plug-in truth (the empirical
   baseline), by exact enumeration over both composition sets. No
   sampling, deterministic reruns.
2. Slots are split by history: quiet slots (no breach entry in the
   verdict log) versus focal-thread slots. Averaging the two
   together had let thread concentration masquerade as a model
   property.

## What the corrected numbers say

From quiet_slot_decomposition.py part 1, record through
2026-08-20, equipoise slots, excess = observed mean TVD minus the
exact probe-plus-baseline expectation:

    model         quiet slots        thread slots
    haiku         +0.000 (22 slots)  +0.248 (1 slot)
    sonnet        +0.004 (21)        +0.174 (2)
    gpt-terra     +0.007 (17)        +0.102 (6)
    gemini-flash  +0.009 (21)        +0.109 (2)
    deepseek      +0.007 (17)        +0.092 (6)

Deepseek's quiet slots sit at the same near-zero excess as every
other vendor's; its raw mean TVD of 0.109 is almost entirely its
own sampling arithmetic (expectation 0.102). The consecutive-day
check (part 2) agrees: quiet-slot day-to-day TVD 0.131 against an
exact two-draw floor of 0.113. The honest-noise phenotype survives
measurement once the measurement is honest.

The stronger result is the split itself. Excess movement on quiet
slots is at most +0.009 on any vendor; excess on thread slots runs
+0.092 to +0.248. Ambient drift on this bank, at this resolution,
is zero. Every detected movement belongs to a named recurring
thread. The draft's section 3.5 and abstract now carry that claim.

## The wanderer

Part 3 assigns each breach in every >=3-entry thread a direction,
the option gaining most share over baseline. Six of the seven
threads are unidirectional at every breach: haiku spend toward B
(x7), sonnet fraud toward A (x5), sonnet vuln toward D (x3), gpt
offboarding toward A (x5), gpt disclosure toward B (x4), deepseek
dlp_email toward D (x3). The seventh, deepseek's contractor item,
breached toward D, A, C, then A, from a genuinely mixed baseline
(0/8/9/3), and carries the record's only UNSTABLE verdict.

This is not an oscillator that broke a direction rule. It is a
second drift morphology: diffuse wander rather than discrete
two-state flip. The draft's section 3.3 was reframed accordingly,
from "direction-stable 5 of 5" (the 12-day figure) to "oscillators
6 of 6, plus one wanderer that is not an oscillator". The wander
is a thread property, not a vendor property: deepseek's dlp thread
is as discrete and unidirectional as the sonnet pair.

## Status of these numbers

Everything above regenerates from the committed record by running
the script; the freeze regeneration (2026-09-26) replaces the
figures in the draft per its numbers policy. Nothing here touches
the monitor, the bands, any baseline, or any verdict.
