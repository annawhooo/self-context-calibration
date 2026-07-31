"""
analyze.py - pre-registered analysis for the convergence study
(convergence/PRE_REGISTRATION_CONVERGENCE.md, lock tag
prereg-lock-convergence-2026-07-24, including the Deviations entries
through 2026-07-25: test-retest supplement, modal-tie rule,
three-singleton Anthropic sensitivity). The pre-registration is the
spec; where this file and it disagree, the pre-registration wins and
the disagreement is a bug.

Input: convergence/results/convergence_rows.jsonl (extended row schema
written by convergence/collect.py). Rows partition by
(model, model_id_exact, arm): a model with more than one distinct echo
id inside an arm has already split into separate cells, and this
analyzer FAILS LOUDLY naming the ids rather than pooling or choosing;
resolution is human, per the pre-registered halt rule. Unparsed rows
(parsed null) drop from the per-item distribution and count toward the
per-model unparsed rate.

Integrity report (runs on any state, including partial data): per model
per arm, row count, unparsed count and rate, distinct echo ids with
per-id row counts, tie count over items, duplicate
(item_id, sample_index) detection. Printed always; written into the
results artifacts on a full run.

Primary computation (Arm A) refuses to run unless every Arm A cell
holds exactly 680 rows (68 items x K=10), stating what is missing.
Per model per item: the answer distribution over parsed rows; the modal
option if the mode is unique, a tied flag otherwise (Deviations
2026-07-25: a tied cell has no modal option and is a non-match for
every pair on that item). Per pair: agreement is the fraction of the 68
items with matching unique modal options. Within-lab mean is reported
lab-balanced (per-lab mean first, then across labs) and pair-weighted.
Primary quantity: lab-balanced within minus cross. Intervals: cluster
bootstrap over items, B = 2000, seed 20260722, percentile 90 percent;
per-model-per-item modals stay fixed, the 68 items are resampled with
replacement, and the full quantity is recomputed per replicate. The
decision output is exactly one of the two pre-committed reporting
sentences; absolute cross-lab agreement is always reported against 0.25
(chance on four options) and 1.00 (identical judgment), and is never
described as accuracy.

Voids and sensitivities. Unparsed rate over 0.20 on an arm voids that
model's reading for the arm (the model drops from that arm's agreement
computations and the void is reported). Sensitivity 1: primary
recomputed excluding any model with unparsed rate over 0.10.
Sensitivity 2: primary recomputed three times with each Anthropic model
as sole lab representative, range reported (Deviations 2026-07-25; the
recompute has no Anthropic within-lab pairs by construction).
Sensitivity 3: primary recomputed under set-intersection tie matching
(a pair matches on an item when the two modal sets intersect, which
reduces to the Deviations wording: either side's mode being a member of
the other side's tied modal set). Sensitivities are reported alongside
the primary, never substituted.

Secondary. Per-model p(modal) distribution over items, both arms; the
tier gradient within Anthropic, OpenAI, and DeepSeek only (vendor tier
order pinned below); Arm A versus Arm B agreement compared
descriptively with bootstrap intervals and the confounded-by-
construction label; the full pair agreement matrix for both arms, with
per-item and per-pair records retained to file.

Test-retest supplement (Deviations 2026-07-25), corroborative only.
For claude-haiku-4-5-20251001 and claude-sonnet-4-6: fresh Arm A
per-item distributions against results/confab_baseline_faithful.jsonl
rows for the same model id, reporting per-item modal match rate and
per-item total variation distance, summarized. Written to its own
artifacts (test_retest.json, test_retest.md), never entering the
primary. Opus is excluded and the exclusion stated in the output: the
faithful baseline ran claude-opus-4-7, a different model.

Output: deterministic artifacts under convergence/analysis/
(convergence_results.json, convergence_report.md, per_item.csv,
per_pair.csv, test_retest.json, test_retest.md). Identical inputs and
seed produce byte-identical outputs (sorted keys, LF line endings, no
timestamps); a repeated run overwrites rather than appends. The
directory is gitignored (convergence/.gitignore); a frozen result is
committed deliberately with git add -f.

Statistics use the standard library only. Bootstrap and percentile
conventions mirror analysis/analyze.py (random.Random(seed),
rng.choice over sorted item ids, linear-interpolation percentile).

Usage:
    python convergence/analyze.py [--rows PATH] [--baseline PATH]
        [--roster PATH] [--out-dir PATH] [--integrity-only]

--integrity-only prints the integrity report for whatever rows exist
and writes nothing, so a partial collection can be checked without
touching a frozen analysis directory.
"""

import os
import sys
import json
import math
import random
import argparse
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from items.items import ITEMS  # noqa: E402  (bank identity by import, never copy)

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ROWS = os.path.join(HERE, "results", "convergence_rows.jsonl")
DEFAULT_BASELINE = os.path.join(REPO, "results", "confab_baseline_faithful.jsonl")
DEFAULT_ROSTER = os.path.join(HERE, "models.json")
DEFAULT_OUT_DIR = os.path.join(HERE, "analysis")

OPTIONS = ("A", "B", "C", "D")
K_SAMPLES = 10
N_ITEMS = 68
GATE_ROWS = N_ITEMS * K_SAMPLES          # 680, the Arm A cell gate
BOOT_B = 2000
BOOT_SEED = 20260722
VOID_UNPARSED = 0.20                     # strictly greater voids the arm reading
SENS1_UNPARSED = 0.10                    # strictly greater excludes in sensitivity 1

ANTHROPIC = "anthropic"
# Vendor tier order for the gradient secondary, small to flagship, pinned
# from the pre-registration roster. GLM and Google contribute no gradient.
TIER_ORDER = {
    "anthropic": ("claude-haiku-4-5-20251001", "claude-sonnet-4-6",
                  "claude-opus-4-8"),
    "openai": ("gpt-5.6-terra", "gpt-5.6-sol"),
    "deepseek": ("deepseek-v4-flash", "deepseek-v4-pro"),
}

