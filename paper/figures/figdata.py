"""Shared data access and style for the INTERCEPT paper figures.

Reads only committed inputs: the verdict log
(probe/monitor/verdicts.jsonl), the derived per-item daily counts
(probe/monitor/derived/daily_counts.jsonl), and the qualified
baselines (probe/monitor/baselines/*.json). No network, no raw rows.
Every figure script imports from here so the freeze re-render is a
re-run, not a rewrite: the scripts draw whatever the committed record
holds on the day they run.

Definitions match the committed record. TVD normalizes each side by
its own parsed count. A breach is strict inequality above the item's
band p99. HOME on a day means no breach and the day's modal answer
equals the baseline modal, ties counting as not-home
(probe/STEP_CHANGE_DECISION_RULE_2026-08-16.md).

Colors are the validated light-mode reference palette from the
data-viz method (categorical slots in fixed order, sequential blue,
neutral grays); figures are print-first, so state encodings are
lightness-ordered and read in grayscale.
"""
import os
import json
import glob
import collections

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, os.pardir, os.pardir))
MONITOR = os.path.join(REPO, "probe", "monitor")
OUT = os.path.join(HERE, "out")
OPTIONS = ("A", "B", "C", "D")

MODELS = ("claude-haiku-4-5-20251001", "claude-sonnet-4-6",
          "gpt-5.6-terra", "gemini-3.6-flash", "deepseek-v4-flash")
SHORT = {"claude-haiku-4-5-20251001": "haiku",
         "claude-sonnet-4-6": "sonnet",
         "gpt-5.6-terra": "gpt-terra",
         "gemini-3.6-flash": "gemini-flash",
         "deepseek-v4-flash": "deepseek"}

# Validated reference palette, light mode.
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE_AXIS = "#c3c2b7"
HOME_FILL = "#f0efec"
AWAY_FILL = "#86b6ef"      # sequential blue, step 250
BREACH_FILL = "#2a78d6"    # sequential blue, step 450
CAT = {"A": "#2a78d6", "B": "#eb6834", "C": "#1baf7a", "D": "#eda100"}


def _lines(path):
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                yield json.loads(line)


def load_verdicts():
    return list(_lines(os.path.join(MONITOR, "verdicts.jsonl")))


def load_daily(phase="monitor_probe"):
    """{(date, model, item_id): counts dict} for one phase."""
    rows = {}
    path = os.path.join(MONITOR, "derived", "daily_counts.jsonl")
    for r in _lines(path):
        if r["phase"] == phase:
            rows[(r["date"], r["model"], r["item_id"])] = r["counts"]
    return rows


def load_baselines():
    """{model: {item_id: item record}} for the five roster models."""
    out = {}
    for path in sorted(glob.glob(os.path.join(MONITOR, "baselines",
                                              "*.json"))):
        b = json.load(open(path, encoding="utf-8"))
        out[b["model"]] = b["items"]
    return out


def tvd(counts_a, counts_b):
    na = sum(counts_a.values()) or 1
    nb = sum(counts_b.values()) or 1
    return 0.5 * sum(abs(counts_a.get(o, 0) / na - counts_b.get(o, 0) / nb)
                     for o in OPTIONS)


def modal(counts):
    """Modal option, or None on a tie for the top count."""
    if not counts:
        return None
    top = max(counts.values())
    leaders = [o for o in OPTIONS if counts.get(o, 0) == top]
    return leaders[0] if len(leaders) == 1 else None


def breach_index(verdicts):
    """{(model, item_id): {date: item_verdict}} over all breach entries."""
    idx = collections.defaultdict(dict)
    for v in verdicts:
        for b in v.get("breached", []):
            idx[(v["model"], b["item_id"])][v["date"]] = b["item_verdict"]
    return dict(idx)


def probe_dates(verdicts):
    """All probe dates, and per model the dates with a non-ERROR probe."""
    dates = sorted({v["date"] for v in verdicts})
    ran = collections.defaultdict(set)
    for v in verdicts:
        if v["verdict"] != "ERROR":
            ran[v["model"]].add(v["date"])
    return dates, dict(ran)


def baseline_for(rec, date):
    """The reference in force on a date, honoring supersession.

    A re-baselined item record (probe/scripts/rebaseline_item.py)
    carries its prior references under "superseded", each with a
    validity window; the boundary convention is pinned there: a
    superseded reference governs THROUGH its valid_through day, and
    the active reference from the day after. Records without
    supersession return themselves, so call sites can route every
    lookup through here unconditionally.
    """
    for old in rec.get("superseded", []):
        if old["valid_from"] <= date <= old["valid_through"]:
            return old
    return rec


def ref_key(rec, date):
    """Cache key for per-reference computations on one item."""
    return baseline_for(rec, date).get("valid_from", "origin")


def is_equipoise(item_id):
    return item_id.startswith("eq_")


