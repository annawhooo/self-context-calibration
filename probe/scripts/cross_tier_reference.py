import json
import collections
import itertools

ROWS = r"C:\Users\Anna\PycharmProjects\self-context-calibration\convergence\results\convergence_rows.jsonl"
OPTIONS = ("A", "B", "C", "D")
MODELS = ["claude-haiku-4-5-20251001", "claude-sonnet-4-6", "claude-opus-4-8"]

rows = [json.loads(l) for l in open(ROWS, encoding="utf-8")]
armA = [r for r in rows if r.get("arm") == "A"]

def dists(model):
    d = {}
    for r in armA:
        if r.get("model") != model:
            continue
        c = d.setdefault(r.get("item_id"), collections.Counter())
        p = r.get("parsed")
        if p in OPTIONS:
            c[p] += 1
    return d

D = {m: dists(m) for m in MODELS}
ids = sorted(set(itertools.chain.from_iterable(D[m] for m in MODELS)))

print("cross-model TVD reference, Arm A, frozen data")
for a, b in itertools.combinations(MODELS, 2):
    tvds = []
    for iid in ids:
        ca, cb = D[a].get(iid), D[b].get(iid)
        if not ca or not cb:
            continue
        na, nb = sum(ca.values()), sum(cb.values())
        tvd = 0.5 * sum(abs(ca.get(o, 0) / na - cb.get(o, 0) / nb)
                        for o in OPTIONS)
        tvds.append(tvd)
    n = len(tvds)
    print(f"{a.split('-')[1]:8s} vs {b.split('-')[1]:8s}  items {n:3d}  "
          f"mean TVD {sum(tvds)/n:.4f}  max {max(tvds):.4f}  "
          f"full flips {sum(1 for t in tvds if t == 1.0)}")
