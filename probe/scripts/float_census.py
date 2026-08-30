"""Float-versus-exact census of every gate decision in the record.

Every quantity the monitor compares is a rational on a fixed
lattice: TVD between count vectors a (n_a parsed) and b (n_b
parsed) equals sum|n_b*a_i - n_a*b_i| / (2*n_a*n_b), an integer
over a known denominator, and a band p99 is an order statistic of
such values. The monitor compares them as floats, and the float a
rational becomes depends on the summation path, so identical
rationals can decide differently (0.45000000000000007 > 0.45 on
one vector, 0.45 == 0.45 on another). This script recomputes every
historical gate BOTH ways and reports the difference. It changes
nothing: monitor.py stays byte-constant, the verdict log is never
rescored, and the census is the deciding read for the dated
float-comparison policy (probe/DRIFT_WINDOW_2026-08-14_to_30.md,
open items).

Method:
1. Replicate the float path bit for bit: bands re-simulated from
   the stored seeds with the monitor's arithmetic, breach and
   rerun gates re-applied. HARD-FAIL unless the replication
   reproduces the stored band p99s, the recorded breach sets, the
   recorded observed TVDs, and the recorded item verdicts exactly.
   Only a bit-faithful float side makes the delta trustworthy.
2. Run the same simulated draws and the same gates in exact
   integer arithmetic (numerator comparison by cross
   multiplication; no epsilon anywhere), including exact band
   order statistics at the same index convention.
3. Report: breaches that exist only under floats, breaches missed
   only under floats, item verdicts that change where a breach
   survives both, day verdicts that change, and the expected
   false-breach null (probe/scripts/expected_false_breaches.py
   method) under both semantics, since the null shares the
   monitor's float comparison and must move with it.

Supersession-aware: each day is scored against the reference in
force on that day (a superseded reference governs through its
valid_through date). Deterministic, offline, committed inputs only.

  python probe/scripts/float_census.py
"""
import os
import sys
import json
import glob
import random
import collections
from math import comb

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
MONITOR = os.path.join(REPO, "probe", "monitor")
OPTIONS = ("A", "B", "C", "D")
K = 10
SIMS = 10000
SMOOTH = 1.0
SEVERITY = {"TRANSIENT": 1, "UNSTABLE": 2, "EVENT": 3}


def tvd_float(a, b):
    """The monitor's float TVD, same op order (OPTIONS order)."""
    na, nb = sum(a.values()), sum(b.values())
    return 0.5 * sum(abs(a.get(o, 0) / na - b.get(o, 0) / nb)
                     for o in OPTIONS)


def tvd_exact(a, b):
    """(num, den) with TVD = num/den exactly; den = 2*na*nb."""
    na, nb = sum(a.values()), sum(b.values())
    num = sum(abs(nb * a.get(o, 0) - na * b.get(o, 0)) for o in OPTIONS)
    return num, 2 * na * nb


def gt(x, y):
    """Exact x > y for (num, den) rationals."""
    return x[0] * y[1] > y[0] * x[1]


def le(x, y):
    return not gt(x, y)


def bands_both(counts, seed, k=K, sims=SIMS, smooth=SMOOTH):
    """(float_p99, exact_p99) from ONE draw sequence.

    Replicates monitor.smoothed_bands draw for draw (same seed rule,
    same rng consumption, same float arithmetic for the float side)
    while also scoring each draw exactly; both sides take the order
    statistic at the same index, so the exact band is the same
    procedure with only the comparison arithmetic changed.
    """
    n = sum(counts.values())
    probs = [(counts.get(o, 0) + smooth) / (n + smooth * len(OPTIONS))
             for o in OPTIONS]
    rng = random.Random(seed)
    floats, nums = [], []
    for _ in range(sims):
        draw = collections.Counter(rng.choices(OPTIONS, weights=probs,
                                               k=k))
        floats.append(tvd_float(counts, draw))
        nums.append(tvd_exact(counts, draw)[0])
    floats.sort()
    nums.sort()
    i99 = int(0.99 * sims) - 1
    return floats[i99], (nums[i99], 2 * n * k)


