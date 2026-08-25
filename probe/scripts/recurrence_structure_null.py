"""Null significance of the breach recurrence structure in the
drift-monitor record.

Standalone reproduction of the null-structure analysis whose figures
were adversarially verified on 2026-08-13 by independent
recomputation. Reads only committed inputs: the qualified baselines
(probe/monitor/baselines/*.json), the verdict log
(probe/monitor/verdicts.jsonl), and the derived per-item daily counts
(probe/monitor/derived/daily_counts.jsonl). Nothing else is touched.

Observed side, from the verdict log inside the analysis window:
breach entries and how many sit on eq_ items, distinct breached slots
(a slot is one model x item pair), slots with >= 2 / 3 / 5 breaches,
item-verdict tallies, items with EVENT verdicts on two or more
models, and per-thread direction. The direction of one breach is the
option whose probe share gains most over the baseline share, ties
resolved to the earliest option in A..D order; a repeat thread is
unidirectional when every breach in it points at the same option.
Probe compositions come from the derived daily counts.

Null side, exact (no sampling). The generating truth per slot is the
Laplace-smoothed baseline (c+1)/(n+4), the same prior the committed
bands are built on. Per-slot daily breach probability p_i: enumerate
all 286 compositions of K=10 draws into the four options, weight
each by its multinomial probability under the smoothed truth, score
the monitor TVD (0.5 * sum |c/20 - k/10|, A..D order, each side over
its own total) against the empirical pooled baseline, and sum the
mass strictly above the committed band p99. Same construction as
expected_false_breaches.py. Recurrence: each slot breaches
Binomial(days, p_i) times; expected slot counts at each threshold
and exact tails for the number of such slots via Poisson-binomial
dynamic programming. Count-calibrated sensitivity: scale every p_i
by one factor so the null expectation matches the observed entry
total, then recompute the tails; this concedes the observed rate and
asks only about the clustering. Concentration: the eq_ share of null
breach mass and the chance that every entry (and every distinct
breached slot) lands on an eq_ item. Direction: the same enumeration
gives each slot a conditional direction distribution given a breach;
from it the pooled P(3 of 3 same direction), the expected number of
slots with >= 3 (or >= 5) breaches all in one direction, and exact
tails at the observed counts.

Out of scope: the two-stage EVENT/TRANSIENT disambiguation null
(rerun bands and the Monte Carlo cross-check) is not ported and
stays in the analysis lane. Only the item_verdict labels already
recorded in the verdict log are tallied here.

Re-baselined items. An item record rewritten by
probe/scripts/rebaseline_item.py carries its prior references under
"superseded", each with a pinned validity window: a superseded
reference governs THROUGH its valid_through day, the next reference
from the day after (probe/REBASELINE_DECISION_2026-08-23.md). Both
sides of this analysis honor that convention. Observed directions
score each breach against the reference in force on its date, and
the null treats every slot as a sequence of reference epochs: each
epoch contributes Binomial(days_in_epoch, p_epoch) breaches, slot
totals are exact convolutions across epochs, and direction masses
are epoch-specific. No historical day is ever scored against a
reference that was not in force when it ran. For records without
supersession all of this reduces to the single-reference arithmetic.
"sum p_i per day" is reported as expected entries divided by window
days, which equals the plain per-day sum whenever every model has a
verdict line on every window day.

The analysis window defaults to the full record and matters because
the record extends past the validated window. --selfcheck pins the
window to 2026-08-02..2026-08-13 and asserts every adversarially
verified figure, so future refactors can be checked in one command.
The validated window predates the first re-baseline, so its pinned
figures are unchanged by the epoch routing.

Run: python probe/scripts/recurrence_structure_null.py
       [--start 2026-08-02] [--end 2026-08-13] [--selfcheck]
"""
import argparse
import collections
import datetime
import glob
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
MONITOR = os.path.join(HERE, os.pardir, "monitor")
BASELINE_DIR = os.path.join(MONITOR, "baselines")
VERDICT_LOG = os.path.join(MONITOR, "verdicts.jsonl")
DAILY_COUNTS = os.path.join(MONITOR, "derived", "daily_counts.jsonl")
OPTIONS = ("A", "B", "C", "D")
K = 10

