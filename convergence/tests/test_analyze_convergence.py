"""
Fixture tests for convergence/analyze.py. No network: everything runs on
hand-built row fixtures with known modals, ties, and agreement values.

Pins, per claude_code_handoff_analysis.md (Tests):

  1. Modal rule: unique mode, tied flag, empty distribution; strict
     matching (tie is a non-match) and set-intersection matching.
  2. Pair agreement and lab-balancing against a hand-computed example
     (three-model lab, two-model lab, singleton lab).
  3. Bootstrap determinism: same seed, same interval, twice; a different
     seed moves the interval on this fixture.
  4. The 680-row gate: one missing row refuses the primary, stating the
     model and what is missing; integrity still runs on partial data.
  5. Multi-echo fail-loud: two distinct model_id_exact values inside one
     cell raise, naming both ids, rather than pooling or choosing.
  6. Both void triggers: unparsed rate over 0.20 voids the model's
     reading on the affected arm (either arm); rate over 0.10 excludes
     the model in sensitivity 1 only.
  7. All three sensitivities: unparsed exclusion, three single-Anthropic
     recomputes with the range, set-intersection tie matching.
  8. Test-retest on a baseline-schema fixture (9-field rows): per-item
     modal match rate, TVD, undefined-TVD handling, the corroborative
     label, and the stated Opus exclusion.
  9. Both pre-committed sentences selected by constructed inputs, at the
     unit level and end-to-end.
 10. Deterministic artifacts: two runs on identical inputs and seed
     produce byte-identical output files; a repeated run overwrites.

Run: python convergence/tests/test_analyze_convergence.py   (plain
asserts, exit 1 on failure; also collectable by pytest).
"""
import os
import sys
import json
import shutil
import tempfile
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)

from convergence import analyze as az  # noqa: E402
from items.items import ITEMS  # noqa: E402

IDS = [it["id"] for it in ITEMS]

ROSTER_A = [
    {"model": "anth-small", "provider": "anthropic", "arms": ["A"]},
    {"model": "anth-mid", "provider": "anthropic", "arms": ["A"]},
    {"model": "anth-big", "provider": "anthropic", "arms": ["A"]},
    {"model": "oai-small", "provider": "openai", "arms": ["A"]},
    {"model": "oai-big", "provider": "openai", "arms": ["A"]},
    {"model": "zai-solo", "provider": "zai", "arms": ["A"]},
]
PROVIDER = {m["model"]: m["provider"] for m in ROSTER_A}

# Hand-designed per-item answers (index i over the 68 bank items):
#   anth-small: A for i<34, else B      anth-mid: A for i<34, else C
#   anth-big:   identical to anth-small
#   oai-small:  D everywhere            oai-big: D for i<51, else A
#   zai-solo:   A for i<17, else D
# Hand-computed pair agreements (over 68 items):
#   within anthropic: small-mid 34/68, small-big 68/68, mid-big 34/68
#   within openai: 51/68
#   cross: zai-anth* 17/68 each; zai-oai-small 51/68; zai-oai-big 34/68;
#          all anth-oai pairs 0/68
ANSWER = {
    "anth-small": lambda i: "A" if i < 34 else "B",
    "anth-mid": lambda i: "A" if i < 34 else "C",
    "anth-big": lambda i: "A" if i < 34 else "B",
    "oai-small": lambda i: "D",
    "oai-big": lambda i: "D" if i < 51 else "A",
    "zai-solo": lambda i: "A" if i < 17 else "D",
}
WITHIN_BAL = ((34 / 68 + 68 / 68 + 34 / 68) / 3 + 51 / 68) / 2
PAIR_WEIGHTED = (34 / 68 + 68 / 68 + 34 / 68 + 51 / 68) / 4
CROSS_MEAN = (3 * (17 / 68) + 51 / 68 + 34 / 68 + 6 * 0.0) / 11
DIFF = WITHIN_BAL - CROSS_MEAN