TEST_RETEST_MODELS = ("claude-haiku-4-5-20251001", "claude-sonnet-4-6")
TEST_RETEST_OPUS_NOTE = (
    "claude-opus-4-8 is excluded from this comparison: the faithful "
    "baseline ran claude-opus-4-7, a different model.")

# Pre-committed reporting sentences (pre-registration, Pre-committed
# reporting language). Exactly one is emitted, chosen by the interval.
DECISION_EXCLUDES = (
    "Within-lab agreement exceeds cross-lab agreement: within-lab "
    "(lab-balanced) {within:.4f}, cross-lab {cross:.4f}, difference "
    "{diff:+.4f}, 90% interval [{lo:+.4f}, {hi:+.4f}].")
DECISION_INCLUDES = (
    "No difference resolved at this N: within-lab (lab-balanced) "
    "{within:.4f}, cross-lab {cross:.4f}, difference {diff:+.4f}, "
    "90% interval [{lo:+.4f}, {hi:+.4f}].")
ABSOLUTE_LINE = (
    "Absolute cross-lab agreement {cross:.4f}, against 0.25 (chance on "
    "four options) and 1.00 (identical judgment). Agreement is not "
    "accuracy.")


class MultiEchoError(RuntimeError):
    """A model carries more than one distinct model_id_exact inside an
    arm: the data is already split into cells and pooling or choosing is
    forbidden. Resolution is human, per the pre-registered halt rule."""


class GateError(RuntimeError):
    """An Arm A cell is not exactly 680 rows; the primary refuses to
    run, stating what is missing."""


# ---------------------------------------------------------------------------
# Loading and integrity


def load_rows(path):
    """Read the rows jsonl. A torn or malformed line is counted, not
    fatal: the integrity report must run on any state."""
    rows, malformed = [], 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                malformed += 1
    return rows, malformed


def load_roster(path):
    """The pinned roster (convergence/models.json): which models are
    expected on which arm. Structure identical to collect.py's loader;
    re-read here so the analyzer never imports network plumbing."""
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    models = cfg.get("models")
    if not models:
        raise RuntimeError("no models in roster {}".format(path))
    return models


def expected_models(roster, arm):
    return [m for m in roster if arm in (m.get("arms") or [])]


def arm_rows(rows, arm):
    return [r for r in rows if r.get("arm") == arm]


def model_rows(rows, model):
    return [r for r in rows if r.get("model") == model]


def item_distribution(cell_rows):
    """Per item: Counter over parsed options, parsed row count, total
    row count. Unparsed rows drop from the distribution and count
    toward the unparsed rate."""
    dist = {}
    for r in cell_rows:
        d = dist.setdefault(r.get("item_id"), Counter())
        p = r.get("parsed")
        if p in OPTIONS:
            d[p] += 1
    return dist


def modal_info(counter):
    """Modal option of one item-model distribution. The modal option is
    the unique mode of the parsed distribution; tied modes mean no
    modal option (Deviations 2026-07-25). An empty distribution (all
    unparsed) also has no modal option."""
    if not counter:
        return {"modal": None, "tied": False, "modal_set": (),
                "p_modal": None, "n_parsed": 0}
    top = max(counter.values())
    modal_set = tuple(sorted(o for o in counter if counter[o] == top))
    n_parsed = sum(counter.values())
    unique = modal_set[0] if len(modal_set) == 1 else None
    return {"modal": unique, "tied": len(modal_set) > 1,
            "modal_set": modal_set, "p_modal": top / n_parsed,
            "n_parsed": n_parsed}


def integrity(rows, roster, malformed=0):
    """The integrity report, computable on any state. Per model per arm:
    row count, unparsed count and rate, distinct echo ids with counts,
    tie count over items, duplicate (item_id, sample_index) slots."""
    report = {"malformed_lines": malformed, "cells": []}
    seen_pairs = {(r.get("model"), r.get("arm")) for r in rows}
    expected = {(m["model"], arm) for arm in ("A", "B")
                for m in expected_models(roster, arm)}
    for model, arm in sorted(seen_pairs | expected):
        cell = [r for r in rows
                if r.get("model") == model and r.get("arm") == arm]
        echoes = Counter("(none)" if r.get("model_id_exact") is None
                         else r.get("model_id_exact") for r in cell)
        unparsed = sum(1 for r in cell if r.get("parsed") not in OPTIONS)
        slots = Counter((r.get("item_id"), r.get("sample_index"))
                        for r in cell)
        dupes = sorted(s for s, n in slots.items() if n > 1)
        dist = item_distribution(cell)
        ties = sum(1 for c in dist.values() if modal_info(c)["tied"])
        report["cells"].append({
            "model": model, "arm": arm, "expected": (model, arm) in expected,
            "rows": len(cell),
            "unparsed": unparsed,
            "unparsed_rate": (unparsed / len(cell)) if cell else None,
            "echo_ids": {k: v for k, v in sorted(echoes.items())},
            "tie_items": ties,
            "duplicate_slots": [list(s) for s in dupes],
        })
    return report


def check_multi_echo(rows):
    """Fail loudly when any model holds more than one distinct echo id
    inside an arm: the rows form separate cells and pooling or choosing
    is forbidden."""
    split = {}
    for r in rows:
        key = (r.get("model"), r.get("arm"))
        split.setdefault(key, set()).add(
            "(none)" if r.get("model_id_exact") is None
            else r.get("model_id_exact"))
    bad = {k: sorted(v) for k, v in split.items() if len(v) > 1}
    if bad:
        parts = ["{} arm {}: {}".format(m, a, ", ".join(ids))
                 for (m, a), ids in sorted(bad.items())]
        raise MultiEchoError(
            "multi-echo cells detected; the data is split and needs human "
            "partitioning before analysis. " + "; ".join(parts))