SELFCHECK_START = "2026-08-02"
SELFCHECK_END = "2026-08-13"

# Adversarially verified figures for the validated window. The float
# tolerance is half a unit in the last quoted digit.
PINNED_INTS = (
    ("obs_entries", 29),
    ("obs_eq_entries", 29),
    ("obs_distinct_slots", 13),
    ("obs_slots_ge2", 7),
    ("obs_slots_ge3", 5),
    ("obs_slots_ge5", 2),
    ("obs_event_entries", 18),
    ("obs_transient_entries", 11),
    ("obs_threads_ge3", 5),
    ("obs_threads_ge3_same_dir", 5),
    ("obs_threads_ge5_same_dir", 2),
    ("obs_cross_model_event_items", 2),
)
PINNED_FLOATS = (
    ("sum_p_per_day", 1.642407, 5e-7),
    ("e_total_entries", 19.709, 5e-4),
    ("p_total_ge_obs", 0.02901, 5e-6),
    ("e_distinct_slots", 19.16, 5e-3),
    ("e_slots_ge2", 0.5368, 5e-5),
    ("e_slots_ge3", 0.010088, 5e-7),
    ("e_slots_ge5", 1.722e-6, 5e-10),
    ("p_nslots_ge2_tail", 1.480e-6, 5e-10),
    ("p_nslots_ge3_tail", 7.978e-13, 5e-16),
    ("p_nslots_ge5_tail", 1.439e-12, 5e-16),
    ("calib_factor", 1.4714, 5e-5),
    ("calib_p_nslots_ge2_tail", 1.753e-4, 5e-8),
    ("calib_p_nslots_ge3_tail", 2.326e-10, 5e-14),
    ("calib_p_nslots_ge5_tail", 6.543e-11, 5e-15),
    ("eq_share", 0.38149, 5e-6),
    ("p_all_entries_eq", 7.296e-13, 5e-16),
    ("p_all_distinct_eq", 3.625e-6, 5e-10),
    ("pooled_same_dir_3of3", 0.155, 5e-4),
    ("pooled_tie_mass", 0.2999, 5e-5),
    ("e_slots_ge3_same_dir", 0.001796, 5e-7),
    ("p_nslots_ge3_same_tail", 1.348e-16, 5e-20),
    ("p_any_slot_ge5_same_dir", 1.204e-7, 5e-11),
    ("p_nslots_ge5_same_tail", 6.773e-15, 5e-19),
)


def compositions(k, parts):
    """Every way to split k draws across parts options."""
    if parts == 1:
        yield (k,)
        return
    for i in range(k + 1):
        for rest in compositions(k - i, parts - 1):
            yield (i,) + rest


COMPS = tuple(compositions(K, len(OPTIONS)))  # 286 at K=10
LOG_FACT = [math.lgamma(i + 1) for i in range(K + 1)]
LOG_K_FACT = math.lgamma(K + 1)


def comp_probs(truth):
    """Multinomial probability of every composition under truth. All
    components positive, which the smoothed truth guarantees."""
    lt = [math.log(t) for t in truth]
    out = []
    for comp in COMPS:
        lp = LOG_K_FACT
        for ci, li in zip(comp, lt):
            lp += ci * li - LOG_FACT[ci]
        out.append(math.exp(lp))
    return out


def binom_pmf(n, p):
    return [math.comb(n, m) * (p ** m) * ((1 - p) ** (n - m))
            for m in range(n + 1)]


def bernoulli_sum_dist(ps, cap):
    """Distribution of a sum of independent Bernoulli(p_i), truncated
    at cap with the excess mass lumped into the cap bin. Tails at
    thresholds <= cap stay exact."""
    dist = [1.0] + [0.0] * cap
    for p in ps:
        if p == 0.0:
            continue
        new = [0.0] * (cap + 1)
        for tot in range(cap + 1):
            d = dist[tot]
            if d == 0.0:
                continue
            new[min(tot + 1, cap)] += d * p
            new[tot] += d * (1 - p)
        dist = new
    return dist


