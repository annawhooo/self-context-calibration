"""Every prose number in the INTERCEPT paper that no other committed
script prints, computed from the committed record for one window.

Reads only committed inputs through figdata (verdict log, derived
daily counts, baseline files). Prints labeled lines; the paper's
number swap is a diff of this output against the manuscript. Any
number in the manuscript that is not on this output, on the output
of a script this file names, or in a committed note, does not go in.

  PAPER_DATA_THROUGH=2026-09-26 python paper/figures/freeze_numbers.py
  python paper/figures/freeze_numbers.py --start S --end E

Companion scripts of record, not recomputed here:
  probe/scripts/recurrence_structure_null.py   (T1, section 3.3)
  probe/scripts/between_day_variance.py        (F3, sections 3.2, 5)
  probe/scripts/float_census.py                (section 4 item f)
  probe/scripts/expected_false_breaches.py     (section 2)
  probe/scripts/step_change_watch.py           (sections 3.1.1, 3.4)
  probe/scripts/return_watch.py                (section 3.1.1)
  paper/figures/quiet_slot_decomposition.py    (F4, section 3.5)
  paper/figures/raw_row_census.py              (rows-only numbers)
"""
import argparse
import collections
import datetime as dt
import os
from fractions import Fraction
from math import comb

import figdata as fd


def vec(counts):
    return "/".join(str(counts.get(o, 0)) for o in fd.OPTIONS)


def multinomial_p(counts, probs):
    k = sum(counts.values())
    p, rem = 1.0, k
    for o, pr in zip(fd.OPTIONS, probs):
        c = counts.get(o, 0)
        p *= comb(rem, c) * (pr ** c if c else 1.0)
        rem -= c
    return p


def fmt_p(p):
    return "%.1e" % p if p < 1e-3 else "%.4f" % p