def check_gate(rows, roster):
    """The Arm A gate: every expected Arm A cell holds exactly 680 rows.
    Refusal states what is missing (or duplicated) per model."""
    problems = []
    a_rows = arm_rows(rows, "A")
    for m in expected_models(roster, "A"):
        cell = model_rows(a_rows, m["model"])
        if len(cell) != GATE_ROWS:
            slots = Counter((r.get("item_id"), r.get("sample_index"))
                            for r in cell)
            dupes = sum(n - 1 for n in slots.values() if n > 1)
            missing = GATE_ROWS - len(slots)
            problems.append(
                "{}: {} rows, expected {} ({} missing slot(s), {} "
                "duplicate row(s))".format(m["model"], len(cell), GATE_ROWS,
                                           missing, dupes))
    if problems:
        raise GateError(
            "Arm A cell gate failed; primary computation refuses to run. "
            + "; ".join(problems))


def check_item_bank(rows):
    """The rows must cover exactly the imported 68-item bank."""
    bank = {it["id"] for it in ITEMS}
    seen = {r.get("item_id") for r in rows}
    if rows and seen - bank:
        raise RuntimeError(
            "rows carry item ids outside the imported bank: {}".format(
                ", ".join(sorted(seen - bank))))


# ---------------------------------------------------------------------------
# Agreement machinery


def build_distributions(rows, arm, models):
    """Per model on one arm: per item parsed Counter and total row count
    (parsed plus unparsed), over the full imported bank."""
    dists, row_counts = {}, {}
    for m in models:
        cell = model_rows(arm_rows(rows, arm), m)
        dist = item_distribution(cell)
        totals = Counter(r.get("item_id") for r in cell)
        dists[m] = {it["id"]: dist.get(it["id"], Counter()) for it in ITEMS}
        row_counts[m] = {it["id"]: totals.get(it["id"], 0) for it in ITEMS}
    return dists, row_counts


def build_modals(dists):
    """Per model: per item modal_info from the built distributions."""
    return {m: {iid: modal_info(c) for iid, c in per_item.items()}
            for m, per_item in dists.items()}


def match_strict(a, b):
    """Pre-registered matching: both sides have a unique modal option and
    the options are equal. A tie (or an empty cell) on either side is a
    non-match."""
    return a["modal"] is not None and a["modal"] == b["modal"]


def match_intersection(a, b):
    """Sensitivity 3 (Deviations 2026-07-25): set-intersection tie
    matching. A pair matches on an item when the modal sets intersect;
    with a unique mode on one side this is exactly 'either side's mode
    is a member of the other side's tied modal set'."""
    return bool(set(a["modal_set"]) & set(b["modal_set"]))


def pair_matches(modals, model_a, model_b, matcher):
    """Per-item 0/1 match vector for one pair, in sorted item-id order."""
    ids = sorted(it["id"] for it in ITEMS)
    return [1 if matcher(modals[model_a][i], modals[model_b][i]) else 0
            for i in ids]


def build_pairs(models, labs, modals, matcher):
    """All unordered pairs with their labs and match vectors. Model
    order follows the given roster order; pair order is deterministic."""
    pairs = []
    for i, a in enumerate(models):
        for b in models[i + 1:]:
            pairs.append({
                "model_a": a, "model_b": b,
                "lab_a": labs[a], "lab_b": labs[b],
                "within": labs[a] == labs[b],
                "matches": pair_matches(modals, a, b, matcher),
            })
    return pairs


def aggregate(pairs, idx=None):
    """The primary quantity from pair match vectors, optionally over a
    bootstrap replicate's item indices. Lab-balanced within: per-lab
    mean of within-lab pair agreements first, then across labs.
    Pair-weighted within and the cross-lab mean alongside."""
    if idx is None:
        idx = list(range(len(ITEMS)))
    n = len(idx)
    agr = {}
    for p in pairs:
        agr[(p["model_a"], p["model_b"])] = \
            sum(p["matches"][i] for i in idx) / n
    within = [p for p in pairs if p["within"]]
    cross = [p for p in pairs if not p["within"]]
    by_lab = {}
    for p in within:
        by_lab.setdefault(p["lab_a"], []).append(
            agr[(p["model_a"], p["model_b"])])
    lab_means = {lab: sum(v) / len(v) for lab, v in sorted(by_lab.items())}
    within_bal = (sum(lab_means.values()) / len(lab_means)
                  if lab_means else None)
    within_pw = (sum(agr[(p["model_a"], p["model_b"])] for p in within)
                 / len(within)) if within else None
    cross_mean = (sum(agr[(p["model_a"], p["model_b"])] for p in cross)
                  / len(cross)) if cross else None
    diff = (within_bal - cross_mean
            if within_bal is not None and cross_mean is not None else None)
    return {"pair_agreement": agr, "lab_means": lab_means,
            "within_lab_balanced": within_bal,
            "within_pair_weighted": within_pw,
            "cross_mean": cross_mean, "diff": diff}


def percentile(xs, qtile):
    ys = sorted(xs)
    if not ys:
        return float("nan")
    pos = qtile * (len(ys) - 1)
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return ys[lo]
    frac = pos - lo
    return ys[lo] * (1.0 - frac) + ys[hi] * frac