def binom_sum_dist(pairs, cap):
    """Distribution of a sum of independent Binomial(n_i, p_i) over
    (n_i, p_i) pairs, truncated at cap as above."""
    dist = [1.0] + [0.0] * cap
    for n, p in pairs:
        if p == 0.0 or n == 0:
            continue
        pmf = binom_pmf(n, p)
        new = [0.0] * (cap + 1)
        for tot in range(cap + 1):
            d = dist[tot]
            if d == 0.0:
                continue
            for m, q in enumerate(pmf):
                if q == 0.0:
                    continue
                new[min(tot + m, cap)] += d * q
        dist = new
    return dist


def tail_ge(dist, m):
    return sum(dist[m:])


def ref_epochs(rec):
    """Reference epochs of one item record, oldest first: every
    superseded reference with its pinned validity window, then the
    active reference, open ended. Records without supersession yield
    the single active epoch."""
    eps = []
    for old in rec.get("superseded", []):
        eps.append({"src": old, "from": old["valid_from"],
                    "through": old["valid_through"]})
    eps.append({"src": rec, "from": rec.get("valid_from"),
                "through": None})
    for ep in eps:
        src = ep["src"]
        ep["base"] = [src["baseline_counts"].get(o, 0)
                      for o in OPTIONS]
        ep["n"] = src["n"]
        ep["p99"] = src["band"]["p99"]
        del ep["src"]
    return eps


def epoch_for(slot, date):
    """The reference epoch in force on a date: the superseded epoch
    whose validity window holds it, else the active one. Mirrors
    paper/figures/figdata.baseline_for."""
    for ep in slot["epochs"][:-1]:
        if ep["from"] <= date <= ep["through"]:
            return ep
    return slot["epochs"][-1]


def load_slots():
    paths = sorted(glob.glob(os.path.join(BASELINE_DIR, "*.json")))
    if not paths:
        raise SystemExit("no baseline files under %s" % BASELINE_DIR)
    slots = []
    for path in paths:
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
        if doc["k"] != K:
            raise SystemExit(
                "baseline %s was qualified at k=%s but this script "
                "assumes K=%d; bands and draws must share one K"
                % (os.path.basename(path), doc["k"], K))
        for iid in sorted(doc["items"]):
            rec = doc["items"][iid]
            if rec["class"] != "alarm":
                continue
            slots.append({
                "model": doc["model"], "iid": iid,
                "epochs": ref_epochs(rec),
                "eq": iid.startswith("eq_")})
    return slots


