"""F1, the regime map: focal threads x days, state per cell.

The money figure. Rows are the focal threads (every model x item slot
with two or more breach entries in the committed verdict log, so the
set grows with the record and needs no hand-editing at the freeze).
Columns are probe days. Cell fill encodes the day's state under the
committed definitions (home, away), lightness-ordered so the figure
reads in grayscale; a letter glyph marks verdict-log breaches (E
EVENT, T TRANSIENT, U UNSTABLE); hatched cells are days the model
returned no probe (ERROR). Run from anywhere:

  python paper/figures/f1_regime_map.py
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch

import figdata as fd


def main():
    verdicts = fd.load_verdicts()
    daily = fd.load_daily()
    baselines = fd.load_baselines()
    breaches = fd.breach_index(verdicts)
    dates, ran = fd.probe_dates(verdicts)

    threads = sorted((slot for slot, hits in breaches.items()
                      if len(hits) >= 2),
                     key=lambda s: (fd.MODELS.index(s[0]), s[1]))

    fig_w = max(6.8, 0.185 * len(dates) + 1.9)
    fig, ax = plt.subplots(figsize=(fig_w, 0.32 * len(threads) + 1.1))
    ax.set_facecolor("white")

    for y, (model, item) in enumerate(threads):
        base_rec = baselines[model][item]
        for x, date in enumerate(dates):
            counts = daily.get((date, model, item))
            state = fd.classify_day(counts,
                                    fd.baseline_for(base_rec, date))
            if state is None and date not in ran.get(model, ()):
                ax.add_patch(Rectangle((x, y), 0.92, 0.82, fill=False,
                                       hatch="////", linewidth=0,
                                       edgecolor=fd.GRID))
                continue
            if state is None:
                continue
            verdict = breaches[(model, item)].get(date)
            fill = (fd.BREACH_FILL if verdict
                    else fd.AWAY_FILL if state == "away"
                    else fd.HOME_FILL)
            ax.add_patch(Rectangle((x, y), 0.92, 0.82, facecolor=fill,
                                   linewidth=0))
            if verdict:
                ax.text(x + 0.46, y + 0.41, verdict[0], ha="center",
                        va="center", fontsize=6.5, color="white",
                        fontweight="bold")

    ax.set_xlim(-0.1, len(dates))
    ax.set_ylim(len(threads), -0.2)
    ax.set_xticks([i + 0.46 for i in range(len(dates))])
    ax.set_xticklabels([d[5:].replace("-", "/") for d in dates],
                       fontsize=6, rotation=90, color=fd.INK_2)
    ax.set_yticks([i + 0.41 for i in range(len(threads))])
    ax.set_yticklabels(["%s  %s" % (fd.SHORT[m], fd.item_short(i))
                        for m, i in threads],
                       fontsize=7, color=fd.INK)
    for side in ax.spines.values():
        side.set_visible(False)
    ax.tick_params(length=0)

    legend = [
        Patch(facecolor=fd.HOME_FILL, label="home (baseline state)"),
        Patch(facecolor=fd.AWAY_FILL, label="away, no breach"),
        Patch(facecolor=fd.BREACH_FILL,
              label="breach (E event, T transient, U unstable)"),
        Patch(facecolor="white", edgecolor=fd.GRID, hatch="////",
              label="no probe recorded (error or pending)"),
    ]
    ax.legend(handles=legend, loc="upper center",
              bbox_to_anchor=(0.5, -0.30), ncol=2, frameon=False,
              fontsize=6.5, labelcolor=fd.INK_2, handlelength=1.4)
    ax.set_title("Focal threads by probe day: state and verdict",
                 fontsize=9, color=fd.INK, loc="left", pad=8)
    ax.text(1.0, 1.02, fd.datestamp(verdicts), transform=ax.transAxes,
            ha="right", fontsize=6, color=fd.MUTED)

    fd.savefig(fig, "f1_regime_map")


if __name__ == "__main__":
    main()