def bootstrap_diff(pairs, B=BOOT_B, seed=BOOT_SEED):
    """Cluster bootstrap over items: resample the 68 items with
    replacement, keep per-model-per-item modals fixed, recompute the
    full quantity per replicate. Percentile 90 percent interval.
    Replicates where a component is undefined (no within or cross
    pairs) are impossible under the pre-registered roster and would be
    a bug; they raise rather than being skipped."""
    ids = sorted(it["id"] for it in ITEMS)
    index = {iid: k for k, iid in enumerate(ids)}
    rng = random.Random(seed)
    reps = []
    for _ in range(B):
        idx = [index[rng.choice(ids)] for _ in ids]
        d = aggregate(pairs, idx)["diff"]
        if d is None:
            raise RuntimeError("undefined primary quantity in a bootstrap "
                               "replicate; pair structure is degenerate")
        reps.append(d)
    return {"B": B, "seed": seed,
            "lo": percentile(reps, 0.05), "hi": percentile(reps, 0.95)}


def excludes_zero(lo, hi):
    return lo > 0.0 or hi < 0.0


def decision_sentence(point, boot):
    """Exactly one of the two pre-committed sentences, plus the always-
    reported absolute cross-lab line."""
    fields = {"within": point["within_lab_balanced"],
              "cross": point["cross_mean"], "diff": point["diff"],
              "lo": boot["lo"], "hi": boot["hi"]}
    tpl = (DECISION_EXCLUDES if excludes_zero(boot["lo"], boot["hi"])
           else DECISION_INCLUDES)
    return tpl.format(**fields), ABSOLUTE_LINE.format(cross=point["cross_mean"])


def primary_computation(rows, models, labs, matcher=match_strict,
                        B=BOOT_B, seed=BOOT_SEED, arm="A"):
    """Point estimates plus bootstrap interval for one model subset on
    one arm. Reused verbatim by the sensitivities and the Arm B
    descriptive read."""
    dists, row_counts = build_distributions(rows, arm, models)
    modals = build_modals(dists)
    pairs = build_pairs(models, labs, modals, matcher)
    point = aggregate(pairs)
    boot = bootstrap_diff(pairs, B=B, seed=seed)
    return {"models": list(models), "point": point, "boot": boot,
            "pairs": pairs, "modals": modals, "dists": dists,
            "row_counts": row_counts}


# ---------------------------------------------------------------------------
# Voids, sensitivities, secondary


def unparsed_rates(rows, roster, arm):
    """Per-model unparsed rate on one arm, over models present."""
    rates = {}
    for m in expected_models(roster, arm):
        cell = model_rows(arm_rows(rows, arm), m["model"])
        if cell:
            unparsed = sum(1 for r in cell if r.get("parsed") not in OPTIONS)
            rates[m["model"]] = unparsed / len(cell)
    return rates


def voided_models(rates):
    """Unparsed rate strictly over 0.20 voids the model's reading for
    the arm."""
    return sorted(m for m, r in rates.items() if r > VOID_UNPARSED)


def p_modal_summary(modals_for_model):
    """Summary of one model's p(modal) distribution over items (the
    self-collision / capability-gradient measure)."""
    ps = [v["p_modal"] for v in modals_for_model.values()
          if v["p_modal"] is not None]
    if not ps:
        return {"n_items": 0, "mean": None, "median": None,
                "min": None, "max": None}
    return {"n_items": len(ps), "mean": sum(ps) / len(ps),
            "median": percentile(ps, 0.5), "min": min(ps), "max": max(ps)}


def test_retest(fresh_rows, baseline_rows):
    """Corroborative test-retest supplement (Deviations 2026-07-25).
    Fresh Arm A distributions for the two carried-over model ids against
    the faithful baseline rows for the same id: per-item unique-modal
    match rate and per-item total variation distance, summarized. Never
    enters the primary. Opus is excluded (see TEST_RETEST_OPUS_NOTE)."""
    out = {"label": "corroborative; decides nothing in the primary",
           "opus_exclusion": TEST_RETEST_OPUS_NOTE, "models": {}}
    ids = sorted(it["id"] for it in ITEMS)
    for model in TEST_RETEST_MODELS:
        fresh = item_distribution(
            model_rows(arm_rows(fresh_rows, "A"), model))
        base = item_distribution(
            [r for r in baseline_rows
             if r.get("model") == model and r.get("phase") == "baseline"])
        items_out, tvds, matches, undefined = [], [], 0, 0
        for iid in ids:
            f = modal_info(fresh.get(iid, Counter()))
            b = modal_info(base.get(iid, Counter()))
            if f["n_parsed"] and b["n_parsed"]:
                fc, bc = fresh.get(iid, Counter()), base.get(iid, Counter())
                tvd = 0.5 * sum(
                    abs(fc.get(o, 0) / f["n_parsed"]
                        - bc.get(o, 0) / b["n_parsed"]) for o in OPTIONS)
            else:
                tvd, undefined = None, undefined + 1
            match = (f["modal"] is not None and f["modal"] == b["modal"])
            matches += 1 if match else 0
            if tvd is not None:
                tvds.append(tvd)
            items_out.append({
                "item_id": iid, "modal_fresh": f["modal"],
                "tied_fresh": f["tied"], "modal_baseline": b["modal"],
                "tied_baseline": b["tied"], "match": match, "tvd": tvd,
                "n_parsed_fresh": f["n_parsed"],
                "n_parsed_baseline": b["n_parsed"]})
        out["models"][model] = {
            "items": items_out,
            "modal_match_rate": matches / len(ids),
            "n_items": len(ids), "n_matches": matches,
            "tvd_mean": sum(tvds) / len(tvds) if tvds else None,
            "tvd_median": percentile(tvds, 0.5) if tvds else None,
            "tvd_max": max(tvds) if tvds else None,
            "items_tvd_undefined": undefined,
        }
    return out


