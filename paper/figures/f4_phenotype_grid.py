"""F4, the phenotype grid: quiet slots hug zero, threads carry drift.

One column of marks per roster model. The x axis is per-call
commitment: the mean share of a slot-day's K samples on that day's
modal answer, over all slot-days (1.0 means every call agrees within
a day). The y axis is excess movement on equipoise slots: mean
observed slot-day TVD against the frozen baseline, minus the exact
expected TVD under a stationary empirical truth with BOTH probe
sampling and n=20 baseline estimation noise charged
(figdata.expected_tvd_pair; the single-draw expectation treats the
baseline as exact and silently penalizes wide-distribution models,
DESIGN_LIMITATIONS.md Limitation 3, which is how an earlier version
of this figure misread the honest-noise phenotype as movement).

Each model gets two marks: a circle for its QUIET equipoise slots
(no breach entry in the verdict log) and a cross for its breached
THREAD slots. The circles hug zero across a wide commitment range:
outside the focal threads, no model moves beyond its own sampling
arithmetic. The crosses sit an order of magnitude higher: the drift
lives in the threads, and F1 shows its two morphologies (discrete
unidirectional oscillation, and the diffuse mixed-direction wander).
Identity is carried by direct labels, not color. The full
decomposition table is quiet_slot_decomposition.py. Run:

  python paper/figures/f4_phenotype_grid.py
"""
import collections

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

import figdata as fd

LABEL_OFFSET = {"claude-haiku-4-5-20251001": (12, -13),
                "claude-sonnet-4-6": (8, 8),
                "gpt-5.6-terra": (-4, -16),
                "gemini-3.6-flash": (-6, 9),
                "deepseek-v4-flash": (14, 6)}


def main():
    daily = fd.load_daily()
    baselines = fd.load_baselines()
    verdicts = fd.load_verdicts()
    breaches = fd.breach_index(verdicts)

    commit = collections.defaultdict(list)
    obs = collections.defaultdict(lambda: collections.defaultdict(
        lambda: {"ref": None, "vals": []}))
    for (date, model, item), counts in sorted(daily.items()):
        if model not in baselines or item not in baselines[model]:
            continue
        n = sum(counts.values())
        if not n:
            continue
        commit[model].append(max(counts.values()) / n)
        if fd.is_equipoise(item):
            group = "thread" if (model, item) in breaches else "quiet"
            rec = baselines[model][item]
            ref = fd.baseline_for(rec, date)
            bucket = obs[(model, group)][(item, fd.ref_key(rec, date))]
            bucket["ref"] = ref
            bucket["vals"].append(fd.tvd(counts,
                                         ref["baseline_counts"]))

    def excess(model, group):
        buckets = obs.get((model, group))
        if not buckets:
            return None
        vals = []
        for bucket in buckets.values():
            exp = fd.expected_tvd_pair(bucket["ref"], base_n=20)
            days = bucket["vals"]
            vals.append(sum(days) / len(days) - exp)
        return sum(vals) / len(vals)

    fig, ax = plt.subplots(figsize=(3.8, 3.2))
    fd.style(ax)
    ax.grid(True, axis="both", color=fd.GRID, linewidth=0.7)
    ax.axhline(0, color=fd.BASELINE_AXIS, linewidth=0.9)

    for m in fd.MODELS:
        x = sum(commit[m]) / len(commit[m])
        yq = excess(m, "quiet")
        yt = excess(m, "thread")
        ax.plot(x, yq, marker="o", markersize=7, color=fd.INK,
                markerfacecolor="white", markeredgewidth=1.4)
        if yt is not None:
            ax.plot(x, yt, marker="x", markersize=6, color=fd.INK_2,
                    markeredgewidth=1.4)
        dx, dy = LABEL_OFFSET[m]
        ax.annotate(fd.SHORT[m], (x, yq), textcoords="offset points",
                    xytext=(dx, dy), ha="center", fontsize=7.5,
                    color=fd.INK)
        print("  %-13s commitment %.3f  quiet %+.4f  thread %s"
              % (fd.SHORT[m], x, yq,
                 "%+.4f" % yt if yt is not None else "-"))

    ax.set_xlabel("per-call commitment (mean modal share, all slots)",
                  fontsize=7.5, color=fd.INK_2)
    ax.set_ylabel("excess movement, equipoise slots\n(observed minus"
                  " exact sampling + baseline expectation)",
                  fontsize=7.5, color=fd.INK_2)
    ax.tick_params(labelsize=7)
    ax.legend(handles=[
        Line2D([], [], marker="o", linestyle="none", markersize=7,
               color=fd.INK, markerfacecolor="white",
               markeredgewidth=1.4, label="quiet slots (never breached)"),
        Line2D([], [], marker="x", linestyle="none", markersize=6,
               color=fd.INK_2, markeredgewidth=1.4,
               label="focal-thread slots")],
        loc="upper left", frameon=False, fontsize=6.5,
        labelcolor=fd.INK_2, handlelength=1.2)
    ax.set_title("Quiet slots hug zero; drift lives in threads",
                 fontsize=9, color=fd.INK, loc="left", pad=8)
    ax.text(1.0, 1.09, fd.datestamp(verdicts), transform=ax.transAxes,
            ha="right", fontsize=6, color=fd.MUTED)

    fd.savefig(fig, "f4_phenotype_grid")


if __name__ == "__main__":
    main()
