"""F4, the phenotype grid: per-call commitment x excess movement.

One point per roster model. The x axis is per-call commitment: the
mean share of a slot-day's K samples on that day's modal answer, over
all slot-days (1.0 means every call agrees within a day). The y axis
is EXCESS temporal movement over equipoise slots: mean observed
slot-day TVD against the frozen baseline, minus the exact expected
TVD under a stationary smoothed baseline (figdata.expected_tvd, the
expected_false_breaches.py enumeration with the mean in place of the
tail). Raw mean TVD would charge a wide-but-stable sampler for its
own per-call spread; subtracting the stationary expectation makes the
axis read movement, not noise. The decisive class is near zero for
every model and is omitted from y to keep the plot readable.

The quadrant reading is the paper's: high commitment with low excess
is frozen-committed; low commitment with low excess is honest noise
(per-call spread the bands absorb); high commitment with high excess
is commit-and-flip, where per-call determinism masks temporal
instability. Identity is carried by direct labels, not color. Run:

  python paper/figures/f4_phenotype_grid.py
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import figdata as fd

LABEL_OFFSET = {"claude-haiku-4-5-20251001": (12, -12),
                "claude-sonnet-4-6": (6, 8),
                "gpt-5.6-terra": (0, 9),
                "gemini-3.6-flash": (-20, 8),
                "deepseek-v4-flash": (14, 6)}


def main():
    verdicts = fd.load_verdicts()
    daily = fd.load_daily()
    baselines = fd.load_baselines()

    expected = {(m, i): fd.expected_tvd(rec)
                for m, items in baselines.items()
                for i, rec in items.items() if fd.is_equipoise(i)}

    commit = {m: [] for m in fd.MODELS}
    excess = {m: [] for m in fd.MODELS}
    for (date, model, item), counts in daily.items():
        if model not in baselines or item not in baselines[model]:
            continue
        n = sum(counts.values())
        if not n:
            continue
        commit[model].append(max(counts.values()) / n)
        if fd.is_equipoise(item):
            obs = fd.tvd(counts,
                         baselines[model][item]["baseline_counts"])
            excess[model].append(obs - expected[(model, item)])

    fig, ax = plt.subplots(figsize=(3.8, 3.2))
    fd.style(ax)
    ax.grid(True, axis="both", color=fd.GRID, linewidth=0.7)
    ax.axhline(0, color=fd.BASELINE_AXIS, linewidth=0.9)

    xs = {m: sum(commit[m]) / len(commit[m]) for m in fd.MODELS}
    ys = {m: sum(excess[m]) / len(excess[m]) for m in fd.MODELS}
    for m in fd.MODELS:
        ax.plot(xs[m], ys[m], marker="o", markersize=7, color=fd.INK,
                markerfacecolor="white", markeredgewidth=1.4)
        dx, dy = LABEL_OFFSET[m]
        ax.annotate(fd.SHORT[m], (xs[m], ys[m]),
                    textcoords="offset points", xytext=(dx, dy),
                    ha="center", fontsize=7.5, color=fd.INK)

    ax.text(0.5, 0.06,
            "at zero, movement is fully explained\n"
            "by baseline sampling noise",
            transform=ax.transAxes, ha="center", va="bottom",
            fontsize=6.5, color=fd.MUTED)
    ax.set_xlabel("per-call commitment (mean modal share, all slots)",
                  fontsize=7.5, color=fd.INK_2)
    ax.set_ylabel("excess movement, equipoise slots\n"
                  "(mean TVD vs baseline minus stationary expectation)",
                  fontsize=7.5, color=fd.INK_2)
    ax.tick_params(labelsize=7)
    ax.set_title("Temporal phenotypes", fontsize=9, color=fd.INK,
                 loc="left", pad=8)
    ax.text(1.0, 1.03, fd.datestamp(verdicts), transform=ax.transAxes,
            ha="right", fontsize=6, color=fd.MUTED)

    fd.savefig(fig, "f4_phenotype_grid")
    for m in fd.MODELS:
        print("  %-13s commitment %.3f  excess %.4f  (%d eq slot-days)"
              % (fd.SHORT[m], xs[m], ys[m], len(excess[m])))


if __name__ == "__main__":
    main()