def load():
    verdicts = [json.loads(l) for l in
                open(os.path.join(MONITOR, "verdicts.jsonl"),
                     encoding="utf-8")]
    daily = {"monitor_probe": {}, "monitor_rerun": {}}
    path = os.path.join(MONITOR, "derived", "daily_counts.jsonl")
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        if r["phase"] in daily:
            daily[r["phase"]][(r["date"], r["model"],
                              r["item_id"])] = r["counts"]
    baselines = {}
    for p in sorted(glob.glob(os.path.join(MONITOR, "baselines",
                                           "*.json"))):
        b = json.load(open(p, encoding="utf-8"))
        baselines[b["model"]] = b["items"]
    return verdicts, daily, baselines


def ref_for(rec, date):
    for old in rec.get("superseded", []):
        if old["valid_from"] <= date <= old["valid_through"]:
            return old
    return rec


def main():
    verdicts, daily, baselines = load()
    band_cache = {}

    def bands(counts, seed):
        key = (seed, tuple(sorted(counts.items())))
        if key not in band_cache:
            band_cache[key] = bands_both(counts, seed)
        return band_cache[key]

    replication_errors = []
    float_only, exact_only, verdict_flips, day_flips = [], [], [], []
    checked_days = checked_gates = 0

    for v in verdicts:
        if v["verdict"] in ("ERROR", "ECHO_CHANGE"):
            continue
        date, model = v["date"], v["model"]
        recorded = {b["item_id"]: b for b in v["breached"]}
        checked_days += 1
        exact_day = []
        for iid, rec0 in baselines[model].items():
            rec = ref_for(rec0, date)
            probe = daily["monitor_probe"].get((date, model, iid))
            if probe is None:
                replication_errors.append(
                    "missing probe counts %s %s %s" % (date, model, iid))
                continue
            base = rec["baseline_counts"]
            t_f = tvd_float(base, probe)
            f_breach = t_f > rec["band"]["p99"]
            checked_gates += 1
            if f_breach != (iid in recorded):
                replication_errors.append(
                    "breach bit mismatch %s %s %s: replicated %s, "
                    "recorded %s" % (date, model, iid, f_breach,
                                     iid in recorded))
                continue
            if f_breach and recorded[iid]["observed_tvd"] != t_f:
                replication_errors.append(
                    "tvd mismatch %s %s %s" % (date, model, iid))
            band_f, band_e = bands(base, rec["band"]["seed"])
            if band_f != rec["band"]["p99"]:
                replication_errors.append(
                    "band mismatch %s %s: recomputed %r stored %r" % (
                        model, iid, band_f, rec["band"]["p99"]))
                continue
            e_breach = gt(tvd_exact(base, probe), band_e)
            slot = "%s %s %s" % (date, model.split("-")[0], iid)
            if f_breach and not e_breach:
                float_only.append("%s (float tvd %r, band %r; exact "
                                  "equality)" % (slot, t_f,
                                                 rec["band"]["p99"]))
            if e_breach and not f_breach:
                exact_only.append(slot)
            if not f_breach:
                if e_breach:
                    exact_day.append((iid, None))
                continue

            # verdict gate for breaches that survive both semantics
            rb = recorded[iid]
            rerun = daily["monitor_rerun"].get((date, model, iid))
            if rerun is None:
                replication_errors.append(
                    "missing rerun counts %s %s %s" % (date, model, iid))
                continue
            pband_f, pband_e = bands(probe, rb["rerun_probe_seed"])
            if pband_f != rb["rerun_probe_p99"]:
                replication_errors.append(
                    "rerun band mismatch %s %s %s" % (date, model, iid))
                continue
            t_probe_f = tvd_float(probe, rerun)
            t_base_f = tvd_float(base, rerun)
            fv = ("EVENT" if t_probe_f <= pband_f
                  and not t_base_f <= rec["band"]["p99"]
                  else "TRANSIENT" if t_base_f <= rec["band"]["p99"]
                  else "UNSTABLE")
            if fv != rb["item_verdict"]:
                replication_errors.append(
                    "verdict mismatch %s %s %s: replicated %s recorded "
                    "%s" % (date, model, iid, fv, rb["item_verdict"]))
                continue
            if e_breach:
                mp = le(tvd_exact(probe, rerun), pband_e)
                mb = le(tvd_exact(base, rerun), band_e)
                ev = ("EVENT" if mp and not mb
                      else "TRANSIENT" if mb else "UNSTABLE")
                exact_day.append((iid, ev))
                if ev != rb["item_verdict"]:
                    verdict_flips.append("%s: %s -> %s" % (
                        slot, rb["item_verdict"], ev))
        exact_worst = max((SEVERITY[ev] for _, ev in exact_day
                           if ev is not None), default=0)
        exact_verdict = ("CLEAN" if not exact_day else
                         "UNKNOWN(new breach, no rerun ran)"
                         if any(ev is None for _, ev in exact_day)
                         and exact_worst == 0 else
                         [k for k, s in SEVERITY.items()
                          if s == exact_worst][0] if exact_worst else
                         "UNKNOWN(new breach, no rerun ran)")
        if exact_verdict != v["verdict"]:
            day_flips.append("%s %s: %s -> %s" % (
                date, model.split("-")[0], v["verdict"], exact_verdict))

    print("gates checked: %d slot-days over %d model-days" % (
        checked_gates, checked_days))
    if replication_errors:
        print("\nREPLICATION FAILED (%d); the census is not valid:" %
              len(replication_errors))
        for e in replication_errors[:20]:
            print("  ", e)
        raise SystemExit(2)
    print("float replication: bit-faithful (bands, breach bits, TVDs, "
          "verdicts all reproduce the record)")

    print("\nbreaches that exist only under floats (exact says "
          "at-band, not over): %d" % len(float_only))
    for s in float_only:
        print("  ", s)
    print("breaches missed only under floats: %d" % len(exact_only))
    for s in exact_only:
        print("  ", s)
    print("item-verdict flips where the breach survives both: %d" %
          len(verdict_flips))
    for s in verdict_flips:
        print("  ", s)
    print("day-verdict changes under exact semantics: %d" %
          len(day_flips))
    for s in day_flips:
        print("  ", s)

    # the null, both truths x both semantics, current active references
    print("\nexpected false breaches per day "
          "(expected_false_breaches.py method):")
    for truth in ("smoothed", "empirical"):
        tot_f = tot_e = 0.0
        for model, items in baselines.items():
            for iid, rec in items.items():
                base = rec["baseline_counts"]
                n = sum(base.values())
                if truth == "smoothed":
                    probs = [(base.get(o, 0) + SMOOTH)
                             / (n + SMOOTH * len(OPTIONS))
                             for o in OPTIONS]
                else:
                    probs = [base.get(o, 0) / n for o in OPTIONS]
                _, band_e = bands(base, rec["band"]["seed"])
                for a in range(K + 1):
                    for b2 in range(K + 1 - a):
                        for c in range(K + 1 - a - b2):
                            d = K - a - b2 - c
                            compv = {"A": a, "B": b2, "C": c, "D": d}
                            w = (comb(K, a) * comb(K - a, b2)
                                 * comb(K - a - b2, c)
                                 * probs[0] ** a * probs[1] ** b2
                                 * probs[2] ** c * probs[3] ** d)
                            if tvd_float(base, compv) > rec["band"]["p99"]:
                                tot_f += w
                            if gt(tvd_exact(base, compv), band_e):
                                tot_e += w
        print("  truth=%-9s float %.4f   exact %.4f" % (
            truth, tot_f, tot_e))


if __name__ == "__main__":
    main()