def dwell_runs(days, state_of):
    runs, cur, last = [], None, None
    for d in days:
        st = state_of(d)
        if st == last:
            cur[1] += 1
        else:
            cur = [st, 1, d]
            runs.append(cur)
            last = st
    return " ".join("%s%d@%s" % (s[0], k, d[5:]) for s, k, d in runs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2026-08-02")
    ap.add_argument("--end", default=fd.DATA_THROUGH)
    a = ap.parse_args()
    lo, hi = a.start, a.end

    verdicts = [v for v in fd.load_verdicts() if lo <= v["date"] <= hi]
    daily = {k: c for k, c in fd.load_daily().items()
             if lo <= k[0] <= hi}
    baselines = fd.load_baselines()
    breaches = fd.breach_index(verdicts)

    d0 = dt.date.fromisoformat(lo)
    d1 = dt.date.fromisoformat(hi)
    dates = sorted({v["date"] for v in verdicts})
    by_day = collections.defaultdict(list)
    for v in verdicts:
        by_day[v["date"]].append(v)
    days_with_data = sum(1 for d in dates
                         if any(v["verdict"] != "ERROR"
                                for v in by_day[d]))
    print("window %s..%s" % (lo, hi))
    print("  calendar days             %d" % ((d1 - d0).days + 1))
    print("  dates with a verdict line %d" % len(dates))
    print("  dates with >=1 probe      %d" % days_with_data)
    all_error = [d for d in dates
                 if all(v["verdict"] == "ERROR" for v in by_day[d])]
    print("  all-model ERROR dates     %s" % (", ".join(all_error)
                                              or "-"))

    print("\nper model: probe days / ERROR days / ECHO_CHANGE days / "
          "calls / breach entries")
    total_calls = 0
    for m in fd.MODELS:
        rows = [v for v in verdicts if v["model"] == m]
        probe = [v for v in rows
                 if v["verdict"] not in ("ERROR", "ECHO_CHANGE")]
        err = [v for v in rows if v["verdict"] == "ERROR"]
        echo = [v for v in rows if v["verdict"] == "ECHO_CHANGE"]
        calls = sum(v["calls"] or 0 for v in rows)
        total_calls += calls
        nb = sum(len(v["breached"]) for v in rows)
        print("  %-13s %3d / %2d / %2d / %6d / %2d   error dates: %s"
              % (fd.SHORT[m], len(probe), len(err), len(echo), calls,
                 nb, ", ".join(v["date"][5:] for v in err) or "-"))
    print("  total calls (verdict log) %d" % total_calls)

    print("\nverdict tallies")
    dv = collections.Counter(v["verdict"] for v in verdicts)
    print("  day verdicts   %s" % dict(sorted(dv.items())))
    iv = collections.Counter(b["item_verdict"] for v in verdicts
                             for b in v["breached"])
    print("  item verdicts  %s" % dict(sorted(iv.items())))
    entries = sum(iv.values())
    eq_entries = sum(1 for v in verdicts for b in v["breached"]
                     if fd.is_equipoise(b["item_id"]))
    print("  breach entries %d, on equipoise %d, distinct slots %d"
          % (entries, eq_entries, len(breaches)))
    joint = [(v["date"], fd.SHORT[v["model"]], len(v["breached"]))
             for v in verdicts if len(v["breached"]) >= 2]
    print("  model-days with >=2 breached items: %d" % len(joint))
    for d, m, k in joint:
        print("    %s %s x%d" % (d, m, k))
    per_item = collections.defaultdict(set)
    for (m, i) in breaches:
        per_item[i].add(m)
    multi = {i: sorted(fd.SHORT[m] for m in ms)
             for i, ms in per_item.items() if len(ms) >= 2}
    print("  items breached on >=2 models: %d  %s" % (len(multi), multi))

    print("\nslots and baselines")
    slots = [(m, i) for m in fd.MODELS for i in baselines[m]]
    eq_slots = [s for s in slots if fd.is_equipoise(s[1])]
    print("  alarm slots %d, equipoise %d, decisive %d"
          % (len(slots), len(eq_slots), len(slots) - len(eq_slots)))
    unan = []
    for m, i in eq_slots:
        bc = fd.baseline_for(baselines[m][i], lo)["baseline_counts"]
        if max(bc.values()) == sum(bc.values()):
            unan.append((m, i))
    print("  equipoise slots unanimous at the Aug 2 baseline: %d of %d"
          % (len(unan), len(eq_slots)))
    print("    per model %s"
          % dict(collections.Counter(fd.SHORT[m] for m, _ in unan)))
    ub = [s for s in unan if s in breaches]
    print("  of those, breached in window: %d  %s"
          % (len(ub), ["%s %s" % (fd.SHORT[m], fd.item_short(i))
                       for m, i in ub]))

    print("\nslot-days (probe phase, in window)")
    dec_tvds, eq_tvds = [], []
    for (d, m, i), c in daily.items():
        if m not in baselines or i not in baselines[m]:
            continue
        ref = fd.baseline_for(baselines[m][i], d)
        t = fd.tvd(c, ref["baseline_counts"])
        (eq_tvds if fd.is_equipoise(i) else dec_tvds).append(t)
    print("  decisive slot-days %d, max TVD %.2f, above 0.20: %d, "
          "above 0.25: %d, above 0.30: %d"
          % (len(dec_tvds), max(dec_tvds),
             sum(t > 0.20 for t in dec_tvds),
             sum(t > 0.25 for t in dec_tvds),
             sum(t > 0.30 for t in dec_tvds)))
    print("  equipoise slot-days %d, max TVD %.2f"
          % (len(eq_tvds), max(eq_tvds)))
    print("  total slot-days %d" % (len(dec_tvds) + len(eq_tvds)))

    print("\nrerun gaps from run ids (probe run start to rerun run "
          "start, minutes)")
    gaps = []
    for v in verdicts:
        r = v.get("run_ids") or {}
        if "probe" in r and "rerun" in r:
            t0 = dt.datetime.fromisoformat(r["probe"])
            t1 = dt.datetime.fromisoformat(r["rerun"])
            gaps.append(((t1 - t0).total_seconds() / 60.0, v["date"],
                         fd.SHORT[v["model"]]))
    gaps.sort()
    if gaps:
        k = len(gaps)
        med = (gaps[k // 2][0] if k % 2
               else (gaps[k // 2 - 1][0] + gaps[k // 2][0]) / 2)
        print("  n=%d  min %.1f (%s %s)  median %.1f  max %.1f (%s %s)"
              % (k, gaps[0][0], gaps[0][1], gaps[0][2], med,
                 gaps[-1][0], gaps[-1][1], gaps[-1][2]))
    print("  (item-level last-probe-sample to first-rerun-sample gaps"
          " need the raw rows: raw_row_census.py)")

    exact = sum(1 for v in verdicts for b in v["breached"]
                if b["rerun_tvd_vs_probe"] == 0)
    print("\nrerun reproduced the probe exactly on %d of %d entries"
          % (exact, entries))

    print("\nfocal threads (>=3 entries): exact vector recurrence")
    order = sorted(breaches, key=lambda s: (fd.MODELS.index(s[0]), s[1]))
    for (m, i) in order:
        hits = breaches[(m, i)]
        if len(hits) < 3:
            continue
        rec = baselines[m][i]
        bc = fd.baseline_for(rec, lo)["baseline_counts"]
        n = sum(bc.values())
        emp = [bc.get(o, 0) / n for o in fd.OPTIONS]
        smo = [(bc.get(o, 0) + 1) / (n + 4) for o in fd.OPTIONS]
        days = sorted(d for (d, mm, ii) in daily if mm == m and ii == i)
        away_vecs = collections.Counter()
        breach_vecs = collections.Counter()
        for d in days:
            c = daily[(d, m, i)]
            if fd.classify_day(c, fd.baseline_for(rec, d)) == "away":
                away_vecs[vec(c)] += 1
            if d in hits:
                breach_vecs[vec(c)] += 1
        print("  %s %s  baseline %s  entries %d  observed days %d  "
              "away days %d" % (fd.SHORT[m], fd.item_short(i), vec(bc),
                                len(hits), len(days),
                                sum(away_vecs.values())))
        print("    breach dates: %s"
              % ", ".join(d[5:] + hits[d][0] for d in sorted(hits)))
        for vs, cnt in away_vecs.most_common(3):
            cv = dict(zip(fd.OPTIONS, map(int, vs.split("/"))))
            print("    away vector %s x%d  (breach days x%d)  "
                  "P(vector | empirical) %s  P(| smoothed) %s"
                  % (vs, cnt, breach_vecs.get(vs, 0),
                     fmt_p(multinomial_p(cv, emp)),
                     fmt_p(multinomial_p(cv, smo))))
        print("    dwell runs: %s" % dwell_runs(
            days, lambda d: fd.classify_day(daily[(d, m, i)],
                                            fd.baseline_for(rec, d))))

    print("\nhaiku spend_anomaly_v2 against the frozen Aug 2 reference"
          " (superseded reference ignored)")
    m, i = "claude-haiku-4-5-20251001", "eq_alert_spend_anomaly_v2"
    rec = baselines[m][i]
    ref0 = fd.baseline_for(rec, lo)
    days = sorted(d for (d, mm, ii) in daily if mm == m and ii == i)
    print("  %s" % dwell_runs(
        days, lambda d: fd.classify_day(daily[(d, m, i)], ref0)))
    home = [d for d in days
            if fd.classify_day(daily[(d, m, i)], ref0) == "home"]
    print("  home days vs Aug 2 reference: %d of %d observed; last %s"
          % (len(home), len(days), home[-1] if home else "-"))
    sup = rec.get("superseded", [])
    if sup:
        print("  re-baselined: superseded reference valid through %s; "
              "new reference %s" % (sup[0]["valid_through"],
                                    vec(rec["baseline_counts"])))

    print("\necho and identity")
    echo_days = [v["date"] for v in verdicts
                 if v["verdict"] == "ECHO_CHANGE"]
    print("  ECHO_CHANGE days %d (%s .. %s)"
          % (len(echo_days), echo_days[0][5:] if echo_days else "-",
             echo_days[-1][5:] if echo_days else "-"))
    for m in fd.MODELS:
        echoes = collections.Counter(
            v["model_id_echo"] for v in verdicts
            if v["model"] == m and v["model_id_echo"])
        print("  %-13s echoed ids %s" % (fd.SHORT[m], dict(echoes)))
    ds = [v for v in verdicts if v["model"] == "deepseek-v4-flash"
          and v["verdict"] not in ("ERROR", "ECHO_CHANGE")]
    print("  deepseek last behavioral probe day %s"
          % max(v["date"] for v in ds))
    dlp = breaches.get(("deepseek-v4-flash", "eq_alert_dlp_email_v2"), {})
    print("  deepseek dlp_email thread: %d breach days, %d EVENT, "
          "first %s, last %s"
          % (len(dlp), sum(1 for x in dlp.values() if x == "EVENT"),
             min(dlp) if dlp else "-", max(dlp) if dlp else "-"))

    review_blocks(verdicts, daily, baselines, breaches, lo, hi)


# ---------------------------------------------------------------------
# Blocks added after the 2026-09-28 verification run. Each answers one
# reviewer question with a committed computation.

def exact_tvd(counts, base):
    """TVD as an exact Fraction, each side over its own parsed count."""
    na = sum(counts.values()) or 1
    nb = sum(base.values()) or 1
    return Fraction(1, 2) * sum(
        abs(Fraction(counts.get(o, 0), na) - Fraction(base.get(o, 0), nb))
        for o in fd.OPTIONS)


def slot_null(base, band, truth, comps):
    """Per-day breach probability, breach-conditional direction law, for
    one slot under one truth. Mirrors expected_false_breaches.py: the
    monitor's float TVD, strict inequality against the stored band; the
    direction of a breaching composition is the option whose share
    gains most over the baseline share, ties to the earliest option
    (recurrence_structure_null.py)."""
    n = sum(base.values())
    emp = {o: base.get(o, 0) for o in fd.OPTIONS}
    if truth == "smoothed":
        probs = [(base.get(o, 0) + 1.0) / (n + 4.0) for o in fd.OPTIONS]
    else:
        probs = [base.get(o, 0) / n for o in fd.OPTIONS]
    p_breach = 0.0
    direction = collections.Counter()
    for comp in comps:
        if any(c and pr == 0 for c, pr in zip(comp, probs)):
            continue
        cv = dict(zip(fd.OPTIONS, comp))
        w = multinomial_p(cv, probs)
        if fd.tvd(cv, emp) > band:
            p_breach += w
            gains = {o: cv[o] / 10 - emp[o] / n for o in fd.OPTIONS}
            top = max(gains.values())
            direction[[o for o in fd.OPTIONS if gains[o] == top][0]] += w
    law = {o: (direction[o] / p_breach if p_breach else 0.0)
           for o in fd.OPTIONS}
    return p_breach, law


def poisson_binomial_tail(ps, k):
    """P(sum of independent Bernoulli(ps) >= k), exact DP."""
    dist = [1.0]
    for p in ps:
        nxt = [0.0] * (len(dist) + 1)
        for i, d in enumerate(dist):
            nxt[i] += d * (1 - p)
            nxt[i + 1] += d * p
        dist = nxt
    return sum(dist[k:])


def binomial_sum_tail(terms, k):
    """P(sum of independent Binomial(n_i, p_i) >= k), exact DP."""
    dist = [1.0]
    for n, p in terms:
        for _ in range(n):
            nxt = [0.0] * (len(dist) + 1)
            for i, d in enumerate(dist):
                nxt[i] += d * (1 - p)
                nxt[i + 1] += d * p
            dist = nxt
    return sum(dist[k:])


def runs_test(seq):
    """Wald-Wolfowitz z for a two-state sequence; None if degenerate."""
    n1 = seq.count("home")
    n2 = seq.count("away")
    if n1 == 0 or n2 == 0:
        return None
    runs = 1 + sum(1 for a, b in zip(seq, seq[1:]) if a != b)
    n = n1 + n2
    mu = 2.0 * n1 * n2 / n + 1
    var = 2.0 * n1 * n2 * (2.0 * n1 * n2 - n) / (n * n * (n - 1))
    return (runs - mu) / var ** 0.5 if var > 0 else None


def k30_bands(baselines):
    """Recompute every slot's band at K=30 from the committed baseline
    counts under the stored seed, the procedure the declined upgrade
    would have run (docs/claude_code_handoff_k30_upgrade.md, scope item
    2). Uses probe/monitor/monitor.py's own smoothed_bands when it
    imports, else a line-for-line replica of it."""
    import random
    import sys
    sys.path.insert(0, os.path.join(fd.REPO, "probe", "monitor"))
    try:
        from monitor import smoothed_bands
        source = "probe/monitor/monitor.py smoothed_bands"
    except Exception:
        def smoothed_bands(counts, seed, k=30, sims=10000, smooth=1.0):
            n = sum(counts.values())
            probs = [(counts.get(o, 0) + smooth) / (n + smooth * 4)
                     for o in fd.OPTIONS]
            rng = random.Random(seed)
            tvds = []
            for _ in range(sims):
                draw = collections.Counter(
                    rng.choices(fd.OPTIONS, weights=probs, k=k))
                tvds.append(0.5 * sum(abs(counts.get(o, 0) / n
                                          - draw.get(o, 0) / k)
                                      for o in fd.OPTIONS))
            tvds.sort()
            return tvds[int(0.95 * sims) - 1], tvds[int(0.99 * sims) - 1]
        source = "replica of monitor.smoothed_bands"
    out = {}
    for m in fd.MODELS:
        for i, rec in baselines[m].items():
            ref = fd.baseline_for(rec, "2026-08-02")
            _, p99 = smoothed_bands(collections.Counter(ref["baseline_counts"]),
                                    ref["band"]["seed"], k=30)
            out[(m, i)] = p99
    return source, out


def review_blocks(verdicts, daily, baselines, breaches, lo, hi):
    import os  # noqa: F401 (k30_bands path)
    comps = [(a, b, c, 10 - a - b - c)
             for a in range(11) for b in range(11 - a)
             for c in range(11 - a - b)]

    print("\nexact-arithmetic decisive census (Fraction TVD)")
    ex_gt20 = ex_eq20 = ex_gt25 = ex_gt30 = fl_gt20 = fl_gt30 = 0
    for (d, m, i), c in daily.items():
        if fd.is_equipoise(i) or i not in baselines[m]:
            continue
        ref = fd.baseline_for(baselines[m][i], d)["baseline_counts"]
        t = exact_tvd(c, ref)
        tf = fd.tvd(c, ref)
        ex_gt20 += t > Fraction(1, 5)
        ex_eq20 += t == Fraction(1, 5)
        ex_gt25 += t > Fraction(1, 4)
        ex_gt30 += t > Fraction(3, 10)
        fl_gt20 += tf > 0.20
        fl_gt30 += tf > 0.30
    print("  exact: above 0.20 %d, exactly 0.20 %d, above 0.25 %d, "
          "above 0.30 %d" % (ex_gt20, ex_eq20, ex_gt25, ex_gt30))
    print("  float (monitor path): above 0.20 %d, above 0.30 %d"
          % (fl_gt20, fl_gt30))
    non = []
    total = 0
    for m in fd.MODELS:
        for i, rec in baselines[m].items():
            if fd.is_equipoise(i):
                continue
            total += 1
            bc = fd.baseline_for(rec, lo)["baseline_counts"]
            if max(bc.values()) != sum(bc.values()):
                non.append("%s %s %s" % (fd.SHORT[m], i, vec(bc)))
    print("  decisive slots unanimous at the Aug 2 baseline: %d of %d; "
          "the others: %s" % (total - len(non), total, "; ".join(non)))
    probed = collections.Counter()
    for (d, m, i) in daily:
        probed[(d, m)] += 1
    complete = sum(1 for k, v in probed.items() if v == 68)
    print("  model-days with any probe row %d, with all 68 items %d"
          % (len(probed), complete))
    gated = sum(v for (d, m), v in probed.items()
                if any(x["date"] == d and x["model"] == m
                       and x["verdict"] not in ("ERROR", "ECHO_CHANGE")
                       for x in verdicts))
    print("  slot-days on verdict-bearing (gated) model-days %d of %d"
          % (gated, sum(probed.values())))
    ungated_days = {(v["date"], v["model"]) for v in verdicts
                    if v["verdict"] in ("ERROR", "ECHO_CHANGE")}
    ug = [(d, m, i, c) for (d, m, i), c in daily.items()
          if (d, m) in ungated_days]
    ug_float = ug_exact = 0
    ug_max = 0.0
    ug_minband = 1.0
    for d, m, i, c in ug:
        ref = fd.baseline_for(baselines[m][i], d)
        t = fd.tvd(c, ref["baseline_counts"])
        ug_float += t > ref["band"]["p99"]
        ug_exact += exact_tvd(c, ref["baseline_counts"]) > Fraction(
            round(ref["band"]["p99"] * 20), 20)
        ug_max = max(ug_max, t)
        ug_minband = min(ug_minband, ref["band"]["p99"])
    print("  ungated slot-days %d (decisive %d, equipoise %d); exceeding "
          "the band in force: float %d, exact %d; max TVD %.2f, min band "
          "%.2f" % (len(ug),
                    sum(1 for x in ug if not fd.is_equipoise(x[2])),
                    sum(1 for x in ug if fd.is_equipoise(x[2])),
                    ug_float, ug_exact, ug_max, ug_minband))
    single = [s for s, h in breaches.items() if len(h) == 1]
    print("  breached slots with exactly one entry: %d  %s"
          % (len(single), ["%s %s" % (fd.SHORT[m], fd.item_short(i))
                           for m, i in single]))

    print("\ndetection floor: smallest lattice TVD strictly above each "
          "slot's band, K=10 draws against the reference in force at the "
          "freeze")
    floor_exact = collections.Counter()
    floor_float = collections.Counter()
    float_lower = []
    for m in fd.MODELS:
        for i, rec in baselines[m].items():
            base = rec["baseline_counts"]
            band = rec["band"]["p99"]
            band_q = Fraction(round(band * 20), 20)
            exact_vals = [exact_tvd(dict(zip(fd.OPTIONS, c)), base)
                          for c in comps]
            float_vals = [fd.tvd(dict(zip(fd.OPTIONS, c)), base)
                          for c in comps]
            ex = min(v for v in exact_vals if v > band_q)
            fl = min(v for v in float_vals if v > band)
            floor_exact[float(ex)] += 1
            floor_float[round(fl, 2)] += 1
            if fl < float(ex) - 1e-9:
                unanimous = max(base.values()) == sum(base.values())
                float_lower.append((fd.SHORT[m], i, unanimous))
    print("  exact strict rule: %s" % dict(sorted(floor_exact.items())))
    print("  monitor float path: %s" % dict(sorted(floor_float.items())))
    print("  slots where the float path breaches at a lower lattice TVD "
          "than the exact rule: %d, of which unanimous at baseline %d"
          % (len(float_lower), sum(1 for x in float_lower if x[2])))
    hi_slots = [(fd.SHORT[m], i) for m in fd.MODELS
                for i, rec in baselines[m].items()
                if round(rec["band"]["p99"], 2) >= 0.5]
    print("  slots with band 0.50: %s" % hi_slots)

    print("\nnull by class (smoothed truth, monitor float compare, "
          "days per arm = verdict lines in window, breach probabilities "
          "on the reference in force at the freeze: the T1 convention)")
    days_m = collections.Counter(v["model"] for v in verdicts)
    probe_days_m = collections.Counter(
        v["model"] for v in verdicts
        if v["verdict"] not in ("ERROR", "ECHO_CHANGE"))
    p_slot = {}
    law_slot = {}
    for m in fd.MODELS:
        for i, rec in baselines[m].items():
            p, _ = slot_null(rec["baseline_counts"], rec["band"]["p99"],
                             "smoothed", comps)
            p_slot[(m, i)] = p
            ref0 = fd.baseline_for(rec, lo)
            _, law_slot[(m, i)] = slot_null(ref0["baseline_counts"],
                                            ref0["band"]["p99"],
                                            "smoothed", comps)
    e_eq = sum(p * days_m[m] for (m, i), p in p_slot.items()
               if fd.is_equipoise(i))
    e_dec = sum(p * days_m[m] for (m, i), p in p_slot.items()
                if not fd.is_equipoise(i))
    e_eq_probed = sum(p * probe_days_m[m] for (m, i), p in p_slot.items()
                      if fd.is_equipoise(i))
    e_dec_probed = sum(p * probe_days_m[m] for (m, i), p in p_slot.items()
                       if not fd.is_equipoise(i))
    obs_eq = sum(1 for v in verdicts for b in v["breached"]
                 if fd.is_equipoise(b["item_id"]))
    obs_dec = sum(1 for v in verdicts for b in v["breached"]
                  if not fd.is_equipoise(b["item_id"]))
    print("  E[entries] equipoise %.2f (observed %d), decisive %.2f "
          "(observed %d), total %.2f" % (e_eq, obs_eq, e_dec, obs_dec,
                                          e_eq + e_dec))
    print("  same under probed days only (%d model-days): equipoise %.2f, "
          "decisive %.2f, total %.2f"
          % (sum(probe_days_m.values()), e_eq_probed, e_dec_probed,
             e_eq_probed + e_dec_probed))
    tail_eq = binomial_sum_tail(
        [(days_m[m], p) for (m, i), p in p_slot.items()
         if fd.is_equipoise(i)], obs_eq)
    p_dec_zero = 1.0
    p_dec_zero_probed = 1.0
    for (m, i), p in p_slot.items():
        if not fd.is_equipoise(i):
            p_dec_zero *= (1 - p) ** days_m[m]
            p_dec_zero_probed *= (1 - p) ** probe_days_m[m]
    print("  P(equipoise entries >= %d) = %s;  P(decisive entries = 0) = %s"
          " (under probed days only %s)"
          % (obs_eq, fmt_p(tail_eq), fmt_p(p_dec_zero),
             fmt_p(p_dec_zero_probed)))

    print("\nconcentration under the empirical truth (c/n as the truth)")
    p_emp = {}
    for m in fd.MODELS:
        for i, rec in baselines[m].items():
            p_emp[(m, i)], _ = slot_null(rec["baseline_counts"],
                                         rec["band"]["p99"], "empirical",
                                         comps)
    tot = sum(p * days_m[m] for (m, i), p in p_emp.items())
    eq_mass = sum(p * days_m[m] for (m, i), p in p_emp.items()
                  if fd.is_equipoise(i))
    zero_dec = sum(1 for (m, i), p in p_emp.items()
                   if not fd.is_equipoise(i) and p == 0)
    share = eq_mass / tot if tot else float("nan")
    print("  decisive slots with zero breach mass %d of 225; equipoise "
          "share of breach mass %.3f; P(all %d entries on equipoise) %s;"
          " E[entries] %.2f"
          % (zero_dec, share, obs_eq, fmt_p(share ** obs_eq), tot))

    print("\nconditional direction test (given the observed threads and "
          "their entry counts; smoothed truth)")
    threads = [(s, hits) for s, hits in breaches.items() if len(hits) >= 3]
    def uni_prob(slot, m_entries):
        law = law_slot[slot]
        return sum(q ** m_entries for q in law.values())
    obs_uni = 0
    ps = []
    for (m, i), hits in threads:
        rec = baselines[m][i]
        dirs = set()
        for d in sorted(hits):
            c = daily.get((d, m, i))
            base = fd.baseline_for(rec, d)["baseline_counts"]
            n = sum(base.values())
            gains = {o: c.get(o, 0) / 10 - base.get(o, 0) / n
                     for o in fd.OPTIONS}
            top = max(gains.values())
            dirs.add([o for o in fd.OPTIONS if gains[o] == top][0])
        uni = len(dirs) == 1
        obs_uni += uni
        ps.append(uni_prob((m, i), len(hits)))
    print("  threads >=3: %d, unidirectional %d, E[unidirectional] %.2f, "
          "P(>= %d) = %s" % (len(threads), obs_uni, sum(ps), obs_uni,
                             fmt_p(poisson_binomial_tail(ps, obs_uni))))
    deep = [(s, h) for s, h in threads if len(h) >= 5]
    obs5 = 0
    ps5 = []
    for (m, i), hits in deep:
        rec = baselines[m][i]
        dirs = set()
        for d in sorted(hits):
            c = daily.get((d, m, i))
            base = fd.baseline_for(rec, d)["baseline_counts"]
            n = sum(base.values())
            gains = {o: c.get(o, 0) / 10 - base.get(o, 0) / n
                     for o in fd.OPTIONS}
            top = max(gains.values())
            dirs.add([o for o in fd.OPTIONS if gains[o] == top][0])
        obs5 += len(dirs) == 1
        ps5.append(uni_prob((m, i), len(hits)))
    print("  threads >=5: %d, unidirectional %d, E[unidirectional] %.2f, "
          "P(>= %d) = %s" % (len(deep), obs5, sum(ps5), obs5,
                             fmt_p(poisson_binomial_tail(ps5, obs5))))

    print("\nrecurrence against each thread's own pooled record "
          "(is one stationary multinomial enough?)")
    for (m, i), hits in sorted(threads, key=lambda t: (
            fd.MODELS.index(t[0][0]), t[0][1])):
        days = sorted(d for (d, mm, ii) in daily if mm == m and ii == i)
        pooled = collections.Counter()
        for d in days:
            pooled.update(daily[(d, m, i)])
        n = sum(pooled.values())
        probs = [pooled.get(o, 0) / n for o in fd.OPTIONS]
        vecs = collections.Counter(vec(daily[(d, m, i)]) for d in hits)
        top_vec, k = vecs.most_common(1)[0]
        cv = dict(zip(fd.OPTIONS, map(int, top_vec.split("/"))))
        p1 = multinomial_p(cv, probs)
        allk = sum(1 for d in days if vec(daily[(d, m, i)]) == top_vec)
        tail = sum(comb(len(days), j) * p1 ** j * (1 - p1) ** (len(days) - j)
                   for j in range(allk, len(days) + 1))
        seq = [fd.classify_day(daily[(d, m, i)],
                               fd.baseline_for(baselines[m][i], d))
               for d in days]
        z = runs_test(seq)
        print("  %s %s  pooled %s  top breach vector %s x%d of %d days  "
              "P(vector|pooled) %s  P(>= %d of %d) %s  runs z %s"
              % (fd.SHORT[m], fd.item_short(i), vec(pooled), top_vec, allk,
                 len(days), fmt_p(p1), allk, len(days), fmt_p(tail),
                 "%.2f" % z if z is not None else "-"))

    print("\nalarm load")
    probe_days = sorted({v["date"] for v in verdicts
                         if v["verdict"] not in ("ERROR", "ECHO_CHANGE")})
    entries = sum(len(v["breached"]) for v in verdicts)
    beh = [v for v in verdicts
           if v["verdict"] not in ("ERROR", "ECHO_CHANGE")]
    non_clean = sum(1 for v in beh if v["verdict"] != "CLEAN")
    events = sum(1 for v in beh if v["verdict"] == "EVENT")
    per_day = collections.Counter()
    for v in verdicts:
        per_day[v["date"]] += len(v["breached"])
    dist = collections.Counter(per_day[d] for d in probe_days)
    print("  %d entries over %d probe days = %.2f per probe day, %.1f per "
          "week; %d of %d behavioral model-days non-CLEAN (%.1f%%); %d "
          "EVENT model-days = %.1f per week; entries per probe day %s"
          % (entries, len(probe_days), entries / len(probe_days),
             7.0 * entries / len(probe_days), non_clean, len(beh),
             100.0 * non_clean / len(beh), events,
             7.0 * events / len(probe_days), dict(sorted(dist.items()))))

    print("\nfalse-breach expectation under the superseded haiku reference")
    tot_cur = sum(p for p in p_slot.values())
    rec = baselines["claude-haiku-4-5-20251001"]["eq_alert_spend_anomaly_v2"]
    sup = rec.get("superseded", [])
    if sup:
        p_cur = p_slot[("claude-haiku-4-5-20251001",
                        "eq_alert_spend_anomaly_v2")]
        p_new, _ = slot_null(rec["baseline_counts"], rec["band"]["p99"],
                             "smoothed", comps)
        print("  smoothed total with the Aug 2 reference in force %.4f "
              "(slot %.4f); with the current reference %.4f (slot %.4f)"
              % (tot_cur, p_cur, tot_cur - p_cur + p_new, p_new))

    print("\nK=30 bands recomputed from the committed baselines")
    source, bands30 = k30_bands(baselines)
    vals = sorted(bands30.values())
    hist = collections.Counter(round(v, 3) for v in vals)
    unan = [v for (m, i), v in bands30.items()
            if max(fd.baseline_for(baselines[m][i], lo)["baseline_counts"]
                   .values()) == 20]
    print("  source: %s; sims 10000, smooth 1.0, stored seeds"
          % source)
    print("  p99 min %.3f max %.3f; histogram %s"
          % (vals[0], vals[-1], dict(sorted(hist.items()))))
    print("  unanimous slots: %d, p99 min %.3f max %.3f"
          % (len(unan), min(unan), max(unan)))


if __name__ == "__main__":
    main()
