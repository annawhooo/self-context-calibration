"""F2, the exact recurrence strip: sonnet fraud_scoring, day by day.

Daily answer distributions for claude-sonnet-4-6 /
eq_alert_fraud_scoring_v2 as stacked proportion bars, with the frozen
pooled baseline as the leftmost bar for reference. Days whose probe
returned the exact pure-A vector (10/0/0/0) are annotated: those are
the identical visits the oscillation claim leans on. Breach days
carry their verdict letter above the bar. Run:

  python paper/figures/f2_recurrence_strip.py
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

import figdata as fd

MODEL = "claude-sonnet-4-6"
ITEM = "eq_alert_fraud_scoring_v2"


def main():
    verdicts = fd.load_verdicts()
    daily = fd.load_daily()
    breaches = fd.breach_index(verdicts).get((MODEL, ITEM), {})
    dates, ran = fd.probe_dates(verdicts)
    base_rec = fd.baseline_for(fd.load_baselines()[MODEL][ITEM],
                               dates[0])

    bars = [("baseline", base_rec["baseline_counts"], None)]
    for date in dates:
        counts = daily.get((date, MODEL, ITEM))
        if counts is None and date not in ran.get(MODEL, ()):
            bars.append((date, None, None))          # provider error day
        elif counts is not None:
            bars.append((date, counts, breaches.get(date)))

    fig, ax = plt.subplots(figsize=(max(6.8, 0.24 * len(bars) + 1.2), 2.4))
    fd.style(ax)
    ax.grid(False)

    pure_a = []
    for x, (label, counts, verdict) in enumerate(bars):
        if counts is None:
            ax.text(x, 0.5, "no\nprobe", ha="center", va="center",
                    fontsize=5, color=fd.MUTED, rotation=90)
            continue
        n = sum(counts.values())
        bottom = 0.0
        for opt in fd.OPTIONS:
            share = counts.get(opt, 0) / n
            if share:
                ax.bar(x, share, bottom=bottom, width=0.8,
                       color=fd.CAT[opt], edgecolor="white",
                       linewidth=0.6)
                bottom += share
        if verdict:
            ax.text(x, 1.04, verdict[0], ha="center", fontsize=6.5,
                    color=fd.INK, fontweight="bold")
        if label != "baseline" and counts.get("A", 0) == n:
            pure_a.append(x)

    for x in pure_a:
        ax.plot(x, 1.13, marker="v", markersize=4, color=fd.INK,
                clip_on=False)

    ax.set_xticks(range(len(bars)))
    ax.set_xticklabels([b[0] if b[0] == "baseline"
                        else b[0][5:].replace("-", "/") for b in bars],
                       fontsize=6, rotation=90, color=fd.INK_2)
    ax.set_ylim(0, 1.12)
    ax.set_yticks((0, 0.5, 1.0))
    ax.set_yticklabels(("0", ".5", "1"), fontsize=7)
    ax.set_ylabel("answer share", fontsize=7.5, color=fd.INK_2)
    ax.axvline(0.5, color=fd.BASELINE_AXIS, linewidth=0.8, ymax=0.9)

    seen = {o for _, c, _ in bars if c for o in c}
    from matplotlib.lines import Line2D
    handles = [Patch(facecolor=fd.CAT[o], label="option %s" % o)
               for o in fd.OPTIONS if o in seen]
    handles.append(Line2D([], [], marker="v", linestyle="none",
                          markersize=4, color=fd.INK,
                          label="exact pure-A visit (10/0/0/0)"))
    ax.legend(handles=handles, loc="upper left",
              bbox_to_anchor=(0, -0.42), ncol=4, frameon=False,
              fontsize=6.5, labelcolor=fd.INK_2, handlelength=1.2)
    ax.set_title("%s / %s: daily answer distribution" % (
        fd.SHORT[MODEL], fd.item_short(ITEM)),
        fontsize=9, color=fd.INK, loc="left", pad=8)
    ax.text(1.0, 1.05, fd.datestamp(verdicts), transform=ax.transAxes,
            ha="right", fontsize=6, color=fd.MUTED)

    fd.savefig(fig, "f2_recurrence_strip")


if __name__ == "__main__":
    main()
