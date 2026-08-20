"""Between-day variance of quiet-slot probe TVDs for the monitor.

Port of the August 2026 between-day variance lane analysis into a
committable reproduction script. Reads only committed inputs: the
per-model baseline files, verdicts.jsonl, and the derived daily
counts file (probe/monitor/derived/daily_counts.jsonl). The raw
per-call record is never touched.

Method. Each alarm slot (model, item) is scored once per probe day:
the TVD between the committed baseline distribution (counts / n)
and that day's K=10 probe draw, each side normalized by its own
parsed count. A slot-day breaches when its TVD strictly exceeds the
item's band p99, the monitor's alarm test. A slot is quiet in a
window when it never breaches there, active otherwise. Quiet slots
are the sample of drift-free behavior the analysis rests on.

Reported, over the chosen window:
 a) quiet/active split by model and class, cross-checked against
    the breached lists in verdicts.jsonl
 b) pooled quiet-slot daily TVD percentiles by class; percentile =
    smallest value with at least q coverage (the band convention)
 c) empirical false-alarm curve: the fraction of quiet-slot daily
    TVDs strictly above each candidate band width
 d) overdispersion: observed mean daily TVD against the exact
    expected mean under multinomial(K, baseline / 20) truth,
    enumerated over all 286 compositions of 10 draws into 4
    options, and under the smoothed truth (c + 1) / (n + 4);
    pooled, per model, and restricted to nonzero-expectation slots
 e) consecutive-day TVDs (adjacent probe days, same slot) against
    the Aug 2 within-day run-pair TVDs (run1 vs run2 in the
    baseline files)
 f) mean decomposition: observed mean = sampling mean + between-day
    excess, plus a K=30 projection that shrinks only the sampling
    term by sqrt(3) and leaves the excess untouched

Window. --start and --end (ISO dates, inclusive) default to the
full derived record; the window actually used is printed first.
Windows matter because the record now extends past the validated
window: the pinned figures asserted by --selfcheck are for
2026-08-02 to 2026-08-13 and were adversarially verified by
independent recomputation. --selfcheck reruns that window and
asserts every pinned figure, so refactors can be checked with one
command.

Run:
  python probe/scripts/between_day_variance.py
  python probe/scripts/between_day_variance.py --start S --end E
  python probe/scripts/between_day_variance.py --selfcheck
"""
import os
import json
import math
import glob
import argparse
import collections

HERE = os.path.dirname(os.path.abspath(__file__))
MONITOR = os.path.join(HERE, os.pardir, "monitor")
BASELINES = os.path.join(MONITOR, "baselines")
VERDICTS = os.path.join(MONITOR, "verdicts.jsonl")
DAILY_COUNTS = os.path.join(MONITOR, "derived", "daily_counts.jsonl")

OPTIONS = ("A", "B", "C", "D")
K = 10
WIDTHS = (0.20, 0.25, 0.267, 0.30, 0.317, 0.35, 0.40, 0.45, 0.50)
CLASSES = ("eq", "decisive")
VALIDATED_START = "2026-08-02"
VALIDATED_END = "2026-08-13"


def cls_of(item_id):
    return "eq" if item_id.startswith("eq_") else "decisive"


def tvd(counts_a, n_a, counts_b, n_b):
    return 0.5 * sum(abs(counts_a.get(o, 0) / n_a
                         - counts_b.get(o, 0) / n_b) for o in OPTIONS)


def pctl(sorted_vals, q):
    """Smallest value with at least q coverage (band convention)."""
    if not sorted_vals:
        return None
    idx = max(0, math.ceil(q * len(sorted_vals)) - 1)
    return sorted_vals[min(idx, len(sorted_vals) - 1)]


def compositions(k, parts):
    """Every way to split k draws across parts options."""
    if parts == 1:
        yield (k,)
        return
    for i in range(k + 1):
        for rest in compositions(k - i, parts - 1):
            yield (i,) + rest


