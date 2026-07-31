import json
import random
import collections

BASE = r"C:\Users\Anna\PycharmProjects\self-context-calibration\results\confab_baseline_faithful.jsonl"
FRESH = r"C:\Users\Anna\PycharmProjects\self-context-calibration\convergence\results\convergence_rows.jsonl"
OPTIONS = ("A", "B", "C", "D")
MODELS = ["claude-haiku-4-5-20251001", "claude-sonnet-4-6"]
RESAMPLES = 200
SEED = 20260731

base_rows = [json.loads(l) for l in open(BASE, encoding="utf-8")]
fresh_rows = [json.loads(l) for l in open(FRESH, encoding="utf-8")]

def parsed_lists(rows, model, want_phase=None):
    """item_id -> list of parsed options (order as collected)."""
    out = collections.defaultdict(list)
    for r in rows:
        if r.get("model") != model:
            continue
        if want_phase is not None and r.get("phase") != want_phase:
            continue
        if want_phase is None and r.get("arm") != "A":
            continue
        p = r.get("parsed")
        if p in OPTIONS:
            out[r.get("item_id")].append(p)
    return out

def tvd(ca, cb):
    na, nb = sum(ca.values()), sum(cb.values())
    return 0.5 * sum(abs(ca.get(o, 0) / na - cb.get(o, 0) / nb)
                     for o in OPTIONS)

rng = random.Random(SEED)

for model in MODELS:
    base = parsed_lists(base_rows, model, want_phase="baseline")
    fresh = parsed_lists(fresh_rows, model)
    ids = sorted(set(base) & set(fresh))
    base_k = sorted({len(base[i]) for i in ids})
    print(f"\n{model}")
    print(f"  items compared: {len(ids)}; baseline per-item K range: "
          f"{min(base_k)}..{max(base_k)}")

    # full-K reference (should reproduce the frozen test-retest numbers)
    full = [tvd(collections.Counter(base[i]), collections.Counter(fresh[i]))
            for i in ids]
    print(f"  full-K mean TVD: {sum(full)/len(full):.4f}")

    # subsampled to K=10 (or all rows if fewer), 200 resamples
    means = []
    for _ in range(RESAMPLES):
        ts = []
        for i in ids:
            pool = base[i]
            take = pool if len(pool) <= 10 else rng.sample(pool, 10)
            ts.append(tvd(collections.Counter(take),
                          collections.Counter(fresh[i])))
        means.append(sum(ts) / len(ts))
    means.sort()
    lo, hi = means[int(0.05 * RESAMPLES)], means[int(0.95 * RESAMPLES) - 1]
    print(f"  K=10-subsampled mean TVD over {RESAMPLES} resamples: "
          f"{sum(means)/len(means):.4f}  [5th..95th pct: {lo:.4f}..{hi:.4f}]")