def mk_row(model, arm, item_id, sample_index, parsed, echo=None):
    return {"run_id": "fixture", "phase": "baseline", "model": model,
            "item_id": item_id, "item_cell": "derivable",
            "sample_index": sample_index, "parsed": parsed,
            "raw_text": "ANSWER: {}".format(parsed) if parsed else "no",
            "ts": "2026-07-26T00:00:00+00:00", "provider": PROVIDER[model],
            "model_id_exact": echo or model, "host": None, "arm": arm,
            "reasoning_requested": "off" if arm == "A" else "on",
            "reasoning_detected": False, "temperature_sent": None}


def grid_rows(models=None, arm="A", k=10):
    rows = []
    for model in (models or [m["model"] for m in ROSTER_A]):
        for i, iid in enumerate(IDS):
            for s in range(k):
                rows.append(mk_row(model, arm, iid, s, ANSWER[model](i)))
    return rows


def unparse(rows, model, arm, n):
    """Set parsed to None on the first n rows of one cell, spread over
    items (at most 3 per item), so modals stay unanimous."""
    changed = 0
    for pass_index in (0, 1, 2):
        for r in rows:
            if changed >= n:
                return rows
            if (r["model"] == model and r["arm"] == arm
                    and r["sample_index"] == pass_index):
                r["parsed"] = None
                changed += 1
    raise AssertionError("could not unparse {} rows".format(n))


def baseline_row(model, item_id, sample_index, parsed):
    """Faithful baseline schema: the 9 original fields only."""
    return {"run_id": "2026-07-04T00:00:00+00:00", "phase": "baseline",
            "model": model, "item_id": item_id, "item_cell": "derivable",
            "sample_index": sample_index, "parsed": parsed,
            "raw_text": "ANSWER: {}".format(parsed),
            "ts": "2026-07-04T00:00:01+00:00"}


def close(a, b, tol=1e-12):
    return a is not None and b is not None and abs(a - b) < tol