def item_short(item_id):
    for prefix in ("eq_alert_", "eq_access_", "eq_"):
        if item_id.startswith(prefix):
            return item_id[len(prefix):]
    return item_id


def classify_day(counts, base_rec):
    """'home' or 'away' under the committed definitions; None if no data."""
    if not counts:
        return None
    base = base_rec["baseline_counts"]
    breached = tvd(counts, base) > base_rec["band"]["p99"]
    if not breached and modal(counts) == modal(base):
        return "home"
    return "away"


def expected_tvd(base_rec, k=10, truth="empirical"):
    """Exact expected TVD of a K-draw probe under stationarity.

    The generating truth is the baseline itself: empirical c/n by
    default (the slot's frozen state taken as the fact of the
    matter), or the Laplace-smoothed (c+1)/(n+4) the bands are built
    on. TVD is measured against the empirical baseline either way,
    matching the monitor. Enumerates all compositions of k draws into
    the four options (286 at k=10) and weights each by its
    multinomial probability, the expected_false_breaches.py method
    with the mean in place of the tail mass. This is the
    sampling-noise floor a stationary slot pays; observed minus
    expected is movement. The smoothed truth charges every slot for
    the prior's off-modal mass and pushes near-unanimous slots
    negative; use it only when that conservatism is wanted.
    """
    from math import comb
    base = base_rec["baseline_counts"]
    n = sum(base.values())
    if truth == "smoothed":
        probs = [(base.get(o, 0) + 1) / (n + 4) for o in OPTIONS]
    else:
        probs = [base.get(o, 0) / n for o in OPTIONS]
    emp = {o: base.get(o, 0) for o in OPTIONS}
    total = 0.0
    for a in range(k + 1):
        for b in range(k + 1 - a):
            for c in range(k + 1 - a - b):
                d = k - a - b - c
                comp = dict(zip(OPTIONS, (a, b, c, d)))
                w = (comb(k, a) * comb(k - a, b) * comb(k - a - b, c)
                     * probs[0] ** a * probs[1] ** b
                     * probs[2] ** c * probs[3] ** d)
                total += w * tvd(comp, emp)
    return total


def _compositions(k):
    """All compositions of k draws into the four options, as an
    (m, 4) numpy int array with m = C(k+3, 3)."""
    import numpy as np
    comps = [(a, b, c, k - a - b - c)
             for a in range(k + 1)
             for b in range(k + 1 - a)
             for c in range(k + 1 - a - b)]
    return np.array(comps)


def _multinomial_weights(comps, probs):
    """Multinomial probability of each composition row under probs."""
    import numpy as np
    from math import lgamma
    k = int(comps[0].sum())
    logs = np.zeros(len(comps))
    lg = np.vectorize(lambda x: lgamma(x + 1))
    logs += lgamma(k + 1) - lg(comps).sum(axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        lp = np.where(comps > 0, comps * np.log(np.maximum(probs, 1e-300)),
                      0.0)
    return np.exp(logs + lp.sum(axis=1))


def expected_tvd_pair(base_rec, probe_k=10, base_n=20):
    """Exact E[TVD(probe, baseline)] with BOTH sides redrawn.

    The plug-in truth is the empirical baseline c/n. The probe is a
    probe_k-draw and the reference itself a base_n-draw from that
    truth, so the expectation charges the slot for probe sampling
    AND baseline estimation noise together (DESIGN_LIMITATIONS.md
    Limitation 3, propagated instead of ignored). base_n=None keeps
    the baseline exact and reduces to the single-draw expectation.
    Exact enumeration over both composition sets, no sampling.
    """
    import numpy as np
    base = base_rec["baseline_counts"]
    n = sum(base.values())
    probs = np.array([base.get(o, 0) / n for o in OPTIONS])
    pc = _compositions(probe_k)
    pw = _multinomial_weights(pc, probs)
    pf = pc / probe_k
    if base_n is None:
        ref_f = probs[None, :]
        ref_w = np.array([1.0])
    else:
        bc = _compositions(base_n)
        ref_w = _multinomial_weights(bc, probs)
        ref_f = bc / base_n
    tvds = 0.5 * np.abs(pf[:, None, :] - ref_f[None, :, :]).sum(axis=2)
    return float(pw @ tvds @ ref_w)


def style(ax):
    ax.set_facecolor("white")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(BASELINE_AXIS)
    ax.tick_params(colors=MUTED, labelcolor=INK_2, length=3, width=0.8)
    ax.grid(True, axis="y", color=GRID, linewidth=0.7)
    ax.set_axisbelow(True)


def savefig(fig, name):
    os.makedirs(OUT, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(OUT, "%s.%s" % (name, ext)),
                    dpi=200, bbox_inches="tight", facecolor="white")
    print("wrote %s.{pdf,png} in %s" % (name, os.path.relpath(OUT, REPO)))


def datestamp(verdicts):
    return "data through %s" % max(v["date"] for v in verdicts)
