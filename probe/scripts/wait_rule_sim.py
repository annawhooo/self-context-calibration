"""Simulation behind the evaluation section of
probe/STEP_CHANGE_DECISION_RULE_2026-10-18.md: six wait-rule reset forms
for gpt-5.6-terra eq_disclosure_timing. The plan below was fixed before
the first run on 2026-10-18. Prints; decides nothing. Reads only the
committed derived daily counts, and only dates through 2026-10-15, so it
never loads data from the wait rule's counting window. No network, no
state, nothing written.

  python probe/scripts/wait_rule_sim.py

DATA: probe-phase A counts (n=10) for this item.
  HOME-regime pool = every probe day 2026-08-02 .. 2026-10-08 (spikes
                     included: they happened inside the home regime).
  AWAY-regime pool = 2026-10-09 .. 2026-10-15 (5 observed days).
HOME day (rule definition) <=> A >= 6 of 10 (TVD <= 0.40 vs 20/20 A AND
unique modal A). Missing days are not simulated (observed days only).

AWAY-STATE MODELS (sensitivity; truth unknown):
  W1 resample the 5 away days
  W2 beta-binomial, method-of-moments fit to the 5 away days
  W3 binomial at the pooled away share (no overdispersion)
HOME-STATE MODEL: resample the home pool.

TRUTH SCENARIOS (day 1 = 2026-10-17, item away on day 1, horizon 60
observed days):
  S1 step change: away for all 60 days.
  S2a slow alternator: away dwell remaining ~ geometric mean 10, then
      home dwells ~ geometric mean 7 and away dwells ~ geometric mean 10.
  S2b same, away dwells mean 20.
  S3 quick return: away remaining ~ geometric mean 3, then home for good.

RULE FORMS (threshold 18 everywhere, as the operator pinned):
  R1 reset on one HOME day; re-baseline at 18 consecutive AWAY.
  C1 close as alternation on the first HOME day; re-baseline at 18.
  R2 a single HOME day neither counts nor resets; two consecutive HOME
     days reset; re-baseline when the AWAY count reaches 18.
  C2 close on two consecutive HOME days; otherwise as R2.
  W  re-baseline when at least 16 of the latest 18 observed days are
     AWAY; never closes.
  B3 pool non-overlapping 3-day blocks (30 answers); block HOME <=>
     pooled A >= 18 (share >= 0.60) and A modal; re-baseline at 6
     consecutive AWAY blocks (18 days); a HOME block resets.

METRICS per scenario x model x rule (REPS reps, fixed seeds):
  rebl   P(re-baseline within 60 days); day = median day when it happens
  close  P(closed as alternation within 60 days) (C rules only)
  rev30  P(re-baseline AND the true state is home on some day within 30
         days after it): the haiku-style reversal.
A closing CHECK prints the exact R1 probabilities under S1 and W3, which
the simulated R1 and C1 rows must match.
"""
import os
import json
import random
from math import comb, lgamma, exp

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
COUNTS = os.path.join(REPO, "probe", "monitor", "derived",
                      "daily_counts.jsonl")
MODEL, ITEM, CUTOFF = "gpt-5.6-terra", "eq_disclosure_timing", "2026-10-15"
REPS, SEED, HORIZON, N = 20000, 20261018, 60, 18
RULES = ["R1", "C1", "R2", "C2", "W", "B3"]
KS = list(range(11))


def load_pools(path):
    rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    a = {x["date"]: x["counts"].get("A", 0) for x in rows
         if x["model"] == MODEL and x["item_id"] == ITEM
         and x["phase"] == "monitor_probe" and x["date"] <= CUTOFF}
    home = [v for d, v in sorted(a.items()) if d <= "2026-10-08"]
    away = [v for d, v in sorted(a.items()) if d >= "2026-10-09"]
    assert len(away) == 5 and len(home) == 64, (len(home), len(away))
    return home, away


def away_models(away):
    m = sum(away) / 50
    mean = sum(away) / 5
    var = sum((x - mean) ** 2 for x in away) / 4
    # beta-binomial MoM: var = n p q (1 + (n-1) rho)
    rho = max(1e-6, (var / (10 * m * (1 - m)) - 1) / 9)
    ab = (1 - rho) / rho
    alpha, beta = m * ab, (1 - m) * ab

    def lb(x, y):
        return lgamma(x) + lgamma(y) - lgamma(x + y)

    pmf = {
        "W1": [away.count(k) / 5 for k in KS],
        "W2": [comb(10, k) * exp(lb(k + alpha, 10 - k + beta) - lb(alpha, beta))
               for k in KS],
        "W3": [comb(10, k) * m ** k * (1 - m) ** (10 - k) for k in KS],
    }
    return pmf, (m, var, rho, alpha, beta)


def geom(rng, mean_len):
    p = 1 / mean_len
    k = 1
    while rng.random() >= p:
        k += 1
    return k