def run():
    fails = []

    def check(name, cond, got=None):
        if cond:
            print("  PASS: %s" % name)
        else:
            print("  FAIL: %s | got %r" % (name, got))
            fails.append(name)

    print("=== modal rule: unique mode, ties, empty; both matchers ===")
    v = az.modal_info(Counter({"A": 6, "B": 4}))
    check("unique mode", v["modal"] == "A" and not v["tied"]
          and close(v["p_modal"], 0.6) and v["n_parsed"] == 10, v)
    t = az.modal_info(Counter({"A": 5, "B": 5}))
    check("tied mode has no modal option",
          t["modal"] is None and t["tied"] and t["modal_set"] == ("A", "B"), t)
    e = az.modal_info(Counter())
    check("empty distribution has no modal option",
          e["modal"] is None and not e["tied"] and e["n_parsed"] == 0, e)
    check("strict: equal unique modes match",
          az.match_strict(v, az.modal_info(Counter({"A": 9, "C": 1}))))
    check("strict: tie on either side is a non-match",
          not az.match_strict(v, t) and not az.match_strict(t, v))
    check("strict: empty side is a non-match", not az.match_strict(v, e))
    check("intersection: tie containing the other side's mode matches",
          az.match_intersection(v, t))
    check("intersection: disjoint modal sets do not match",
          not az.match_intersection(
              t, az.modal_info(Counter({"C": 3, "D": 3}))))
    check("intersection: empty side never matches",
          not az.match_intersection(t, e))

    print("=== lab-balancing against the hand-computed example ===")
    rows = grid_rows()
    baseline = [baseline_row("claude-haiku-4-5-20251001", IDS[0], 0, "A")]
    res = az.analyze(rows, ROSTER_A, baseline, B=100)
    p = res["primary"]
    check("within-lab lab-balanced mean",
          close(p["within_lab_balanced"], WITHIN_BAL), p["within_lab_balanced"])
    check("within-lab pair-weighted mean",
          close(p["within_pair_weighted"], PAIR_WEIGHTED),
          p["within_pair_weighted"])
    check("per-lab means", close(p["lab_means"]["anthropic"],
                                 (34 / 68 + 1.0 + 34 / 68) / 3)
          and close(p["lab_means"]["openai"], 51 / 68), p["lab_means"])
    check("cross-lab mean", close(p["cross_mean"], CROSS_MEAN), p["cross_mean"])
    check("primary difference", close(p["diff"], DIFF), p["diff"])
    check("no voids on the clean grid",
          res["voided"] == {"A": [], "B": []}, res["voided"])
    check("integrity: 680 rows, zero unparsed, no dup slots, no ties",
          all(c["rows"] == 680 and c["unparsed"] == 0
              and c["duplicate_slots"] == [] and c["tie_items"] == 0
              for c in res["integrity"]["cells"]), res["integrity"]["cells"])

    print("=== pre-committed sentences ===")
    s, absolute = az.decision_sentence(
        {"within_lab_balanced": 0.9, "cross_mean": 0.7, "diff": 0.2},
        {"lo": 0.1, "hi": 0.3})
    check("interval excluding zero selects the exceeds sentence",
          s.startswith("Within-lab agreement exceeds cross-lab agreement"), s)
    s2, _ = az.decision_sentence(
        {"within_lab_balanced": 0.9, "cross_mean": 0.88, "diff": 0.02},
        {"lo": -0.01, "hi": 0.05})
    check("interval including zero selects the unresolved sentence",
          s2.startswith("No difference resolved at this N"), s2)
    check("absolute line names 0.25, 1.00 and is not accuracy",
          "0.25" in absolute and "1.00" in absolute
          and "not accuracy" in absolute, absolute)
    check("end-to-end: clear separation selects the exceeds sentence",
          p["decision_sentence"].startswith(
              "Within-lab agreement exceeds cross-lab agreement"),
          p["decision_sentence"])
    identical = []
    for model in [m["model"] for m in ROSTER_A]:
        for i, iid in enumerate(IDS):
            for s_idx in range(10):
                identical.append(mk_row(model, "A", iid, s_idx, "C"))
    res_flat = az.analyze(identical, ROSTER_A, baseline, B=100)
    check("end-to-end: zero difference selects the unresolved sentence",
          res_flat["primary"]["decision_sentence"].startswith(
              "No difference resolved at this N"),
          res_flat["primary"]["decision_sentence"])

    print("=== bootstrap determinism ===")
    dists, _ = az.build_distributions(rows, "A", list(ANSWER))
    pairs = az.build_pairs(list(ANSWER), PROVIDER, az.build_modals(dists),
                           az.match_strict)
    b1 = az.bootstrap_diff(pairs, B=200, seed=az.BOOT_SEED)
    b2 = az.bootstrap_diff(pairs, B=200, seed=az.BOOT_SEED)
    check("same seed, same interval, twice",
          b1["lo"] == b2["lo"] and b1["hi"] == b2["hi"], (b1, b2))
    b3 = az.bootstrap_diff(pairs, B=200, seed=1)
    check("different seed moves the interval on this fixture",
          (b3["lo"], b3["hi"]) != (b1["lo"], b1["hi"]), (b1, b3))

    print("=== the 680-row gate ===")
    short = [r for r in rows
             if not (r["model"] == "oai-big" and r["item_id"] == IDS[0]
                     and r["sample_index"] == 9)]
    try:
        az.analyze(short, ROSTER_A, baseline, B=100)
        check("gate refuses on 679 rows", False, "no exception")
    except az.GateError as exc:
        check("gate refuses on 679 rows, stating what is missing",
              "oai-big" in str(exc) and "679" in str(exc)
              and "680" in str(exc) and "1 missing" in str(exc), str(exc))
    check("integrity still runs on partial data",
          any(c["model"] == "oai-big" and c["rows"] == 679
              for c in az.integrity(short, ROSTER_A)["cells"]))
    dup = rows + [mk_row("zai-solo", "A", IDS[3], 2, "D")]
    try:
        az.analyze(dup, ROSTER_A, baseline, B=100)
        check("gate refuses on a duplicate slot", False, "no exception")
    except az.GateError as exc:
        check("gate refuses on a duplicate slot, naming the duplication",
              "zai-solo" in str(exc) and "1 duplicate" in str(exc), str(exc))
    check("integrity detects the duplicate slot",
          any(c["model"] == "zai-solo"
              and c["duplicate_slots"] == [[IDS[3], 2]]
              for c in az.integrity(dup, ROSTER_A)["cells"]))

    print("=== multi-echo fail-loud ===")
    split = [dict(r) for r in rows]
    for r in split:
        if (r["model"] == "anth-mid" and r["item_id"] == IDS[5]
                and r["sample_index"] == 7):
            r["model_id_exact"] = "anth-mid-realiased"
    try:
        az.analyze(split, ROSTER_A, baseline, B=100)
        check("multi-echo raises", False, "no exception")
    except az.MultiEchoError as exc:
        check("multi-echo raises naming both ids",
              "anth-mid" in str(exc) and "anth-mid-realiased" in str(exc),
              str(exc))
    check("integrity reports both echo ids with counts",
          any(c["model"] == "anth-mid"
              and c["echo_ids"] == {"anth-mid": 679, "anth-mid-realiased": 1}
              for c in az.integrity(split, ROSTER_A)["cells"]))

    print("=== void triggers and sensitivity 1 ===")
    sens = unparse(grid_rows(), "oai-big", "A", 70)   # 70/680 > 0.10, < 0.20
    res_s = az.analyze(sens, ROSTER_A, baseline, B=100)
    check("0.10 < rate <= 0.20 does not void",
          res_s["voided"]["A"] == [], res_s["voided"])
    check("sensitivity 1 excludes the over-0.10 model",
          res_s["sensitivity_1_unparsed"]["excluded"] == ["oai-big"]
          and not res_s["sensitivity_1_unparsed"]["identical_to_primary"],
          res_s["sensitivity_1_unparsed"])
    check("primary still includes the over-0.10 model",
          "oai-big" in res_s["primary"]["models"], res_s["primary"]["models"])
    check("unanimous modals survive the unparse spread: primary unchanged",
          close(res_s["primary"]["diff"], DIFF), res_s["primary"]["diff"])
    sub = [m for m in ANSWER if m != "oai-big"]
    ref = az.primary_computation(grid_rows(), sub, PROVIDER, B=100)
    check("sensitivity 1 equals the primary on the reduced roster",
          close(res_s["sensitivity_1_unparsed"]["diff"], ref["point"]["diff"]),
          (res_s["sensitivity_1_unparsed"]["diff"], ref["point"]["diff"]))

    void_a = unparse(grid_rows(), "zai-solo", "A", 137)  # 137/680 > 0.20
    res_v = az.analyze(void_a, ROSTER_A, baseline, B=100)
    check("rate over 0.20 voids the Arm A reading",
          res_v["voided"]["A"] == ["zai-solo"], res_v["voided"])
    check("voided model drops from the primary",
          "zai-solo" not in res_v["primary"]["models"]
          and res_v["primary"]["voided_excluded"] == ["zai-solo"],
          res_v["primary"]["models"])
    ref_v = az.primary_computation(
        grid_rows(), [m for m in ANSWER if m != "zai-solo"], PROVIDER, B=100)
    check("primary after the void equals the no-void reduced computation",
          close(res_v["primary"]["diff"], ref_v["point"]["diff"]),
          (res_v["primary"]["diff"], ref_v["point"]["diff"]))

    roster_ab = [dict(m, arms=["A", "B"]) for m in ROSTER_A]
    both = grid_rows() + grid_rows(arm="B")
    void_b = unparse(both, "anth-mid", "B", 137)
    res_b = az.analyze(void_b, roster_ab, baseline, B=100)
    check("Arm B void trigger fires independently of Arm A",
          res_b["voided"] == {"A": [], "B": ["anth-mid"]}, res_b["voided"])
    check("Arm B void drops the model from Arm B secondary only",
          "anth-mid" not in res_b["secondary"]["p_modal"]["B"]
          and "anth-mid" in res_b["secondary"]["p_modal"]["A"],
          sorted(res_b["secondary"]["p_modal"]["B"]))
    check("Arm B aggregates carry the confounded-by-construction label",
          "confounded by construction"
          in res_b["secondary"]["arm_comparison_label"])

    print("=== sensitivity 2: single Anthropic representative ===")
    s2 = res["sensitivity_2_single_anthropic"]
    check("three recomputes, one per Anthropic model",
          sorted(s2["runs"]) == ["anth-big", "anth-mid", "anth-small"],
          sorted(s2["runs"]))
    for solo in sorted(s2["runs"]):
        r = s2["runs"][solo]
        others = {"anth-small", "anth-mid", "anth-big"} - {solo}
        check("sole representative {}: other Anthropic models removed"
              .format(solo), not others & set(r["models"]), r["models"])
    # Hand-computed: within reduces to the openai pair (51/68); cross is
    # solo-vs-openai (0, 0), solo-vs-zai (17/68), openai-vs-zai
    # (51/68, 34/68), five pairs.
    expect_solo = 51 / 68 - (17 / 68 + 51 / 68 + 34 / 68) / 5
    for solo in sorted(s2["runs"]):
        check("sole representative {}: hand-computed difference".format(solo),
              close(s2["runs"][solo]["diff"], expect_solo),
              s2["runs"][solo]["diff"])
    check("difference range over the three recomputes",
          close(s2["diff_range"][0], expect_solo)
          and close(s2["diff_range"][1], expect_solo), s2["diff_range"])

    print("=== sensitivity 3: set-intersection tie matching ===")
    tie_rows = []
    for r in grid_rows():
        if (r["model"] == "oai-small" and r["item_id"] == IDS[40]
                and r["sample_index"] < 5):
            r = dict(r, parsed="A")   # oai-small item 40: 5xD, 5xA tie
        tie_rows.append(r)
    res_t = az.analyze(tie_rows, ROSTER_A, baseline, B=100)
    strict = az.primary_computation(tie_rows, list(ANSWER), PROVIDER, B=100)
    inter = az.primary_computation(tie_rows, list(ANSWER), PROVIDER,
                                   matcher=az.match_intersection, B=100)
    key = ("oai-small", "oai-big")
    check("tie is a non-match under the primary rule (51 -> 50 of 68)",
          close(strict["point"]["pair_agreement"][key], 50 / 68),
          strict["point"]["pair_agreement"][key])
    check("intersection restores the tied-set match (51 of 68)",
          close(inter["point"]["pair_agreement"][key], 51 / 68),
          inter["point"]["pair_agreement"][key])
    check("analyze primary uses strict; sensitivity 3 uses intersection",
          close(res_t["primary"]["diff"], strict["point"]["diff"])
          and close(res_t["sensitivity_3_tie_intersection"]["diff"],
                    inter["point"]["diff"]),
          (res_t["primary"]["diff"],
           res_t["sensitivity_3_tie_intersection"]["diff"]))
    check("integrity counts the tie item",
          any(c["model"] == "oai-small" and c["arm"] == "A"
              and c["tie_items"] == 1
              for c in res_t["integrity"]["cells"]))

    print("=== test-retest on a baseline-schema fixture ===")
    haiku, sonnet = az.TEST_RETEST_MODELS
    fresh, base = [], []
    for i, iid in enumerate(IDS):
        for s_idx in range(10):
            fresh.append(dict(mk_row("anth-small", "A", iid, s_idx,
                                     "A" if i < 60 else "B"),
                              model=haiku, provider="anthropic"))
            fresh.append(dict(mk_row("anth-small", "A", iid, s_idx,
                                     "B" if (i == 0 and s_idx < 5) else
                                     ("A" if i == 0 else "D")),
                              model=sonnet, provider="anthropic"))
        for s_idx in range(6):
            base.append(baseline_row(
                haiku, iid, s_idx,
                ("A" if s_idx < 4 else "B") if i < 60 else "C"))
            if i != 1:
                base.append(baseline_row(
                    sonnet, iid, s_idx, "A" if i == 0 else "D"))
    tr = az.test_retest(fresh, base)
    h = tr["models"][haiku]
    check("haiku modal match rate 60/68",
          close(h["modal_match_rate"], 60 / 68) and h["n_matches"] == 60, h)
    check("haiku TVD: 1/3 on matched items, 1.0 on moved items, mean 7/17",
          close(h["tvd_mean"], 7 / 17) and close(h["tvd_median"], 1 / 3)
          and close(h["tvd_max"], 1.0),
          (h["tvd_mean"], h["tvd_median"], h["tvd_max"]))
    s = tr["models"][sonnet]
    check("sonnet fresh tie counts as a non-match",
          s["items"][ [it["item_id"] for it in s["items"]].index(IDS[0]) ]
          ["tied_fresh"] and s["n_matches"] == 66, s["n_matches"])
    check("missing baseline item: TVD undefined, counted, non-match",
          s["items_tvd_undefined"] == 1
          and close(s["tvd_mean"], 0.5 / 67), (s["items_tvd_undefined"],
                                               s["tvd_mean"]))
    check("labelled corroborative", "corroborative" in tr["label"], tr["label"])
    check("Opus exclusion stated, naming the different baseline model",
          "claude-opus-4-7" in tr["opus_exclusion"]
          and "claude-opus-4-8" in tr["opus_exclusion"], tr["opus_exclusion"])

    print("=== deterministic artifacts: byte-identical repeat run ===")
    tmp = tempfile.mkdtemp(prefix="convergence_analyze_test_")
    try:
        d1, d2 = os.path.join(tmp, "run1"), os.path.join(tmp, "run2")
        az.write_outputs(az.analyze(grid_rows(), ROSTER_A, base, B=100), d1)
        az.write_outputs(az.analyze(grid_rows(), ROSTER_A, base, B=100), d2)
        az.write_outputs(az.analyze(grid_rows(), ROSTER_A, base, B=100), d2)
        names = sorted(os.listdir(d1))
        check("all six artifacts written",
              names == ["convergence_report.md", "convergence_results.json",
                        "per_item.csv", "per_pair.csv", "test_retest.json",
                        "test_retest.md"], names)
        same = all(
            open(os.path.join(d1, n), "rb").read()
            == open(os.path.join(d2, n), "rb").read() for n in names)
        check("byte-identical across runs, overwrite not append", same)
        with open(os.path.join(d1, "convergence_results.json"),
                  encoding="utf-8") as f:
            blob = json.load(f)
        check("results json carries no test-retest content (own file)",
              "test_retest" not in blob, sorted(blob))
        with open(os.path.join(d1, "per_pair.csv"), encoding="utf-8") as f:
            n_pairs = sum(1 for _ in f) - 1
        check("per-pair csv holds the 15 Arm A pairs", n_pairs == 15, n_pairs)
        with open(os.path.join(d1, "per_item.csv"), encoding="utf-8") as f:
            n_items = sum(1 for _ in f) - 1
        check("per-item csv holds 6 models x 68 items",
              n_items == 6 * 68, n_items)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    print("FAILURES: %d %s" % (len(fails), fails if fails else "- ALL PASS"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(run())


def test_analyze_convergence():  # pytest entry point
    assert run() == 0
