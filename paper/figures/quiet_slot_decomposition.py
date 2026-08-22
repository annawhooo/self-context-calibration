"""Quiet-slot excess decomposition and thread direction analysis.

The analysis of record behind
paper/WORKING_NOTE_2026-08-22_quiet_slot_excess.md and the rebuilt
F4. Reads only the committed record; every expectation is exact
enumeration (figdata.expected_tvd_pair), no sampling anywhere, so
reruns are byte-stable for an unchanged record.

Part 1 splits each model's equipoise slots into breached threads
(any slot with a breach entry in the verdict log) and quiet slots,
and reports mean observed TVD against the frozen baseline next to
two exact expectations under a stationary empirical truth: probe
sampling alone, and probe plus n=20 baseline estimation noise. The
excess column is observed minus the second expectation. Part 2
reports mean consecutive-day self-TVD on quiet slots against the
exact two-draw floor E[TVD(K10, K10)]. Part 3 lists, for every slot
with three or more breach entries, the per-breach drift direction
(the option gaining most share over baseline, ties to the earliest
in A..D), which separates the unidirectional oscillators from the
mixed-direction wanderer. Run:

  python paper/figures/quiet_slot_decomposition.py
"""
import collections

import figdata as fd


def share(counts, o):
    n = sum(counts.values()) or 1
    return counts.get(o, 0) / n


def direction(counts, base):
    gains = {o: share(counts, o) - share(base, o) for o in fd.OPTIONS}
    top = max(gains.values())
    return [o for o in fd.OPTIONS if gains[o] == top][0]


def vec(counts):
    return "/".join(str(counts.get(o, 0)) for o in fd.OPTIONS)


def main():
    daily = fd.load_daily()
    baselines = fd.load_baselines()
    verdicts = fd.load_verdicts()
    breaches = fd.breach_index(verdicts)
    print("record: %s" % fd.datestamp(verdicts))

    obs = collections.defaultdict(list)
    for (date, model, item), counts in sorted(daily.items()):
        if not fd.is_equipoise(item) or item not in baselines.get(
                model, {}):
            continue
        group = "thread" if (model, item) in breaches else "quiet"
        obs[(model, group, item)].append(
            fd.tvd(counts, baselines[model][item]["baseline_counts"]))

    print("\npart 1: equipoise slot-day TVD vs exact expectations")
    print("model         group   slots  days  obs    exp"
          "    exp+b20  excess")
    for model in fd.MODELS:
        for group in ("quiet", "thread"):
            items = sorted(i for (m, g, i) in obs
                           if m == model and g == group)
            if not items:
                continue
            o = e1 = e2 = days = 0.0
            for item in items:
                rec = baselines[model][item]
                d = obs[(model, group, item)]
                days += len(d)
                o += sum(d) / len(d)
                e1 += fd.expected_tvd_pair(rec, base_n=None)
                e2 += fd.expected_tvd_pair(rec, base_n=20)
            k = len(items)
            o, e1, e2 = o / k, e1 / k, e2 / k
            print("%-13s %-7s %5d %5d  %.3f  %.3f  %.3f  %+.3f"
                  % (fd.SHORT[model], group, k, days, o, e1, e2,
                     o - e2))

    print("\npart 2: quiet-slot consecutive-day self-TVD vs exact"
          " two-draw floor")
    for model in fd.MODELS:
        pair_obs, floors = [], []
        for (m, g, item) in sorted(obs):
            if m != model or g != "quiet":
                continue
            rec = baselines[model][item]
            floor = fd.expected_tvd_pair(rec, probe_k=10, base_n=10)
            dates = sorted(d for (d, mm, i) in daily
                           if mm == model and i == item)
            for d1, d2 in zip(dates, dates[1:]):
                pair_obs.append(fd.tvd(daily[(d1, model, item)],
                                       daily[(d2, model, item)]))
                floors.append(floor)
        print("  %-13s obs %.3f  floor %.3f  excess %+.3f"
              % (fd.SHORT[model], sum(pair_obs) / len(pair_obs),
                 sum(floors) / len(floors),
                 sum(pair_obs) / len(pair_obs)
                 - sum(floors) / len(floors)))

    print("\npart 3: drift direction per breach, threads with >=3"
          " entries")
    for (model, item), hits in sorted(breaches.items()):
        if len(hits) < 3:
            continue
        base = baselines[model][item]["baseline_counts"]
        dirs = []
        for date in sorted(hits):
            counts = daily.get((date, model, item))
            dirs.append((date, hits[date][0],
                         direction(counts, base) if counts else "?"))
        uni = len({d for _, _, d in dirs if d != "?"}) == 1
        print("  %s %s  baseline %s  %s" % (
            fd.SHORT[model], fd.item_short(item), vec(base),
            "unidirectional" if uni else "MIXED"))
        for date, v, d in dirs:
            print("    %s  %s  toward %s" % (date, v, d))


if __name__ == "__main__":
    main()
