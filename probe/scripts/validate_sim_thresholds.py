"""Validate simulation-based thresholds against the frozen noise data.

For each model and item: take run1's distribution as the baseline,
simulate 10,000 K=10 re-draws from it, compute TVD of each draw
against the baseline, and record the simulated 95th/99th percentile.
Then check where the OBSERVED run2 TVD falls. If the simulator is
right, observed TVDs should exceed the simulated 99th percentile on
roughly 1% of items (about 0.7 of 68), and the equipoise items'
observed swings should sit comfortably inside their (wide) bands.
"""
import json
import random
import collections

NOISE1 = r"C:\Users\Anna\PycharmProjects\self-context-calibration\convergence\results\noise_run1.jsonl"
NOISE2 = r"C:\Users\Anna\PycharmProjects\self-context-calibration\convergence\results\noise_run2.jsonl"
OPTIONS = ("A", "B", "C", "D")
K = 10
SIMS = 10000
SEED = 20260731

rng = random.Random(SEED)

def item_counts(path):
    out = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        p = r.get("parsed")
        if p in OPTIONS:
            out[r["model"]][r["item_id"]][p] += 1
    return out

def tvd(ca, cb, na, nb):
    return 0.5 * sum(abs(ca.get(o, 0) / na - cb.get(o, 0) / nb)
                     for o in OPTIONS)

def simulate_percentiles(base, smooth=1.0):
    """Laplace-smoothed plug-in: an observed 10-0-0-0 baseline becomes
    11-1-1-1 over 14 before simulation, so bands carry honest width on
    items whose K=10 estimate may be a lucky draw. smooth=0 recovers
    the naive plug-in."""
    n = sum(base.values())
    probs = [(base.get(o, 0) + smooth) / (n + smooth * len(OPTIONS))
             for o in OPTIONS]
    tvds = []
    for _ in range(SIMS):
        draw = collections.Counter(
            rng.choices(OPTIONS, weights=probs, k=K))
        tvds.append(tvd(base, draw, n, K))
    tvds.sort()
    return tvds[int(0.95 * SIMS) - 1], tvds[int(0.99 * SIMS) - 1]

d1 = item_counts(NOISE1)
d2 = item_counts(NOISE2)

for model in sorted(d1):
    over95 = over99 = compared = 0
    flagged = []
    for iid in sorted(d1[model]):
        base = d1[model][iid]
        obs = d2[model].get(iid)
        if not obs:
            continue
        compared += 1
        p95, p99 = simulate_percentiles(base)
        o = tvd(base, obs, sum(base.values()), sum(obs.values()))
        if o > p95:
            over95 += 1
        if o > p99:
            over99 += 1
            flagged.append((iid, round(o, 3), round(p99, 3)))
    print(f"{model}")
    print(f"  items {compared}; observed over sim-95th: {over95} "
          f"(expect ~{compared*0.05:.1f}); over sim-99th: {over99} "
          f"(expect ~{compared*0.01:.1f})")
    for iid, o, p in flagged:
        print(f"    over-99th: {iid}  observed {o}  sim99 {p}")
