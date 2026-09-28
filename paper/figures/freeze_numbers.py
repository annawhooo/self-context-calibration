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


if __name__ == "__main__":
    main()