def compare_runs(rows_a, rows_b, arm, label_a, label_b):
    """Distribution distance between two convergence-schema row files
    for the same models on the same bank. Same measures and scale as
    test_retest, so a same-day self-distance is directly comparable to
    the three-week supplement. Not part of the pre-registered analysis:
    an instrument characterization, reported on its own."""
    out = {"label": "instrument characterization; not part of the "
                    "pre-registered analysis",
           "arm": arm, "file_a": label_a, "file_b": label_b, "models": {}}
    ids = sorted(it["id"] for it in ITEMS)
    models = sorted({r.get("model") for r in rows_a}
                    & {r.get("model") for r in rows_b})
    for model in models:
        da = item_distribution(model_rows(arm_rows(rows_a, arm), model))
        db = item_distribution(model_rows(arm_rows(rows_b, arm), model))
        items_out, tvds, matches, undefined = [], [], 0, 0
        for iid in ids:
            ca, cb = da.get(iid, Counter()), db.get(iid, Counter())
            ia, ib = modal_info(ca), modal_info(cb)
            if ia["n_parsed"] and ib["n_parsed"]:
                na, nb = ia["n_parsed"], ib["n_parsed"]
                tvd = 0.5 * sum(abs(ca.get(o, 0) / na - cb.get(o, 0) / nb)
                                for o in OPTIONS)
                tvds.append(tvd)
                if ia["modal"] and ib["modal"] and ia["modal"] == ib["modal"]:
                    matches += 1
                elif ia["modal"] is None or ib["modal"] is None:
                    undefined += 1
                items_out.append(
                    {"item_id": iid, "tvd": round(tvd, 4),
                     "modal_a": ia["modal"], "modal_b": ib["modal"],
                     "match": bool(ia["modal"] and ib["modal"]
                                   and ia["modal"] == ib["modal"])})
        n = len(tvds)
        out["models"][model] = {
            "n_items_compared": n,
            "modal_matches": matches,
            "modal_undefined_either_side": undefined,
            "mean_tvd": round(sum(tvds) / n, 4) if n else None,
            "max_tvd": round(max(tvds), 4) if n else None,
            "full_flips": sum(1 for t in tvds if t == 1.0),
            "items": items_out}
    return out


def analyze(rows, roster, baseline_rows, B=BOOT_B, seed=BOOT_SEED,
            malformed=0):
    """The full pre-registered computation. Raises MultiEchoError or
    GateError rather than computing on bad partitions."""
    check_item_bank(rows)
    check_multi_echo(rows)
    check_gate(rows, roster)

    labs = {m["model"]: m["provider"] for m in roster}
    result = {"parameters": {"B": B, "seed": seed, "gate_rows": GATE_ROWS,
                             "void_unparsed": VOID_UNPARSED,
                             "sens1_unparsed": SENS1_UNPARSED},
              "integrity": integrity(rows, roster, malformed)}

    # Voids, both arms.
    rates = {arm: unparsed_rates(rows, roster, arm) for arm in ("A", "B")}
    voids = {arm: voided_models(rates[arm]) for arm in ("A", "B")}
    result["unparsed_rates"] = rates
    result["voided"] = voids

    def arm_models(arm):
        return [m["model"] for m in expected_models(roster, arm)
                if m["model"] not in voids[arm]]

    a_models = arm_models("A")

    # Primary, Arm A.
    primary = primary_computation(rows, a_models, labs, B=B, seed=seed)
    sentence, absolute = decision_sentence(primary["point"], primary["boot"])
    result["primary"] = {
        "models": primary["models"],
        "voided_excluded": voids["A"],
        "within_lab_balanced": primary["point"]["within_lab_balanced"],
        "within_pair_weighted": primary["point"]["within_pair_weighted"],
        "cross_mean": primary["point"]["cross_mean"],
        "lab_means": primary["point"]["lab_means"],
        "diff": primary["point"]["diff"],
        "interval": {"lo": primary["boot"]["lo"], "hi": primary["boot"]["hi"]},
        "decision_sentence": sentence,
        "absolute_sentence": absolute,
    }

    # Sensitivity 1: exclude unparsed rate > 0.10.
    s1_excluded = sorted(m for m in a_models
                         if rates["A"].get(m, 0.0) > SENS1_UNPARSED)
    s1_models = [m for m in a_models if m not in s1_excluded]
    s1 = primary_computation(rows, s1_models, labs, B=B, seed=seed)
    result["sensitivity_1_unparsed"] = {
        "excluded": s1_excluded, "models": s1["models"],
        "within_lab_balanced": s1["point"]["within_lab_balanced"],
        "cross_mean": s1["point"]["cross_mean"],
        "diff": s1["point"]["diff"],
        "interval": {"lo": s1["boot"]["lo"], "hi": s1["boot"]["hi"]},
        "identical_to_primary": s1_excluded == [],
    }

    # Sensitivity 2: each Anthropic model as sole lab representative.
    anth = [m for m in a_models if labs[m] == ANTHROPIC]
    s2_runs = {}
    for solo in anth:
        subset = [m for m in a_models if labs[m] != ANTHROPIC or m == solo]
        r = primary_computation(rows, subset, labs, B=B, seed=seed)
        s2_runs[solo] = {
            "models": r["models"],
            "within_lab_balanced": r["point"]["within_lab_balanced"],
            "cross_mean": r["point"]["cross_mean"],
            "diff": r["point"]["diff"],
            "interval": {"lo": r["boot"]["lo"], "hi": r["boot"]["hi"]},
        }
    diffs = [v["diff"] for v in s2_runs.values()]
    result["sensitivity_2_single_anthropic"] = {
        "runs": s2_runs,
        "diff_range": ([min(diffs), max(diffs)] if diffs else None),
        "note": "each recompute removes all Anthropic within-lab pairs "
                "by construction; no single representative is designated",
    }

    # Sensitivity 3: set-intersection tie matching.
    s3 = primary_computation(rows, a_models, labs,
                             matcher=match_intersection, B=B, seed=seed)
    result["sensitivity_3_tie_intersection"] = {
        "models": s3["models"],
        "within_lab_balanced": s3["point"]["within_lab_balanced"],
        "cross_mean": s3["point"]["cross_mean"],
        "diff": s3["point"]["diff"],
        "interval": {"lo": s3["boot"]["lo"], "hi": s3["boot"]["hi"]},
    }

    # Secondary: p(modal) both arms, tier gradient, Arm B descriptive
    # aggregates, full pair matrices.
    secondary = {"p_modal": {}, "tier_gradient": {}, "arms": {}}
    arm_full = {"A": primary}
    if arm_models("B"):
        arm_full["B"] = primary_computation(rows, arm_models("B"), labs,
                                            B=B, seed=seed, arm="B")
    for arm, full in sorted(arm_full.items()):
        secondary["p_modal"][arm] = {
            m: p_modal_summary(full["modals"][m]) for m in full["models"]}
        secondary["arms"][arm] = {
            "within_lab_balanced": full["point"]["within_lab_balanced"],
            "within_pair_weighted": full["point"]["within_pair_weighted"],
            "cross_mean": full["point"]["cross_mean"],
            "lab_means": full["point"]["lab_means"],
            "diff": full["point"]["diff"],
            "interval": {"lo": full["boot"]["lo"], "hi": full["boot"]["hi"]},
            "pair_agreement": {
                "{}|{}".format(a, b): v
                for (a, b), v in sorted(full["point"]["pair_agreement"].items())},
        }
    for lab, order in sorted(TIER_ORDER.items()):
        secondary["tier_gradient"][lab] = {
            arm: [{"model": m,
                   "p_modal_mean": secondary["p_modal"][arm][m]["mean"]}
                  for m in order if m in secondary["p_modal"].get(arm, {})]
            for arm in sorted(arm_full)}
    secondary["arm_comparison_label"] = (
        "Arm A versus Arm B is descriptive and confounded by "
        "construction: reasoning means adaptive on one lab, a token "
        "budget on another, and always-on elsewhere, and Arm B adds "
        "Google. It is the deployed-configuration comparison, never a "
        "controlled contrast.")
    result["secondary"] = secondary
    result["arm_full"] = arm_full  # internal, for the writers; not serialized

    # Test-retest supplement, separate artifact, never entering the primary.
    result["test_retest"] = test_retest(rows, baseline_rows)
    return result