def load_verdict_lines():
    out = []
    with open(VERDICT_LOG, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    if not out:
        raise SystemExit("no verdict lines in %s" % VERDICT_LOG)
    return out


def load_probe_counts():
    """(date, model, item_id) -> parsed option counts of the daily
    probe, from the committed derived daily counts."""
    out = {}
    with open(DAILY_COUNTS, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec["phase"] != "monitor_probe":
                continue
            key = (rec["date"], rec["model"], rec["item_id"])
            out[key] = rec["counts"]
    return out


def epoch_null(ep):
    """Attach exact null quantities to one reference epoch: the daily
    breach probability p, and the conditional direction distribution
    and tie mass given a breach. Direction of a breaching composition
    is the option with the largest share gain over the baseline, ties
    resolved to the earliest option in A..D order (the tie mass is
    tracked separately)."""
    n = ep["n"]
    base_share = [b / n for b in ep["base"]]
    w = comp_probs([(b + 1.0) / (n + 4.0) for b in ep["base"]])
    p99 = ep["p99"]
    p = 0.0
    dvec = [0.0, 0.0, 0.0, 0.0]
    tie = 0.0
    for j, comp in enumerate(COMPS):
        t = 0.5 * sum(abs(bs - c / K)
                      for bs, c in zip(base_share, comp))
        if not (t > p99):
            continue
        wj = w[j]
        p += wj
        gains = [comp[o] / K - base_share[o] for o in range(4)]
        g = max(gains)
        idxs = [o for o in range(4) if gains[o] == g]
        if len(idxs) > 1:
            tie += wj
        dvec[idxs[0]] += wj
    ep["p"] = p
    ep["dir_cond"] = ([x / p for x in dvec] if p > 0
                      else [0.25] * 4)
    ep["tie_cond"] = tie / p if p > 0 else 0.0


def slot_count_pmf(slot, infl=1.0):
    """Exact pmf of the slot's window breach count: the convolution
    of Binomial(days_in_epoch, p_epoch) across reference epochs,
    optionally with every epoch probability inflated by infl."""
    nd = sum(ep["days"] for ep in slot["epochs"])
    if nd == 0:
        return [1.0]
    return binom_sum_dist(
        [(ep["days"], min(ep["p"] * infl, 1.0))
         for ep in slot["epochs"]], nd)


def slot_same_dir_ge(slot, thr):
    """P(the slot collects at least thr breaches in the window and
    every one points at the same option), exact across reference
    epochs. Within an epoch each breach independently points at
    option o with the epoch's conditional direction mass; across
    epochs the all-point-at-o counts convolve. The single-epoch case
    reduces to sum_m pmf[m] * sum_o dir[o]^m over m >= thr, the
    original arithmetic."""
    if sum(ep["days"] for ep in slot["epochs"]) < thr:
        return 0.0
    total = 0.0
    for o in range(4):
        dist = [1.0]
        for ep in slot["epochs"]:
            if ep["days"] == 0:
                continue
            pmf = binom_pmf(ep["days"], ep["p"])
            f = [pmf[m] * ep["dir_cond"][o] ** m
                 for m in range(len(pmf))]
            new = [0.0] * (len(dist) + len(f) - 1)
            for i, di in enumerate(dist):
                if di == 0.0:
                    continue
                for j, fj in enumerate(f):
                    new[i + j] += di * fj
            dist = new
        total += sum(dist[thr:])
    return total


def entry_direction(slot, counts, date):
    """Index in OPTIONS of the max-share-gain option of one observed
    probe against the reference in force on its date, ties to the
    earliest option."""
    total = sum(counts.values())
    if total == 0:
        raise SystemExit("empty probe counts for %s %s"
                         % (slot["model"], slot["iid"]))
    ep = epoch_for(slot, date)
    gains = [counts.get(o, 0) / total - b / ep["n"]
             for o, b in zip(OPTIONS, ep["base"])]
    return gains.index(max(gains))


def observed_structure(in_window, slot_map, probe_map):
    entries = []
    for v in in_window:
        for b in v.get("breached", []):
            entries.append({"date": v["date"], "model": v["model"],
                            "iid": b["item_id"],
                            "verdict": b.get("item_verdict")})
    for e in entries:
        key = (e["model"], e["iid"])
        if key not in slot_map:
            raise SystemExit("breach entry on unknown slot %s %s"
                             % key)
        pkey = (e["date"], e["model"], e["iid"])
        if pkey not in probe_map:
            raise SystemExit("no derived probe counts for breach "
                             "entry %s %s %s" % pkey)
        e["dir"] = entry_direction(slot_map[key], probe_map[pkey],
                                   e["date"])

    per_slot = collections.Counter(
        (e["model"], e["iid"]) for e in entries)
    verdicts = collections.Counter(e["verdict"] for e in entries)
    ev_models = collections.defaultdict(set)
    for e in entries:
        if e["verdict"] == "EVENT":
            ev_models[e["iid"]].add(e["model"])

    def thread_stats(thr):
        total = same = 0
        for key, c in per_slot.items():
            if c < thr:
                continue
            total += 1
            dirs = set(e["dir"] for e in entries
                       if (e["model"], e["iid"]) == key)
            if len(dirs) == 1:
                same += 1
        return total, same

    t3, s3 = thread_stats(3)
    t5, s5 = thread_stats(5)
    return {
        "obs_entries": len(entries),
        "obs_eq_entries": sum(1 for e in entries
                              if e["iid"].startswith("eq_")),
        "obs_distinct_slots": len(per_slot),
        "obs_slots_ge2": sum(1 for c in per_slot.values() if c >= 2),
        "obs_slots_ge3": sum(1 for c in per_slot.values() if c >= 3),
        "obs_slots_ge5": sum(1 for c in per_slot.values() if c >= 5),
        "obs_max_thread": (max(per_slot.values()) if per_slot else 0),
        "obs_event_entries": verdicts.get("EVENT", 0),
        "obs_transient_entries": verdicts.get("TRANSIENT", 0),
        "obs_unstable_entries": verdicts.get("UNSTABLE", 0),
        "obs_threads_ge3": t3,
        "obs_threads_ge3_same_dir": s3,
        "obs_threads_ge5": t5,
        "obs_threads_ge5_same_dir": s5,
        "obs_cross_model_event_items": sum(
            1 for ms in ev_models.values() if len(ms) >= 2),
    }


def analyze(start, end):
    lines = load_verdict_lines()
    all_dates = sorted(set(v["date"] for v in lines))
    if start is None:
        start = all_dates[0]
    if end is None:
        end = all_dates[-1]
    if end < start:
        raise SystemExit("--end is before --start")
    in_window = [v for v in lines if start <= v["date"] <= end]
    if not in_window:
        raise SystemExit(
            "no verdict lines in %s..%s (the record covers %s..%s)"
            % (start, end, all_dates[0], all_dates[-1]))
    dates = sorted(set(v["date"] for v in in_window))
    dates_by_model = collections.defaultdict(set)
    for v in in_window:
        dates_by_model[v["model"]].add(v["date"])

    slots = load_slots()
    slot_map = {(s["model"], s["iid"]): s for s in slots}
    for m in dates_by_model:
        if not any(s["model"] == m for s in slots):
            raise SystemExit("verdict model %s has no baseline" % m)

    figs = {"start": start, "end": end, "n_days": len(dates),
            "record_start": all_dates[0],
            "record_end": all_dates[-1],
            "record_days": len(all_dates), "n_slots": len(slots),
            "eq_slots": sum(1 for s in slots if s["eq"])}
    figs.update(observed_structure(in_window, slot_map,
                                   load_probe_counts()))

    for s in slots:
        model_dates = dates_by_model.get(s["model"], set())
        for ep in s["epochs"]:
            epoch_null(ep)
            ep["days"] = sum(1 for d in model_dates
                             if epoch_for(s, d) is ep)

    def slot_mass(s):
        return sum(ep["days"] * ep["p"] for ep in s["epochs"])

    total_mass = sum(slot_mass(s) for s in slots)
    figs["e_total_entries"] = total_mass
    figs["sum_p_per_day"] = total_mass / len(dates)
    figs["e_distinct_slots"] = 0.0
    for s in slots:
        p_never = 1.0
        for ep in s["epochs"]:
            p_never *= (1 - ep["p"]) ** ep["days"]
        figs["e_distinct_slots"] += 1 - p_never
    figs["eq_share"] = sum(slot_mass(s) for s in slots
                           if s["eq"]) / total_mass
    figs["p_all_entries_eq"] = (
        figs["eq_share"] ** figs["obs_entries"])
    figs["p_all_distinct_eq"] = (
        figs["eq_share"] ** figs["obs_distinct_slots"])

    cap_total = max(80, figs["obs_entries"] + 20)
    dist = binom_sum_dist([(ep["days"], ep["p"]) for s in slots
                           for ep in s["epochs"]], cap_total)
    figs["p_total_ge_obs"] = tail_ge(dist, figs["obs_entries"])

    cap_slots = max(15, figs["obs_slots_ge2"] + 5)
    for thr in (2, 3, 5):
        qs = [tail_ge(slot_count_pmf(s), thr) for s in slots]
        figs["e_slots_ge%d" % thr] = sum(qs)
        figs["p_nslots_ge%d_tail" % thr] = tail_ge(
            bernoulli_sum_dist(qs, cap_slots),
            figs["obs_slots_ge%d" % thr])

    if figs["obs_entries"] > 0 and figs["e_total_entries"] > 0:
        infl = figs["obs_entries"] / figs["e_total_entries"]
        figs["calib_factor"] = infl
        for thr in (2, 3, 5):
            qs = [tail_ge(slot_count_pmf(s, infl), thr)
                  for s in slots]
            figs["calib_e_slots_ge%d" % thr] = sum(qs)
            figs["calib_p_nslots_ge%d_tail" % thr] = tail_ge(
                bernoulli_sum_dist(qs, cap_slots),
                figs["obs_slots_ge%d" % thr])
    else:
        figs["calib_factor"] = None

    figs["pooled_same_dir_3of3"] = sum(
        ep["days"] * ep["p"] * sum(x ** 3 for x in ep["dir_cond"])
        for s in slots for ep in s["epochs"]) / total_mass
    figs["pooled_tie_mass"] = sum(
        ep["days"] * ep["p"] * ep["tie_cond"]
        for s in slots for ep in s["epochs"]) / total_mass
    for thr, obs_key in ((3, "obs_threads_ge3_same_dir"),
                         (5, "obs_threads_ge5_same_dir")):
        qs = [slot_same_dir_ge(s, thr) for s in slots]
        figs["e_slots_ge%d_same_dir" % thr] = sum(qs)
        p_none = 1.0
        for q in qs:
            p_none *= (1 - q)
        figs["p_any_slot_ge%d_same_dir" % thr] = 1 - p_none
        figs["p_nslots_ge%d_same_tail" % thr] = tail_ge(
            bernoulli_sum_dist(qs, cap_slots), figs[obs_key])
    return figs


def report(figs):
    print("window %s..%s, %d probe days (record %s..%s, %d days)"
          % (figs["start"], figs["end"], figs["n_days"],
             figs["record_start"], figs["record_end"],
             figs["record_days"]))
    print("%d alarm slots, %d on eq_ items"
          % (figs["n_slots"], figs["eq_slots"]))
    print()
    print("observed structure")
    print("  breach entries               %d (%d on eq_ items)"
          % (figs["obs_entries"], figs["obs_eq_entries"]))
    print("  distinct breached slots      %d"
          % figs["obs_distinct_slots"])
    print("  slots >=2 / >=3 / >=5        %d / %d / %d "
          "(max thread %d)"
          % (figs["obs_slots_ge2"], figs["obs_slots_ge3"],
             figs["obs_slots_ge5"], figs["obs_max_thread"]))
    print("  item verdicts                EVENT %d, TRANSIENT %d, "
          "UNSTABLE %d"
          % (figs["obs_event_entries"],
             figs["obs_transient_entries"],
             figs["obs_unstable_entries"]))
    print("  >=3-threads unidirectional   %d of %d"
          % (figs["obs_threads_ge3_same_dir"],
             figs["obs_threads_ge3"]))
    print("  >=5-threads unidirectional   %d of %d"
          % (figs["obs_threads_ge5_same_dir"],
             figs["obs_threads_ge5"]))
    print("  cross-model EVENT items      %d"
          % figs["obs_cross_model_event_items"])
    print()
    print("no-drift null, exact")
    print("  sum p_i per day              %.6f"
          % figs["sum_p_per_day"])
    print("  E[breach entries]            %.3f   P(>= %d) = %.4g"
          % (figs["e_total_entries"], figs["obs_entries"],
             figs["p_total_ge_obs"]))
    print("  E[distinct breached slots]   %.2f"
          % figs["e_distinct_slots"])
    print("  E[slots >=2 / >=3 / >=5]     %.4f / %.6f / %.4g"
          % (figs["e_slots_ge2"], figs["e_slots_ge3"],
             figs["e_slots_ge5"]))
    print("  P(#slots >=2 at least %2d)    %.4g"
          % (figs["obs_slots_ge2"], figs["p_nslots_ge2_tail"]))
    print("  P(#slots >=3 at least %2d)    %.4g"
          % (figs["obs_slots_ge3"], figs["p_nslots_ge3_tail"]))
    print("  P(#slots >=5 at least %2d)    %.4g"
          % (figs["obs_slots_ge5"], figs["p_nslots_ge5_tail"]))
    if figs["calib_factor"] is None:
        print("  count-calibrated             skipped (no observed "
              "entries)")
    else:
        print("  count-calibrated x%.4f     %.4g / %.4g / %.4g"
              % (figs["calib_factor"],
                 figs["calib_p_nslots_ge2_tail"],
                 figs["calib_p_nslots_ge3_tail"],
                 figs["calib_p_nslots_ge5_tail"]))
    print("  eq_ share of breach mass     %.5f"
          % figs["eq_share"])
    print("  P(all %2d entries on eq_)     %.4g"
          % (figs["obs_entries"], figs["p_all_entries_eq"]))
    print("  P(all %2d distinct on eq_)    %.4g"
          % (figs["obs_distinct_slots"], figs["p_all_distinct_eq"]))
    print("  pooled P(same dir 3 of 3)    %.4f (tie mass %.4f)"
          % (figs["pooled_same_dir_3of3"], figs["pooled_tie_mass"]))
    print("  E[slots >=3 same dir]        %.6f   tail at %d: %.4g"
          % (figs["e_slots_ge3_same_dir"],
             figs["obs_threads_ge3_same_dir"],
             figs["p_nslots_ge3_same_tail"]))
    print("  P(any slot >=5 same dir)     %.4g   tail at %d: %.4g"
          % (figs["p_any_slot_ge5_same_dir"],
             figs["obs_threads_ge5_same_dir"],
             figs["p_nslots_ge5_same_tail"]))


def selfcheck():
    figs = analyze(SELFCHECK_START, SELFCHECK_END)
    report(figs)
    print()
    print("selfcheck against the adversarially verified figures for "
          "%s..%s" % (SELFCHECK_START, SELFCHECK_END))
    bad = 0
    for name, want in PINNED_INTS:
        got = figs[name]
        ok = got == want
        bad += 0 if ok else 1
        print("  %-27s got %-14s pinned %-12s %s"
              % (name, got, want, "ok" if ok else "FAIL"))
    for name, want, tol in PINNED_FLOATS:
        got = figs[name]
        ok = abs(got - want) <= tol
        bad += 0 if ok else 1
        print("  %-27s got %-14.6g pinned %-12g %s"
              % (name, got, want, "ok" if ok else "FAIL"))
    if bad:
        raise SystemExit("selfcheck FAILED on %d of %d pinned "
                         "figures" % (bad, len(PINNED_INTS)
                                      + len(PINNED_FLOATS)))
    print("selfcheck passed: all %d pinned figures reproduced"
          % (len(PINNED_INTS) + len(PINNED_FLOATS)))


def iso_date(s):
    try:
        datetime.date.fromisoformat(s)
    except ValueError:
        raise argparse.ArgumentTypeError(
            "not an ISO date (YYYY-MM-DD): %r" % s)
    return s


def main():
    ap = argparse.ArgumentParser(
        description="Recurrence structure of the observed monitor "
                    "breaches against the exact no-drift null.")
    ap.add_argument("--start", type=iso_date, default=None,
                    help="window start, ISO, inclusive (default: "
                         "first recorded day)")
    ap.add_argument("--end", type=iso_date, default=None,
                    help="window end, ISO, inclusive (default: last "
                         "recorded day)")
    ap.add_argument("--selfcheck", action="store_true",
                    help="pin the window to %s..%s and assert the "
                         "adversarially verified figures"
                         % (SELFCHECK_START, SELFCHECK_END))
    args = ap.parse_args()
    if args.selfcheck:
        if args.start or args.end:
            raise SystemExit(
                "--selfcheck fixes the window; drop --start/--end")
        selfcheck()
    else:
        report(analyze(args.start, args.end))


if __name__ == "__main__":
    main()
