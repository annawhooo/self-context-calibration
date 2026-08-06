"""Exact expected false breaches per day for the drift monitor.

Regenerates the corrected expectations in probe/DESIGN_LIMITATIONS.md
("Corrected false-breach expectation") from the committed baseline
files. No network and no sampling: these figures are exact, so a run
that does not reproduce the published numbers means a baseline file
changed.

Method. A false breach is a probe that exceeds an item's band p99 while
nothing has actually drifted. For one item, enumerate every composition
of K draws into the four options (286 of them at K=10), weight each by
its multinomial probability under an assumed truth, compute the TVD
between the baseline and that composition with each side normalized by
its own count, and sum the probability of the compositions exceeding
that item's committed band p99. The comparison is a strict inequality,
matching the monitor's breach test. Summing over all 340 alarm slots
gives the expected count of false breaches per probe day.

Two truths, as in the note. The smoothed baseline (c+1)/(n+4) carries
the same Laplace prior the bands are built on, so it admits that the
n=20 baseline is an estimate rather than the fact of the matter. The
empirical baseline c/n treats the observed counts as exact. The gap
between the two figures is the cost of unpropagated baseline sampling
error, DESIGN_LIMITATIONS.md Limitation 3. TVD is measured against the
empirical pooled baseline in both cases; only the generating truth
changes.

This replaces the naive "340 slots times 1 percent, or 3.4 per day",
which treats p99 as an exact exceedance rate. On a discrete statistic
p99 is the smallest value with at least 99 percent coverage, so the
true tail mass per item is usually well below 1 percent.

K is pinned to the K of the committed bands. Scoring draws at one K
against a band computed at another K is not a false-breach rate at all,
so this constant moves only when the baselines themselves are
recomputed.

Run: python probe/scripts/expected_false_breaches.py
"""
import os
import json
import glob
import math
import collections

HERE = os.path.dirname(os.path.abspath(__file__))
BASELINES = os.path.join(HERE, os.pardir, "monitor", "baselines")
OPTIONS = ("A", "B", "C", "D")
K = 10

# Published in DESIGN_LIMITATIONS.md; printed alongside as a check.
PUBLISHED = {"smoothed": 1.64, "empirical": 0.05}


def compositions(k, parts):
    """Every way to split k draws across parts options."""
    if parts == 1:
        yield (k,)
        return
    for i in range(k + 1):
        for rest in compositions(k - i, parts - 1):
            yield (i,) + rest


def log_multinomial(comp, log_probs):
    """Log probability of one composition, or None if it needs an option
    the truth assigns zero mass."""
    lp = math.lgamma(sum(comp) + 1)
    for c, l in zip(comp, log_probs):
        lp -= math.lgamma(c + 1)
        if c:
            if l is None:
                return None
            lp += c * l
    return lp


def truth_probs(counts, n, truth):
    """Generating distribution over OPTIONS under the named truth."""
    if truth == "smoothed":
        return [(counts.get(o, 0) + 1.0) / (n + 4.0) for o in OPTIONS]
    return [counts.get(o, 0) / n for o in OPTIONS]


def item_false_breach_rate(counts, n, p99, truth, comps):
    """P(TVD(baseline, K-draw) > p99) for one item under one truth."""
    base = [counts.get(o, 0) / n for o in OPTIONS]
    probs = truth_probs(counts, n, truth)
    log_probs = [None if p <= 0 else math.log(p) for p in probs]
    acc = 0.0
    for comp in comps:
        lp = log_multinomial(comp, log_probs)
        if lp is None:
            continue
        tvd = 0.5 * sum(abs(b - c / K) for b, c in zip(base, comp))
        if tvd > p99:
            acc += math.exp(lp)
    return acc


def main():
    comps = list(compositions(K, len(OPTIONS)))
    paths = sorted(glob.glob(os.path.join(BASELINES, "*.json")))
    if not paths:
        raise SystemExit("no baseline files under %s" % BASELINES)

    print("K=%d, %d compositions of %d draws into %d options"
          % (K, len(comps), K, len(OPTIONS)))
    slots = 0
    totals = collections.Counter()
    per_model = collections.defaultdict(dict)

    for path in paths:
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
        if doc["k"] != K:
            raise SystemExit(
                "baseline %s was qualified at k=%s but this script assumes "
                "K=%d; bands and draws must share one K"
                % (os.path.basename(path), doc["k"], K))
        alarm = {iid: rec for iid, rec in doc["items"].items()
                 if rec["class"] == "alarm"}
        slots += len(alarm)
        for truth in ("smoothed", "empirical"):
            total = 0.0
            for rec in alarm.values():
                total += item_false_breach_rate(
                    collections.Counter(rec["baseline_counts"]), rec["n"],
                    rec["band"]["p99"], truth, comps)
            per_model[doc["model"]][truth] = total
            totals[truth] += total

    print("%d alarm slots across %d models" % (slots, len(paths)))
    print()
    print("expected false breaches per probe day")
    for truth in ("smoothed", "empirical"):
        print("  truth = %-9s baseline   %.2f   (published %.2f)"
              % (truth, totals[truth], PUBLISHED[truth]))
    print()
    print("per model")
    for model in sorted(per_model):
        print("  %-28s smoothed %.2f   empirical %.3f"
              % (model, per_model[model]["smoothed"],
                 per_model[model]["empirical"]))


if __name__ == "__main__":
    main()