def truth(rng, scen):
    """1 = away state, 0 = home state, one entry per observed day."""
    if scen == "S1":
        return [1] * HORIZON
    if scen == "S3":
        k = geom(rng, 3)
        return ([1] * k + [0] * HORIZON)[:HORIZON + 30]
    away_mean = 10 if scen == "S2a" else 20
    s, st = [1] * geom(rng, away_mean), 1
    while len(s) < HORIZON + 30:
        st = 1 - st
        s += [st] * geom(rng, 7 if st == 0 else away_mean)
    return s[:HORIZON + 30]


def run_rule(rule, home):
    """home: one bool per observed day. Returns (outcome, day)."""
    if rule == "W":
        for d in range(N, HORIZON + 1):
            if sum(not h for h in home[d - N:d]) >= 16:
                return ("rebl", d)
        return ("none", None)
    cnt, prev_home = 0, False
    for d in range(1, HORIZON + 1):
        h = home[d - 1]
        if rule in ("R1", "C1"):
            if h:
                if rule == "C1":
                    return ("close", d)
                cnt = 0
            else:
                cnt += 1
        else:  # R2, C2
            if h and prev_home:
                if rule == "C2":
                    return ("close", d)
                cnt = 0
            elif not h:
                cnt += 1
            prev_home = h
        if cnt >= N:
            return ("rebl", d)
    return ("none", None)


def run_b3(counts):
    cnt = 0
    for b in range(HORIZON // 3):
        a = sum(counts[3 * b:3 * b + 3])
        block_home = a >= 18 and a > 30 - a   # share >= .60 and A modal
        cnt = 0 if block_home else cnt + 1
        if cnt >= 6:
            return ("rebl", 3 * b + 3)
    return ("none", None)


def main():
    home_pool, away_pool = load_pools(COUNTS)
    pmf, (m, var, rho, alpha, beta) = away_models(away_pool)
    home_pmf = [home_pool.count(k) / len(home_pool) for k in KS]
    for v in list(pmf.values()) + [home_pmf]:
        assert abs(sum(v) - 1) < 1e-9

    print(f"home pool n={len(home_pool)}  P(HOME day | home regime) = "
          f"{sum(v >= 6 for v in home_pool) / len(home_pool):.3f}")
    print(f"away pool {away_pool}  share={m:.3f}  var={var:.2f}  "
          f"rho={rho:.3f}  beta({alpha:.2f},{beta:.2f})")
    for model in ["W1", "W2", "W3"]:
        print(f"  {model}: P(HOME day | away state) = {sum(pmf[model][6:]):.4f}")
    print()
    print(f"{'scen':4} {'model':5} {'rule':4} {'rebl':>6} {'day':>4} "
          f"{'close':>6} {'rev30':>6}")
    for scen in ["S1", "S2a", "S2b", "S3"]:
        for model in ["W1", "W2", "W3"]:
            res = {r: [0, [], 0, 0] for r in RULES}
            rng = random.Random(f"{SEED}:{scen}:{model}")
            for _ in range(REPS):
                st = truth(rng, scen)
                aw = rng.choices(KS, pmf[model], k=len(st))
                hm = rng.choices(KS, home_pmf, k=len(st))
                counts = [aw[i] if s else hm[i] for i, s in enumerate(st)]
                home = [c >= 6 for c in counts[:HORIZON]]
                for r in RULES:
                    kind, day = (run_b3(counts) if r == "B3"
                                 else run_rule(r, home))
                    if kind == "rebl":
                        res[r][0] += 1
                        res[r][1].append(day)
                        if 0 in st[day:day + 30]:
                            res[r][3] += 1
                    elif kind == "close":
                        res[r][2] += 1
            for r in RULES:
                n_rb, days, n_cl, n_rev = res[r]
                med = sorted(days)[len(days) // 2] if days else "-"
                print(f"{scen:4} {model:5} {r:4} {n_rb / REPS:6.3f} "
                      f"{med!s:>4} {n_cl / REPS:6.3f} {n_rev / REPS:6.3f}")
        print()

    # Exact cross-check: R1 under S1 and W3 has i.i.d. HOME days, so
    # P(first 18 days all AWAY) = (1 - q)^18, and P(re-baseline within 60)
    # follows from a DP over the current AWAY run length.
    q = sum(pmf["W3"][6:])
    print(f"CHECK R1/S1/W3: analytic P(first 18 days all AWAY) = "
          f"{(1 - q) ** 18:.3f}")
    dp = [1.0] + [0.0] * (N - 1)
    hit = 0.0
    for _ in range(HORIZON):
        new = [0.0] * N
        for k, pr in enumerate(dp):
            new[0] += pr * q
            if k + 1 == N:
                hit += pr * (1 - q)
            else:
                new[k + 1] += pr * (1 - q)
        dp = new
    print(f"CHECK R1/S1/W3: analytic P(re-baseline within 60) = {hit:.3f}")


if __name__ == "__main__":
    main()