def log_multinomial(comp, log_probs):
    """Log probability of one composition, or None if it needs an
    option the truth assigns zero mass."""
    lp = math.lgamma(sum(comp) + 1)
    for c, l in zip(comp, log_probs):
        lp -= math.lgamma(c + 1)
        if c:
            if l is None:
                return None
            lp += c * l
    return lp


def expected_mean_tvd(counts, n, truth, comps):
    """E[TVD(baseline, K-draw)] under multinomial(K, truth)."""
    base = [counts.get(o, 0) / n for o in OPTIONS]
    log_probs = [None if p <= 0 else math.log(p) for p in truth]
    acc = 0.0
    for comp in comps:
        lp = log_multinomial(comp, log_probs)
        if lp is None:
            continue
        t = 0.5 * sum(abs(b - c / K) for b, c in zip(base, comp))
        acc += math.exp(lp) * t
    return acc


def load_baselines():
    paths = sorted(glob.glob(os.path.join(BASELINES, "*.json")))
    if not paths:
        raise SystemExit("no baseline files under %s" % BASELINES)
    base = {}
    for path in paths:
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
        if doc["k"] != K:
            raise SystemExit(
                "baseline %s was qualified at k=%s but this script "
                "assumes K=%d" % (os.path.basename(path), doc["k"], K))
        base[doc["model"]] = {iid: rec for iid, rec
                              in doc["items"].items()
                              if rec["class"] == "alarm"}
    item_ids = None
    for model in sorted(base):
        ids = sorted(base[model])
        if item_ids is None:
            item_ids = ids
        elif ids != item_ids:
            raise SystemExit("item banks differ across models")
    return base