# ---------------------------------------------------------------------------
# Deterministic writers (sorted keys, LF endings, no timestamps)


def _write(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def write_json(path, obj):
    _write(path, json.dumps(obj, sort_keys=True, indent=2) + "\n")


def per_item_csv(result):
    lines = ["arm,model,item_id,n_rows,n_parsed,n_A,n_B,n_C,n_D,"
             "modal,tied,modal_set,p_modal"]
    for arm, full in sorted(result["arm_full"].items()):
        for m in sorted(full["models"]):
            modals = full["modals"][m]
            for iid in sorted(modals):
                v = modals[iid]
                c = full["dists"][m][iid]
                lines.append(",".join([
                    arm, m, iid, str(full["row_counts"][m][iid]),
                    str(v["n_parsed"])]
                    + [str(c.get(o, 0)) for o in OPTIONS]
                    + [v["modal"] or "", "1" if v["tied"] else "0",
                       "|".join(v["modal_set"]),
                       "" if v["p_modal"] is None else "%.6f" % v["p_modal"]]))
    return "\n".join(lines) + "\n"


def per_pair_csv(result):
    lines = ["arm,model_a,model_b,lab_a,lab_b,within_lab,agreement"]
    for arm, full in sorted(result["arm_full"].items()):
        agr = full["point"]["pair_agreement"]
        for p in full["pairs"]:
            key = (p["model_a"], p["model_b"])
            lines.append(",".join([
                arm, p["model_a"], p["model_b"], p["lab_a"], p["lab_b"],
                "1" if p["within"] else "0", "%.6f" % agr[key]]))
    return "\n".join(lines) + "\n"


def fmt(x, digits=4):
    return "n/a" if x is None else ("%.*f" % (digits, x))


def report_md(result):
    out = []
    w = out.append
    w("# Convergence analysis (pre-registered)")
    w("")
    w("Spec: convergence/PRE_REGISTRATION_CONVERGENCE.md, lock tag "
      "prereg-lock-convergence-2026-07-24, Deviations through 2026-07-25. "
      "Cluster bootstrap over items, B = {}, seed {}, percentile 90% "
      "intervals.".format(result["parameters"]["B"],
                          result["parameters"]["seed"]))
    w("")
    w("## Integrity")
    w("")
    w("| model | arm | rows | unparsed | rate | echo ids | tie items | dup slots |")
    w("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for c in result["integrity"]["cells"]:
        w("| {} | {} | {} | {} | {} | {} | {} | {} |".format(
            c["model"], c["arm"], c["rows"], c["unparsed"],
            fmt(c["unparsed_rate"]), "; ".join(
                "{} ({})".format(k, v) for k, v in c["echo_ids"].items()),
            c["tie_items"], len(c["duplicate_slots"])))
    if result["integrity"]["malformed_lines"]:
        w("")
        w("Malformed input lines skipped: {}.".format(
            result["integrity"]["malformed_lines"]))
    w("")
    w("## Voids")
    w("")
    for a in ("A", "B"):
        v = result["voided"][a]
        w("- Arm {}: {}".format(
            a, "voided (unparsed rate > 0.20): " + ", ".join(v) if v
            else "no model voided (all unparsed rates at or below 0.20)."))
    w("")
    p = result["primary"]
    w("## Primary (Arm A)")
    w("")
    w("Models: {}.".format(", ".join(p["models"])))
    w("")
    w("| quantity | value |")
    w("| --- | --- |")
    w("| within-lab, lab-balanced | {} |".format(fmt(p["within_lab_balanced"])))
    w("| within-lab, pair-weighted | {} |".format(fmt(p["within_pair_weighted"])))
    for lab, v in sorted(p["lab_means"].items()):
        w("| within-lab mean, {} | {} |".format(lab, fmt(v)))
    w("| cross-lab mean | {} |".format(fmt(p["cross_mean"])))
    w("| difference (lab-balanced within minus cross) | {} |".format(fmt(p["diff"])))
    w("| 90% interval | [{}, {}] |".format(fmt(p["interval"]["lo"]),
                                           fmt(p["interval"]["hi"])))
    w("")
    w("**Decision:** " + p["decision_sentence"])
    w("")
    w(p["absolute_sentence"])
    w("")
    w("## Sensitivities (reported alongside the primary, never substituted)")
    w("")
    s1 = result["sensitivity_1_unparsed"]
    w("### 1. Excluding unparsed rate > 0.10")
    w("")
    w("Excluded: {}. Within (lab-balanced) {}, cross {}, difference {}, "
      "90% interval [{}, {}].{}".format(
          ", ".join(s1["excluded"]) if s1["excluded"] else "none",
          fmt(s1["within_lab_balanced"]), fmt(s1["cross_mean"]),
          fmt(s1["diff"]), fmt(s1["interval"]["lo"]),
          fmt(s1["interval"]["hi"]),
          " Identical to the primary (no model excluded)."
          if s1["identical_to_primary"] else ""))
    w("")
    s2 = result["sensitivity_2_single_anthropic"]
    w("### 2. Single Anthropic representative (three recomputes)")
    w("")
    w("| sole representative | within (lab-balanced) | cross | diff | 90% interval |")
    w("| --- | --- | --- | --- | --- |")
    for solo, r in sorted(s2["runs"].items()):
        w("| {} | {} | {} | {} | [{}, {}] |".format(
            solo, fmt(r["within_lab_balanced"]), fmt(r["cross_mean"]),
            fmt(r["diff"]), fmt(r["interval"]["lo"]), fmt(r["interval"]["hi"])))
    w("")
    w("Difference range across the three recomputes: [{}, {}]. {}.".format(
        fmt(s2["diff_range"][0]), fmt(s2["diff_range"][1]), s2["note"]))
    w("")
    s3 = result["sensitivity_3_tie_intersection"]
    w("### 3. Set-intersection tie matching")
    w("")
    w("Within (lab-balanced) {}, cross {}, difference {}, 90% interval "
      "[{}, {}].".format(fmt(s3["within_lab_balanced"]), fmt(s3["cross_mean"]),
                         fmt(s3["diff"]), fmt(s3["interval"]["lo"]),
                         fmt(s3["interval"]["hi"])))
    w("")
    w("## Secondary")
    w("")
    sec = result["secondary"]
    w("### p(modal) over items (self-collision), by arm")
    w("")
    w("| arm | model | mean | median | min | max |")
    w("| --- | --- | --- | --- | --- | --- |")
    for arm in sorted(sec["p_modal"]):
        for m in sorted(sec["p_modal"][arm]):
            s = sec["p_modal"][arm][m]
            w("| {} | {} | {} | {} | {} | {} |".format(
                arm, m, fmt(s["mean"]), fmt(s["median"]),
                fmt(s["min"]), fmt(s["max"])))
    w("")
    w("### Tier gradient (within Anthropic, OpenAI, DeepSeek only; "
      "vendor tier order, small to flagship)")
    w("")
    w("| lab | arm | tier order: mean p(modal) |")
    w("| --- | --- | --- |")
    for lab in sorted(sec["tier_gradient"]):
        for arm in sorted(sec["tier_gradient"][lab]):
            seq = sec["tier_gradient"][lab][arm]
            w("| {} | {} | {} |".format(lab, arm, " -> ".join(
                "{} {}".format(e["model"], fmt(e["p_modal_mean"]))
                for e in seq)))
    w("")
    w("### Arm A versus Arm B (descriptive)")
    w("")
    w(sec["arm_comparison_label"])
    w("")
    w("| arm | within (lab-balanced) | within (pair-weighted) | cross | diff | 90% interval |")
    w("| --- | --- | --- | --- | --- | --- |")
    for arm in sorted(sec["arms"]):
        a = sec["arms"][arm]
        w("| {} | {} | {} | {} | {} | [{}, {}] |".format(
            arm, fmt(a["within_lab_balanced"]), fmt(a["within_pair_weighted"]),
            fmt(a["cross_mean"]), fmt(a["diff"]),
            fmt(a["interval"]["lo"]), fmt(a["interval"]["hi"])))
    w("")
    w("### Pair agreement matrices")
    w("")
    for arm, full in sorted(result["arm_full"].items()):
        w("Arm {} (models in roster order):".format(arm))
        w("")
        models = full["models"]
        agr = full["point"]["pair_agreement"]
        w("| | " + " | ".join(models) + " |")
        w("| --- |" + " --- |" * len(models))
        for a in models:
            cells = []
            for b in models:
                if a == b:
                    cells.append("-")
                else:
                    key = (a, b) if (a, b) in agr else (b, a)
                    cells.append(fmt(agr[key]))
            w("| {} | ".format(a) + " | ".join(cells) + " |")
        w("")
    w("Per-item and per-pair records: per_item.csv, per_pair.csv. "
      "Test-retest supplement (corroborative, never entering the "
      "primary): test_retest.md / test_retest.json.")
    w("")
    return "\n".join(out)


def test_retest_md(tr):
    out = []
    w = out.append
    w("# Test-retest supplement (corroborative)")
    w("")
    w("Declared in PRE_REGISTRATION_CONVERGENCE.md Deviations, "
      "2026-07-25, before any Anthropic collection. This comparison is "
      "corroborative only, is reported separately from the primary "
      "analysis, and decides nothing in it.")
    w("")
    w(tr["opus_exclusion"])
    w("")
    w("| model | modal match rate | matches / items | TVD mean | TVD median | TVD max |")
    w("| --- | --- | --- | --- | --- | --- |")
    for m in sorted(tr["models"]):
        s = tr["models"][m]
        w("| {} | {} | {}/{} | {} | {} | {} |".format(
            m, fmt(s["modal_match_rate"]), s["n_matches"], s["n_items"],
            fmt(s["tvd_mean"]), fmt(s["tvd_median"]), fmt(s["tvd_max"])))
    w("")
    for m in sorted(tr["models"]):
        s = tr["models"][m]
        w("## {}".format(m))
        w("")
        w("| item | fresh modal | baseline modal | match | TVD |")
        w("| --- | --- | --- | --- | --- |")

        def label(modal, tied):
            return modal if modal is not None else ("tie" if tied else "none")

        for it in s["items"]:
            w("| {} | {} | {} | {} | {} |".format(
                it["item_id"],
                label(it["modal_fresh"], it["tied_fresh"]),
                label(it["modal_baseline"], it["tied_baseline"]),
                "yes" if it["match"] else "no", fmt(it["tvd"])))
        w("")
    return "\n".join(out)


def write_outputs(result, out_dir):
    """All artifacts, overwriting deterministically. The internal
    arm_full block (match vectors, modal caches) is not serialized; the
    csvs are its durable form."""
    os.makedirs(out_dir, exist_ok=True)
    serializable = {k: v for k, v in result.items()
                    if k not in ("arm_full", "test_retest")}
    write_json(os.path.join(out_dir, "convergence_results.json"), serializable)
    _write(os.path.join(out_dir, "convergence_report.md"),
           report_md(result) + "\n")
    _write(os.path.join(out_dir, "per_item.csv"), per_item_csv(result))
    _write(os.path.join(out_dir, "per_pair.csv"), per_pair_csv(result))
    write_json(os.path.join(out_dir, "test_retest.json"),
               result["test_retest"])
    _write(os.path.join(out_dir, "test_retest.md"),
           test_retest_md(result["test_retest"]) + "\n")


def print_integrity(report):
    print("Integrity report")
    if report["malformed_lines"]:
        print("  malformed lines skipped: {}".format(report["malformed_lines"]))
    for c in report["cells"]:
        print("  {:<26} arm {}  rows {:>4}  unparsed {:>3} ({})  echo ids "
              "{}  tie items {}  dup slots {}".format(
                  c["model"], c["arm"], c["rows"], c["unparsed"],
                  fmt(c["unparsed_rate"]),
                  ", ".join(c["echo_ids"]) or "-", c["tie_items"],
                  len(c["duplicate_slots"])))


def main():
    ap = argparse.ArgumentParser(
        description="Pre-registered convergence analysis. Integrity "
                    "report on any state; primary refuses to run unless "
                    "every Arm A cell holds exactly 680 rows.")
    ap.add_argument("--rows", default=DEFAULT_ROWS)
    ap.add_argument("--baseline", default=DEFAULT_BASELINE,
                    help="faithful baseline jsonl for the corroborative "
                         "test-retest supplement")
    ap.add_argument("--roster", default=DEFAULT_ROSTER)
    ap.add_argument("--out-dir", default=DEFAULT_OUT_DIR)
    ap.add_argument("--integrity-only", action="store_true",
                    help="print the integrity report and write nothing")
    ap.add_argument("--compare-runs", nargs=2, metavar=("FILE_A", "FILE_B"),
                    help="instrument characterization: distribution "
                         "distance between two convergence-schema row "
                         "files; writes its own file and nothing else")
    ap.add_argument("--compare-arm", default="A",
                    help="arm to compare for --compare-runs (default A)")
    ap.add_argument("--compare-out",
                    default="convergence/analysis_runs/compare_runs.json",
                    help="output path for --compare-runs")
    args = ap.parse_args()

    if args.compare_runs:
        pa, pb = args.compare_runs
        os.makedirs(os.path.dirname(args.compare_out) or ".", exist_ok=True)
        ra, _ = load_rows(pa)
        rb, _ = load_rows(pb)
        res = compare_runs(ra, rb, args.compare_arm, pa, pb)
        write_json(args.compare_out, res)
        for m, v in sorted(res["models"].items()):
            print(f"{m:34s} items {v['n_items_compared']:3d}  "
                  f"modal match {v['modal_matches']:3d}  "
                  f"tied/undefined {v['modal_undefined_either_side']:2d}  "
                  f"mean TVD {v['mean_tvd']}  max {v['max_tvd']}  "
                  f"full flips {v['full_flips']}")
        print("wrote", args.compare_out)
        return

    roster = load_roster(args.roster)
    rows, malformed = load_rows(args.rows)
    report = integrity(rows, roster, malformed)
    print_integrity(report)
    if args.integrity_only:
        return

    baseline_rows, base_malformed = load_rows(args.baseline)
    if base_malformed:
        print("  baseline malformed lines skipped: {}".format(base_malformed))
    try:
        result = analyze(rows, roster, baseline_rows, malformed=malformed)
    except (MultiEchoError, GateError) as exc:
        sys.stderr.write(str(exc) + "\n")
        sys.exit(1)
    write_outputs(result, args.out_dir)
    print()
    print(result["primary"]["decision_sentence"])
    print(result["primary"]["absolute_sentence"])
    print("Artifacts: {}".format(args.out_dir))


if __name__ == "__main__":
    main()
