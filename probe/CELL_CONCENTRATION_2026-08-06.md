# Cell concentration: five days of monitor breaches, 2026-08-06

Date: 2026-08-06. Companion to NOISE_FLOOR.md,
DRIFT_EVENT_2026-07-31.md, and DRIFT_EVENT_2026-08-03.md. An
aggregate observation over the monitor window to date, expected to
be superseded as days accrue; the drift event notes are the frozen
per-event records.

## Finding

Every band breach the monitor has recorded lands on a
designed-equipoise item. Five probe days (Aug 2 to Aug 6), five
models, 340 alarm-set slots per day, 1,700 item-day observations:
nine breaches, on five distinct items, across two models and two
vendors, all nine on equipoise items.

The bank is 45 derivable and 23 equipoise items (33.8 percent
equipoise). Under a uniform null, five of five distinct breached
items landing in the equipoise cell has probability 3.2e-3. The
per-event figure (nine of nine) is 5.8e-5, but breach events on the
same item are not independent, so the distinct-item number is the
one to lean on.

Derivable items did not move at all: zero exceedances in 1,125
item-day observations, with the largest observed distance reaching
half its band. The one-sided 95 percent upper bound on the
derivable exceedance rate is 0.27 percent (rule of three). Observed
equipoise exceedance is 9 of 575, 1.57 percent.

## The sensitivity ceiling caveat

The honest claim is that detectable drift concentrates on
equipoise items, not that drift occurs only there. At K=10 the
smoothed simulation bands are effectively flat near TVD 0.4
regardless of item distribution (a discreteness effect, not an
entropy adjustment), so registering a breach requires roughly four
of ten samples to change category. Derivable items sit unanimous
at baseline; a breach there requires close to an outright answer
flip. Derivable silence is therefore an instrument ceiling, not
demonstrated stability. A probe-K increase narrows the threshold
and is analyzed separately; it requires no re-baseline because
bands recompute offline from the committed baseline counts.

## Relation to prior design notes

DRIFT_EVENT_2026-07-31.md, design consequence 3, predicted that
contested judgment items near a decision boundary surface narrow
serving changes first. Nine of nine is consistent with that
prediction. NOISE_FLOOR.md, design consequence 2, expected
decisive items to carry the drift alarm when they move; nothing in
five days contradicts the conditional (no decisive item has
moved), but the alarm load so far is carried entirely by the
equipoise cell, and consequence 3's framing of equipoise items as
sensitive positive controls is the one the data currently favors.

## Scale of the claim

Five days, one bank, five models. The concentration is a property
of this window and this instrument at K=10. It establishes where
this monitor's sensitivity lives; it does not establish that
derivable behavior is stable, and it says nothing about cause.

## Reproducibility

Verdicts: probe/monitor/verdicts.jsonl, all lines through
2026-08-06 (committed). Slot counts and exceedance rates derive
from the five baseline files in probe/monitor/baselines/ (68 alarm
items per model, zero sentinels) and the daily probe row files.
Band flatness and the K analysis: smoothed_bands in
probe/monitor/monitor.py against the stored baseline_counts.