def load_daily_counts(start, end):
    """(model, item) -> {date: Counter} for monitor_probe days in
    [start, end], plus the sorted list of dates seen."""
    counts = collections.defaultdict(dict)
    dates = set()
    with open(DAILY_COUNTS, encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            if rec["phase"] != "monitor_probe":
                continue
            d = rec["date"]
            if not (start <= d <= end):
                continue
            dates.add(d)
            counts[(rec["model"], rec["item_id"])][d] = \
                collections.Counter(rec["counts"])
    return counts, sorted(dates)


def load_verdict_breaches(dates):
    """Set of (date, model, item_id) breached per verdicts.jsonl."""
    breached = set()
    dateset = set(dates)
    with open(VERDICTS, encoding="utf-8") as f:
        for line in f:
            v = json.loads(line)
            if v["date"] not in dateset:
                continue
            for b in v.get("breached", []):
                breached.add((v["date"], v["model"], b["item_id"]))
    return breached


def compute(base, counts, dates):
    """All figures for one window, returned as a plain dict."""
    res = {"dates": dates}

    # (a) daily TVDs, breach days, quiet/active split
    daily = {}
    breach = {}
    skipped = 0
    for model in sorted(base):
        for iid in sorted(base[model]):
            rec = base[model][iid]
            bc = rec["baseline_counts"]
            bn = rec["n"]
            p99 = rec["band"]["p99"]
            per = {}
            br = []
            for d in dates:
                c = counts.get((model, iid), {}).get(d)
                if c is None or sum(c.values()) == 0:
                    skipped += 1
                    continue
                t = tvd(bc, bn, c, sum(c.values()))
                per[d] = t
                if t > p99:
                    br.append(d)
            if per:
                daily[(model, iid)] = per
                breach[(model, iid)] = br
    quiet = sorted(k for k in daily if not breach[k])
    active = sorted(k for k in daily if breach[k])
    res["skipped_slot_days"] = skipped
    res["quiet_total"] = len(quiet)
    res["active_total"] = len(active)
    res["active_by_model"] = {m: sum(1 for k in active if k[0] == m)
                              for m in sorted(base)}
    res["active_by_class"] = {c: sum(1 for k in active
                                     if cls_of(k[1]) == c)
                              for c in CLASSES}
    res["active_detail"] = [
        (m, iid, cls_of(iid), breach[(m, iid)],
         base[m][iid]["band"]["p99"],
         max(daily[(m, iid)].values())) for (m, iid) in active]

    mine = set((d, m, iid) for (m, iid) in active
               for d in breach[(m, iid)])
    verd = load_verdict_breaches(dates)
    res["breach_slot_days"] = len(mine)
    res["verdict_breach_slot_days"] = len(verd)
    res["breach_only_mine"] = sorted(mine - verd)
    res["breach_only_verdicts"] = sorted(verd - mine)

    # (b) pooled quiet-slot daily TVDs by class
    pooled = {c: [] for c in CLASSES}
    for k in quiet:
        pooled[cls_of(k[1])].extend(daily[k].values())
    for c in CLASSES:
        pooled[c].sort()
    res["pooled"] = pooled

    # (c) false-alarm curve (strict exceedance fractions)
    curve = {}
    for c in CLASSES:
        v = pooled[c]
        curve[c] = {w: (sum(1 for x in v if x > w),
                        sum(1 for x in v if x > w) / len(v))
                    for w in WIDTHS} if v else {}
    res["curve"] = curve

    # (d) overdispersion, exact enumeration
    comps = list(compositions(K, len(OPTIONS)))
    assert len(comps) == 286
    slots = []  # (model, item, class, obs_mean, exp_emp, exp_smo)
    for (model, iid) in quiet:
        rec = base[model][iid]
        bc = collections.Counter(rec["baseline_counts"])
        bn = rec["n"]
        emp = [bc.get(o, 0) / bn for o in OPTIONS]
        smo = [(bc.get(o, 0) + 1.0) / (bn + 4.0) for o in OPTIONS]
        vals = list(daily[(model, iid)].values())
        slots.append((model, iid, cls_of(iid),
                      sum(vals) / len(vals),
                      expected_mean_tvd(bc, bn, emp, comps),
                      expected_mean_tvd(bc, bn, smo, comps)))

    def group_stats(members):
        obs = sum(r[3] for r in members)
        e_emp = sum(r[4] for r in members)
        e_smo = sum(r[5] for r in members)
        nz = [r for r in members if r[4] > 0]
        obs_nz = sum(r[3] for r in nz)
        e_nz = sum(r[4] for r in nz)
        return {
            "n_slots": len(members),
            "obs_sum": obs,
            "exp_emp_sum": e_emp,
            "exp_smo_sum": e_smo,
            "ratio_emp": obs / e_emp if e_emp > 0 else None,
            "ratio_smo": obs / e_smo if e_smo > 0 else None,
            "ratio_emp_nonzero": obs_nz / e_nz if e_nz > 0 else None,
            "slots_exp0": len(members) - len(nz),
            "slots_exp0_obs_gt0": sum(1 for r in members
                                      if r[4] == 0 and r[3] > 0)}

    over = {"all": group_stats(slots)}
    for c in CLASSES:
        over["class=" + c] = group_stats(
            [r for r in slots if r[2] == c])
    for m in sorted(base):
        over["model=" + m] = group_stats(
            [r for r in slots if r[0] == m])
    res["overdispersion"] = over

    # (e) consecutive-day vs within-day run-pair TVDs, quiet slots
    consec = {c: [] for c in CLASSES}
    for (model, iid) in quiet:
        per = counts.get((model, iid), {})
        for i in range(len(dates) - 1):
            ca = per.get(dates[i])
            cb = per.get(dates[i + 1])
            if not ca or not cb:
                continue
            consec[cls_of(iid)].append(
                tvd(ca, sum(ca.values()), cb, sum(cb.values())))
    within = {c: [] for c in CLASSES}
    for (model, iid) in quiet:
        runs = base[model][iid]["runs"]
        r1 = collections.Counter(runs["run1"])
        r2 = collections.Counter(runs["run2"])
        within[cls_of(iid)].append(
            tvd(r1, sum(r1.values()), r2, sum(r2.values())))
    for c in CLASSES:
        consec[c].sort()
        within[c].sort()
    res["consec"] = consec
    res["within"] = within
    res["daypair_ratio"] = {
        c: ((sum(consec[c]) / len(consec[c]))
            / (sum(within[c]) / len(within[c]))
            if consec[c] and within[c] and sum(within[c]) > 0
            else None)
        for c in CLASSES}

    # (f) decomposition and K=30 projection, per class
    decomp = {}
    for c in CLASSES:
        members = [r for r in slots if r[2] == c]
        if not members:
            continue
        obs = sum(r[3] for r in members) / len(members)
        exp = sum(r[4] for r in members) / len(members)
        excess = obs - exp
        k30 = exp / math.sqrt(3.0) + excess
        decomp[c] = {"obs_mean": obs, "exp_sampling_mean": exp,
                     "excess": excess, "k30_projected_mean": k30,
                     "k30_shrink": k30 / obs if obs > 0 else None}
    res["decomp"] = decomp
    return res


def fmt(x, nd=3):
    return "nan" if x is None else "%.*f" % (nd, x)


def report(res):
    print("window %s .. %s (%d probe days)"
          % (res["dates"][0], res["dates"][-1], len(res["dates"])))
    print("skipped slot-days (no probe data): %d"
          % res["skipped_slot_days"])
    print()

    print("quiet %d / active %d" % (res["quiet_total"],
                                    res["active_total"]))
    print("active by class %s" % json.dumps(res["active_by_class"]))
    print("active by model %s" % json.dumps(res["active_by_model"]))
    for (m, iid, c, days, p99, mx) in res["active_detail"]:
        print("  active %s %s class=%s n_breach=%d band_p99=%.3f "
              "max_tvd=%.3f days=%s"
              % (m, iid, c, len(days), p99, mx, ",".join(days)))
    print("breach slot-days: mine=%d verdicts=%d only_mine=%s "
          "only_verdicts=%s"
          % (res["breach_slot_days"],
             res["verdict_breach_slot_days"],
             res["breach_only_mine"], res["breach_only_verdicts"]))
    print()

    for c in CLASSES:
        v = res["pooled"][c]
        if not v:
            continue
        print("quiet pooled TVD class=%s n=%d p50=%.4f p90=%.4f "
              "p95=%.4f p99=%.4f max=%.4f mean=%.5f frac_zero=%.4f"
              % (c, len(v), pctl(v, .50), pctl(v, .90),
                 pctl(v, .95), pctl(v, .99), v[-1],
                 sum(v) / len(v),
                 sum(1 for x in v if x == 0) / len(v)))
    print()

    for c in CLASSES:
        cur = res["curve"][c]
        if not cur:
            continue
        frac = {"%.3f" % w: round(cur[w][1], 5) for w in WIDTHS}
        print("false-alarm curve class=%s frac=%s"
              % (c, json.dumps(frac)))
    print()

    order = (["all"] + ["class=" + c for c in CLASSES]
             + sorted(g for g in res["overdispersion"]
                      if g.startswith("model=")))
    for g in order:
        s = res["overdispersion"][g]
        print("overdispersion %s n_slots=%d obs_sum=%.4f "
              "exp_emp_sum=%.4f ratio_emp=%s "
              "ratio_emp_nonzero_only=%s ratio_smoothed=%s "
              "slots_exp0=%d slots_exp0_obs_gt0=%d"
              % (g, s["n_slots"], s["obs_sum"], s["exp_emp_sum"],
                 fmt(s["ratio_emp"]), fmt(s["ratio_emp_nonzero"]),
                 fmt(s["ratio_smo"]), s["slots_exp0"],
                 s["slots_exp0_obs_gt0"]))
    print()

    for c in CLASSES:
        v = res["consec"][c]
        w = res["within"][c]
        if not v or not w:
            continue
        print("consecutive-day TVD quiet class=%s n=%d p50=%.4f "
              "p90=%.4f p99=%.4f max=%.4f mean=%.5f"
              % (c, len(v), pctl(v, .50), pctl(v, .90),
                 pctl(v, .99), v[-1], sum(v) / len(v)))
        print("within-day run-pair quiet class=%s n=%d p50=%.4f "
              "p90=%.4f p99=%.4f max=%.4f mean=%.5f"
              % (c, len(w), pctl(w, .50), pctl(w, .90),
                 pctl(w, .99), w[-1], sum(w) / len(w)))
        print("consec/within mean ratio class=%s %s"
              % (c, fmt(res["daypair_ratio"][c])))
    print()

    for c in CLASSES:
        if c not in res["decomp"]:
            continue
        d = res["decomp"][c]
        print("decomposition class=%s obs_mean=%.5f "
              "exp_sampling_mean=%.5f excess_betweenday=%.5f "
              "k30_projected_mean=%.4f k30_vs_k10_shrink=%s"
              % (c, d["obs_mean"], d["exp_sampling_mean"],
                 d["excess"], d["k30_projected_mean"],
                 fmt(d["k30_shrink"])))


def selfcheck(res):
    """Assert every pinned figure for 2026-08-02 .. 2026-08-13.

    The pinned values were adversarially verified by independent
    recomputation; a mismatch means the port (or an input file)
    changed, not the record."""
    fails = []

    def check(label, got, want, nd=None):
        val = got if nd is None else round(got, nd)
        ok = val == want
        if not ok:
            fails.append(label)
        print("  %-44s got=%s want=%s %s"
              % (label, val, want, "ok" if ok else "FAIL"))

    check("quiet_total", res["quiet_total"], 327)
    check("active_total", res["active_total"], 13)
    check("active_decisive", res["active_by_class"]["decisive"], 0)
    check("active_eq", res["active_by_class"]["eq"], 13)
    abm = res["active_by_model"]
    check("active_haiku", abm["claude-haiku-4-5-20251001"], 1)
    check("active_sonnet", abm["claude-sonnet-4-6"], 2)
    check("active_gpt", abm["gpt-5.6-terra"], 5)
    check("active_gemini", abm["gemini-3.6-flash"], 0)
    check("active_deepseek", abm["deepseek-v4-flash"], 5)

    eq = res["pooled"]["eq"]
    de = res["pooled"]["decisive"]
    check("pooled_eq_n", len(eq), 1224)
    check("pooled_eq_p50", pctl(eq, .50), 0.0, 4)
    check("pooled_eq_p90", pctl(eq, .90), 0.15, 4)
    check("pooled_eq_p95", pctl(eq, .95), 0.20, 4)
    check("pooled_eq_p99", pctl(eq, .99), 0.35, 4)
    check("pooled_eq_max", eq[-1], 0.45, 4)
    check("pooled_eq_mean", sum(eq) / len(eq), 0.03632, 5)
    check("pooled_eq_frac_zero",
          sum(1 for x in eq if x == 0) / len(eq), 0.7484, 4)
    check("pooled_dec_n", len(de), 2700)
    check("pooled_dec_p99", pctl(de, .99), 0.10, 4)
    check("pooled_dec_max", de[-1], 0.20, 4)
    check("pooled_dec_mean", sum(de) / len(de), 0.00217, 5)
    check("pooled_dec_frac_zero",
          sum(1 for x in de if x == 0) / len(de), 0.9781, 4)

    eq_curve = {0.20: 0.04412, 0.25: 0.02288, 0.267: 0.02206,
                0.30: 0.01879, 0.317: 0.01307, 0.35: 0.00817,
                0.40: 0.00327, 0.45: 0.0, 0.50: 0.0}
    for w in WIDTHS:
        check("curve_eq_%.3f" % w, res["curve"]["eq"][w][1],
              eq_curve[w], 5)
        check("curve_dec_%.3f" % w,
              res["curve"]["decisive"][w][1], 0.0, 5)

    over = res["overdispersion"]
    check("ratio_emp_eq", over["class=eq"]["ratio_emp"], 1.502, 3)
    check("ratio_emp_dec",
          over["class=decisive"]["ratio_emp"], 1.557, 3)
    check("ratio_emp_all", over["all"]["ratio_emp"], 1.508, 3)
    check("ratio_emp_nonzero_all",
          over["all"]["ratio_emp_nonzero"], 1.301, 3)
    check("ratio_smoothed_all", over["all"]["ratio_smo"], 0.100, 3)
    check("ratio_emp_sonnet",
          over["model=claude-sonnet-4-6"]["ratio_emp"], 1.757, 3)
    check("ratio_emp_gemini",
          over["model=gemini-3.6-flash"]["ratio_emp"], 2.107, 3)
    check("ratio_emp_gpt",
          over["model=gpt-5.6-terra"]["ratio_emp"], 1.480, 3)
    check("ratio_emp_deepseek",
          over["model=deepseek-v4-flash"]["ratio_emp"], 1.382, 3)
    check("haiku_exp_emp_sum",
          over["model=claude-haiku-4-5-20251001"]["exp_emp_sum"],
          0.0, 6)
    check("slots_exp0_all", over["all"]["slots_exp0"], 300)
    check("slots_exp0_obs_gt0_all",
          over["all"]["slots_exp0_obs_gt0"], 24)

    cv = res["consec"]["eq"]
    wv = res["within"]["eq"]
    check("consec_eq_n", len(cv), 1122)
    check("consec_eq_mean", sum(cv) / len(cv), 0.03984, 5)
    check("consec_eq_p90", pctl(cv, .90), 0.20, 4)
    check("consec_eq_p99", pctl(cv, .99), 0.40, 4)
    check("consec_eq_max", cv[-1], 0.60, 4)
    check("within_eq_n", len(wv), 102)
    check("within_eq_mean", sum(wv) / len(wv), 0.03725, 5)
    check("within_eq_p90", pctl(wv, .90), 0.10, 4)
    check("daypair_ratio_eq", res["daypair_ratio"]["eq"], 1.069, 3)
    check("daypair_ratio_dec",
          res["daypair_ratio"]["decisive"], 0.761, 3)

    d = res["decomp"]["eq"]
    check("decomp_eq_exp", d["exp_sampling_mean"], 0.02418, 5)
    check("decomp_eq_excess", d["excess"], 0.01214, 5)
    check("decomp_eq_k30", d["k30_projected_mean"], 0.0261, 4)
    check("decomp_eq_shrink", d["k30_shrink"], 0.719, 3)

    if fails:
        raise SystemExit("SELFCHECK FAIL: %d mismatched figure(s): %s"
                         % (len(fails), ", ".join(fails)))
    print("SELFCHECK PASS: every pinned figure reproduced for "
          "%s .. %s" % (VALIDATED_START, VALIDATED_END))


def main():
    ap = argparse.ArgumentParser(
        description="Between-day variance of quiet-slot probe TVDs.")
    ap.add_argument("--start", default=None,
                    help="window start, ISO date, inclusive "
                         "(default: first recorded probe day)")
    ap.add_argument("--end", default=None,
                    help="window end, ISO date, inclusive "
                         "(default: last recorded probe day)")
    ap.add_argument("--selfcheck", action="store_true",
                    help="run the validated window %s..%s and "
                         "assert every pinned figure"
                         % (VALIDATED_START, VALIDATED_END))
    args = ap.parse_args()

    if args.selfcheck:
        start, end = VALIDATED_START, VALIDATED_END
        if args.start or args.end:
            raise SystemExit("--selfcheck fixes the window; drop "
                             "--start/--end")
    else:
        start = args.start or "0000-01-01"
        end = args.end or "9999-12-31"
        if start > end:
            raise SystemExit("--start is after --end")

    base = load_baselines()
    counts, dates = load_daily_counts(start, end)
    if not dates:
        raise SystemExit("no probe days in [%s, %s]" % (start, end))
    res = compute(base, counts, dates)

    if args.selfcheck:
        print("selfcheck window %s .. %s (%d probe days)"
              % (dates[0], dates[-1], len(dates)))
        selfcheck(res)
    else:
        report(res)


if __name__ == "__main__":
    main()
