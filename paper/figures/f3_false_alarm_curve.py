"""F3, the false-alarm curve: quiet-slot exceedance versus band width.

For each item class (decisive, equipoise), pool every slot-day TVD
against baseline over the QUIET slots (slots with zero breach entries
in the committed verdict log, so the drifting threads do not
contaminate the noise estimate) and plot the fraction of slot-days
exceeding each candidate band width (strict inequality, the monitor's
breach test, over the K=10 TVD lattice). Shaded spans mark the
deployed band range and the declined K=30 band range from the dated
decline (probe/RECALIBRATION_POLICY_DRAFT_2026-08-16.md and the
handoff record). Run:

  python paper/figures/f3_false_alarm_curve.py
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import figdata as fd

LATTICE = [round(0.05 * i, 2) for i in range(15)]     # 0.00 .. 0.70
DECLINED_K30 = (0.267, 0.317)


def exceedance(tvds):
    n = len(tvds)
    return [(w, sum(1 for t in tvds if t > w) / n) for w in LATTICE]


def main():
    verdicts = fd.load_verdicts()
    daily = fd.load_daily()
    baselines = fd.load_baselines()
    breached_slots = set(fd.breach_index(verdicts))

    tvds = {"decisive": [], "equipoise": []}
    for (date, model, item), counts in daily.items():
        if model not in baselines or item not in baselines[model]:
            continue
        if (model, item) in breached_slots:
            continue
        cls = "equipoise" if fd.is_equipoise(item) else "decisive"
        ref = fd.baseline_for(baselines[model][item], date)
        tvds[cls].append(fd.tvd(counts, ref["baseline_counts"]))

    deployed = sorted({rec["band"]["p99"]
                       for items in baselines.values()
                       for rec in items.values()})
    dep_lo, dep_hi = round(min(deployed), 2), round(max(deployed), 2)

    fig, ax = plt.subplots(figsize=(4.6, 2.9))
    fd.style(ax)

    ax.axvspan(*DECLINED_K30, color=fd.CAT["D"], alpha=0.18, linewidth=0)
    ax.axvspan(dep_lo, dep_hi, color=fd.GRID, alpha=0.55, linewidth=0)
    ax.text(sum(DECLINED_K30) / 2, 0.55, "declined\nK=30 bands",
            ha="center", fontsize=6.5, color=fd.INK_2)
    ax.text((dep_lo + dep_hi) / 2, 0.55, "deployed\nbands",
            ha="center", fontsize=6.5, color=fd.INK_2)

    colors = {"decisive": fd.CAT["A"], "equipoise": fd.CAT["B"]}
    floor = 1e-4
    for cls in ("equipoise", "decisive"):
        pts = exceedance(tvds[cls])
        xs = [w for w, _ in pts]
        ys = [max(e, floor) for _, e in pts]
        ax.plot(xs, ys, color=colors[cls], linewidth=2,
                marker="o", markersize=3)
        ax.annotate("%s (%d slot-days)" % (cls, len(tvds[cls])),
                    (xs[5], ys[5]), textcoords="offset points",
                    xytext=(8, 6), fontsize=7, color=colors[cls],
                    fontweight="bold")

    ax.set_yscale("log")
    ax.set_ylim(floor, 1.5)
    ax.set_yticks((1, 1e-1, 1e-2, 1e-3, 1e-4))
    ax.set_yticklabels(("1", ".1", ".01", ".001", "0 obs."), fontsize=7)
    ax.set_xlim(0, 0.7)
    ax.set_xlabel("band width (TVD threshold, breach if strictly above)",
                  fontsize=7.5, color=fd.INK_2)
    ax.set_ylabel("fraction of quiet slot-days exceeding",
                  fontsize=7.5, color=fd.INK_2)
    ax.tick_params(labelsize=7)
    ax.set_title("Quiet-slot exceedance by class",
                 fontsize=9, color=fd.INK, loc="left", pad=8)
    ax.text(1.0, 1.03, fd.datestamp(verdicts), transform=ax.transAxes,
            ha="right", fontsize=6, color=fd.MUTED)

    fd.savefig(fig, "f3_false_alarm_curve")


if __name__ == "__main__":
    main()
