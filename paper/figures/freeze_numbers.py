"""Every record-dependent number in the INTERCEPT draft, regenerated.

The draft's numbers policy (paper/INTERCEPT_DRAFT.md, header) says no
number goes to the PDF without a script behind it and a verifier
match. This script is the manifest side of that bargain: it computes
every [FREEZE]-tagged quantity that is regenerable from the committed
record, renders each one as the prose should print it, and writes a
keyed manifest that check_draft_numbers.py diffs against the draft.
At the freeze the number swap is: rerun this, rerun the checker, fix
what it flags. Between now and then any run is a dress rehearsal on
the record to date.

Inputs are committed only: the verdict log, the derived daily counts,
the qualified baseline files, and the outputs of the three committed
analyses of record it shells out to (recurrence_structure_null.py,
between_day_variance.py, quiet_slot_decomposition.py), the same way
tables.py consumes T1. Re-baselined items are scored against the
reference in force on each date throughout, per the convention in
probe/REBASELINE_DECISION_2026-08-23.md.

Provenance classes carried per entry:
  record      regenerated from the committed record by this run
  raw-rows    needs the gitignored raw row files; the manifest holds
              the last published value and names the source note
  no-script   published from a session analysis that never became a
              committed script; blocked from the PDF until one exists
  constant    instrument constant, verified against the record

Consistency gates (the run dies loudly if any fails): the direct
verdict-log tallies match the null script's observed side, the
variance script's recomputed breach slot-days match the verdict log
exactly in both directions, and the band-simulation replica used for
the K=30 estimate reproduces every committed K=10 band byte-exactly
from the stored seeds before k is changed.

Writes out/freeze_numbers.json and out/freeze_numbers.md.

  python paper/figures/freeze_numbers.py
"""
import collections
import datetime
import json
import math
import os
import random
import re
import subprocess
import sys

import figdata as fd

NULL_SCRIPT = os.path.join(fd.REPO, "probe", "scripts",
                           "recurrence_structure_null.py")
VARIANCE_SCRIPT = os.path.join(fd.REPO, "probe", "scripts",
                               "between_day_variance.py")
DECOMP_SCRIPT = os.path.join(fd.HERE, "quiet_slot_decomposition.py")

SONNET = "claude-sonnet-4-6"
HAIKU = "claude-haiku-4-5-20251001"
GPT = "gpt-5.6-terra"
GEMINI = "gemini-3.6-flash"
DEEPSEEK = "deepseek-v4-flash"
FRAUD = "eq_alert_fraud_scoring_v2"
VULN = "eq_alert_vuln_gating_v2"
SPEND = "eq_alert_spend_anomaly_v2"
OFFBOARD = "eq_access_offboarding"
CONTRACTOR = "eq_access_contractor"

WORDS = ("zero", "one", "two", "three", "four", "five", "six",
         "seven", "eight", "nine", "ten", "eleven", "twelve")


def word(n):
    return WORDS[n] if 0 <= n < len(WORDS) else str(n)


def sci(x):
    """7.3e-13 style: one decimal mantissa, bare exponent."""
    m, e = ("%.1e" % x).split("e")
    return "%se%d" % (m, int(e))


def month_days(dates):
    """ISO dates -> 'Aug 3, 4, 6, 10' with month names carried only
    on a month change."""
    out, last_month = [], None
    for d in dates:
        dt = datetime.date.fromisoformat(d)
        name = dt.strftime("%b")
        out.append("%s %d" % (name, dt.day) if name != last_month
                   else str(dt.day))
        last_month = name
    return ", ".join(out)


def run_script(path, *args):
    proc = subprocess.run((sys.executable, path) + args, cwd=fd.REPO,
                          capture_output=True, text=True, check=True)
    return proc.stdout


def grab(text, label):
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(label):
            return " ".join(stripped[len(label):].split())
    raise KeyError(label)


def vec(counts):
    return "/".join(str(counts.get(o, 0)) for o in fd.OPTIONS)


def log_multinomial(counts, probs):
    """Log P of an exact count vector under a multinomial with probs
    over fd.OPTIONS; None if it needs a zero-mass option."""
    k = sum(counts.values())
    lp = math.lgamma(k + 1)
    for o, p in zip(fd.OPTIONS, probs):
        c = counts.get(o, 0)
        lp -= math.lgamma(c + 1)
        if c:
            if p <= 0:
                return None
            lp += c * math.log(p)
    return lp


def smoothed_probs(base_counts, n):
    return [(base_counts.get(o, 0) + 1.0) / (n + 4.0)
            for o in fd.OPTIONS]


def compositions(k):
    for a in range(k + 1):
        for b in range(k + 1 - a):
            for c in range(k + 1 - a - b):
                yield {"A": a, "B": b, "C": c, "D": k - a - b - c}


COMPS10 = tuple(compositions(10))


def false_breach_mass(ref, truth, strict=True, k=10):
    """P(K-draw TVD vs the empirical reference {strictly above /
    at or above} the band p99), exact enumeration; the
    expected_false_breaches.py method."""
    base = ref["baseline_counts"]
    n = ref["n"]
    p99 = ref["band"]["p99"]
    if truth == "smoothed":
        probs = smoothed_probs(base, n)
    else:
        probs = [base.get(o, 0) / n for o in fd.OPTIONS]
    acc = 0.0
    for comp in COMPS10:
        t = fd.tvd(comp, base)
        hit = t > p99 if strict else t >= p99
        if not hit:
            continue
        lp = log_multinomial(comp, probs)
        if lp is not None:
            acc += math.exp(lp)
    return acc


def band_replica(base_counts, n, seed, k, sims=10000, smooth=1.0):
    """monitor.py smoothed_bands, replicated exactly: Laplace-smooth
    the counts, simulate sims K-draws with random.Random(seed), TVD
    each against the observed counts, take the (p95, p99) order
    statistics with that function's index convention."""
    probs = [(base_counts.get(o, 0) + smooth)
             / (n + smooth * len(fd.OPTIONS)) for o in fd.OPTIONS]
    rng = random.Random(seed)
    tvds = []
    for _ in range(sims):
        draw = collections.Counter(
            rng.choices(fd.OPTIONS, weights=probs, k=k))
        tvds.append(0.5 * sum(
            abs(base_counts.get(o, 0) / n - draw.get(o, 0) / k)
            for o in fd.OPTIONS))
    tvds.sort()
    return tvds[int(0.95 * sims) - 1], tvds[int(0.99 * sims) - 1]


def qualified_ref(rec):
    """The as-qualified (2026-08-02) reference of an item record."""
    return fd.baseline_for(rec, "2026-08-02")


def gate(ok, what):
    if not ok:
        raise SystemExit("CONSISTENCY GATE FAILED: %s" % what)
    print("gate ok: %s" % what)


def entry(entries, key, render, value, source, provenance="record",
          note=None):
    entries[key] = {"render": render, "value": value,
                    "source": source, "provenance": provenance}
    if note:
        entries[key]["note"] = note


def main():
    verdicts = fd.load_verdicts()
    daily = fd.load_daily()
    baselines = fd.load_baselines()
    breaches = fd.breach_index(verdicts)

    dates = sorted({v["date"] for v in verdicts})
    start, end = dates[0], dates[-1]
    n_days = len(dates)
    E = {}

    # ---- committed analyses of record ----------------------------
    null_out = run_script(NULL_SCRIPT)
    var_out = run_script(VARIANCE_SCRIPT)
    dec_out = run_script(DECOMP_SCRIPT)

    m = re.search(r"window (\S+)\.\.(\S+), (\d+) probe days", null_out)
    gate(m and m.group(1) == start and m.group(2) == end
         and int(m.group(3)) == n_days,
         "null-script window matches the verdict log")

    mv = re.search(r"breach slot-days: mine=(\d+) verdicts=(\d+) "
                   r"only_mine=\[\] only_verdicts=\[\]", var_out)
    gate(mv is not None and mv.group(1) == mv.group(2),
         "variance-script breaches match the verdict log exactly")

    # ---- record shape --------------------------------------------
    total_calls = sum(v["calls"] or 0 for v in verdicts)
    error_days = [(v["date"], v["model"]) for v in verdicts
                  if v["verdict"] == "ERROR"]
    entry(E, "days", str(n_days), n_days,
          "distinct dates in probe/monitor/verdicts.jsonl")
    entry(E, "window", "%s to %s" % (start, end), [start, end],
          "verdict log date span")
    entry(E, "total-rows", format(total_calls, ","), total_calls,
          "sum of the calls field over all verdict lines (probe "
          "plus rerun rows; ERROR days contribute none)",
          note="%d model-days are ERROR: %s"
               % (len(error_days),
                  ", ".join("%s %s" % (d, fd.SHORT[m])
                            for d, m in error_days)))

    # ---- observed breach structure (verdict log, direct) ---------
    entries_all = [(v["date"], v["model"], b["item_id"],
                    b["item_verdict"])
                   for v in verdicts for b in v.get("breached", [])]
    eq_entries = [e for e in entries_all if fd.is_equipoise(e[2])]
    n_entries = int(grab(null_out, "breach entries").split()[0])
    gate(n_entries == len(entries_all),
         "direct breach-entry count matches the null script")
    gate(len(eq_entries) == int(
        re.search(r"\((\d+) on eq_ items\)",
                  grab(null_out, "breach entries")).group(1)),
         "direct eq-entry count matches the null script")
    entry(E, "breach-entries-eq-of-total",
          "%d of %d" % (len(eq_entries), len(entries_all)),
          [len(eq_entries), len(entries_all)],
          "breach entries in the verdict log, eq_ share")

    unstable = [e for e in entries_all if e[3] == "UNSTABLE"]
    entry(E, "unstable-entries", word(len(unstable)), len(unstable),
          "UNSTABLE item verdicts in the log",
          note="; ".join("%s %s %s" % (d, fd.SHORT[m], i)
                         for d, m, i, _ in unstable))

    gem = [(d, i, v) for d, m, i, v in entries_all if m == GEMINI]
    gem_verdicts = sorted({v for _, _, v in gem})
    gem_render = (("%s transient breaches" % word(len(gem)))
                  if gem_verdicts == ["TRANSIENT"] else
                  "%d breaches (%s)" % (len(gem), ", ".join(
                      "%s %s" % (v.lower(), word(c)) for v, c in
                      collections.Counter(
                          v for _, _, v in gem).items())))
    entry(E, "gemini-breaches", gem_render, gem,
          "gemini breach entries and their item verdicts",
          note="entries: " + "; ".join(
              "%s %s %s" % (d, i, v) for d, i, v in gem))

    # ---- decisive class ------------------------------------------
    dec_slot_days = 0
    dec_exceed = {0.20: 0, 0.25: 0}
    dec_max = 0.0
    for (date, model, item), counts in daily.items():
        if fd.is_equipoise(item) or item not in baselines.get(
                model, {}):
            continue
        dec_slot_days += 1
        ref = fd.baseline_for(baselines[model][item], date)
        t = fd.tvd(counts, ref["baseline_counts"])
        dec_max = max(dec_max, t)
        for w in dec_exceed:
            if t > w:
                dec_exceed[w] += 1
    dec_breaches = sum(1 for _, _, i, _ in entries_all
                       if not fd.is_equipoise(i))
    gate(dec_breaches == 0, "no decisive breach entry in the log")
    entry(E, "decisive-slot-days", format(dec_slot_days, ","),
          dec_slot_days,
          "decisive slot-days with probe data in the derived counts",
          note="includes partial rows collected on ERROR model-days "
               "before the failure (the bank probes decisive items "
               "first); an ERROR day contributes data but no "
               "verdict")
    entry(E, "decisive-breaches", word(dec_breaches), dec_breaches,
          "decisive breach entries (band exceedances) in the log")
    entry(E, "decisive-020-exceedances",
          "%s exceedances above 0.20 in %s slot-days"
          % (word(dec_exceed[0.20]), format(dec_slot_days, ",")),
          dec_exceed[0.20],
          "decisive slot-day TVDs strictly above 0.20, in-force "
          "references",
          note="above 0.25: %d; max decisive slot-day TVD %.2f. The "
               "draft's section 5 claim of zero is the 12-day "
               "figure; reword at the freeze if this is nonzero."
               % (dec_exceed[0.25], dec_max))

    # ---- null structure (analysis of record) ---------------------
    exp_entries, p_count = re.match(
        r"([\d.]+)\s+P\(>= \d+\) = ([\d.e+-]+)",
        grab(null_out, "E[breach entries]")).groups()
    entry(E, "entries-vs-null",
          "%d observed against %.1f expected under the smoothed "
          "null, p = %.3f"
          % (n_entries, float(exp_entries), float(p_count)),
          [n_entries, float(exp_entries), float(p_count)],
          "recurrence_structure_null.py, full window")

    obs3 = int(re.match(r"(\d+) / (\d+) / (\d+)",
                        grab(null_out, "slots >=2 / >=3 / >=5")
                        ).group(2))
    e3 = float(grab(null_out, "E[slots >=2 / >=3 / >=5]"
                    ).split(" / ")[1])
    p3 = float(grab(null_out, "P(#slots >=3 at least"
                    ).split(")")[-1].strip())
    entry(E, "slots-ge3",
          "%s slots carry three or more breaches each, against "
          "%.3g expected slots at that depth, P = %s"
          % (word(obs3).capitalize(), e3, sci(p3)), [obs3, e3, p3],
          "recurrence_structure_null.py, full window; the render "
          "opens a sentence and is capitalized")

    eq_share = float(grab(null_out, "eq_ share of breach mass"))
    entry(E, "eq-null-share", "%.3f" % eq_share, eq_share,
          "recurrence_structure_null.py: eq_ share of null breach "
          "mass, day-weighted")
    p_all = float(grab(null_out, "P(all %d entries on eq_)"
                       % n_entries))
    n_distinct = int(grab(null_out, "distinct breached slots"))
    p_all_d = float(grab(null_out, "P(all %d distinct on eq_)"
                         % n_distinct))
    entry(E, "p-all-entries-eq", sci(p_all), p_all,
          "recurrence_structure_null.py")
    entry(E, "p-all-distinct-eq", sci(p_all_d), p_all_d,
          "recurrence_structure_null.py, distinct slots")

    dir3 = grab(null_out, ">=3-threads unidirectional")
    uni3, tot3 = (int(x) for x in dir3.split(" of "))
    e_same3 = float(grab(null_out, "E[slots >=3 same dir]"
                         ).split()[0])
    entry(E, "oscillator-direction",
          "%d of %d" % (uni3, uni3), [uni3, tot3, e_same3],
          "recurrence_structure_null.py; oscillators = the "
          "unidirectional >=3-threads, the mixed-direction wanderer "
          "counted separately",
          note="threads >=3: %d, unidirectional %d; E[slots >=3 "
               "same dir] under the null %.3g (the draft's 0.008 "
               "was the through-2026-08-20 value)"
               % (tot3, uni3, e_same3))
    entry(E, "oscillator-null", "%.3f" % e_same3, e_same3,
          "recurrence_structure_null.py: E[slots >=3 breaches all "
          "one direction] under the no-drift null")

    # ---- wanderer (decomposition part 3) -------------------------
    block = re.search(
        r"deepseek contractor\s+baseline (\S+)\s+MIXED\n((?:\s+\S+"
        r"\s+\S+\s+toward \S+\n?)+)", dec_out)
    gate(block is not None,
         "contractor thread is the MIXED thread in part 3")
    hits = re.findall(r"(\S+)\s+([A-Z])\s+toward ([A-D])",
                      block.group(2))
    dirs = sorted({d for _, _, d in hits})
    entry(E, "wanderer",
          "toward %s different options across %s entries"
          % (word(len(dirs)), word(len(hits))),
          {"entries": len(hits), "directions": dirs},
          "quiet_slot_decomposition.py part 3, deepseek contractor",
          note="per-entry: " + "; ".join(
              "%s %s toward %s" % h for h in hits))

    # ---- quiet-slot excess and modal share -----------------------
    quiet_rows = re.findall(
        r"(\S+)\s+quiet\s+\d+\s+\d+\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+"
        r"([+-][\d.]+)", dec_out)
    gate(len(quiet_rows) == 5, "five quiet rows in part 1")
    excess_max = max(float(x) for _, x in quiet_rows)
    entry(E, "quiet-excess-max", "%+.3f" % excess_max, excess_max,
          "quiet_slot_decomposition.py part 1: max over models of "
          "quiet-slot excess (observed minus probe-plus-baseline "
          "expectation)",
          note="per model: " + ", ".join(
              "%s %s" % (m, x) for m, x in quiet_rows))

    commit = collections.defaultdict(list)
    for (date, model, item), counts in daily.items():
        n = sum(counts.values())
        if n and item in baselines.get(model, {}):
            commit[model].append(max(counts.values()) / n)
    shares = {m: sum(v) / len(v) for m, v in commit.items()}
    entry(E, "modal-share-range",
          "%.2f to %.2f" % (min(shares.values()),
                            max(shares.values())),
          {fd.SHORT[m]: round(s, 4) for m, s in shares.items()},
          "mean per-day modal share over all slot-days, per model "
          "(the F4 x axis)")

    # ---- sonnet pair: recurrence and round trips -----------------
    fraud_pure = sorted(d for (d, m, i), c in daily.items()
                        if m == SONNET and i == FRAUD
                        and c == {"A": 10})
    entry(E, "fraud-pure-a-visits",
          "%s times (%s)" % (word(len(fraud_pure)),
                             month_days(fraud_pure)),
          fraud_pure,
          "days whose probe vector is exactly 10/0/0/0 on the "
          "sonnet fraud-scoring slot")

    joint = {}
    for d in dates:
        cf = daily.get((d, SONNET, FRAUD))
        cv = daily.get((d, SONNET, VULN))
        if cf and cv:
            joint[d] = (fd.modal(cf) == "A" and fd.modal(cv) == "D")
    runs, cur = [], None
    seq = sorted(joint)
    for d in seq:
        if joint[d] and cur is None:
            cur = [d, d, False]
        elif joint[d] and cur:
            cur[1] = d
        elif not joint[d] and cur:
            cur[2] = True
            runs.append(tuple(cur))
            cur = None
    if cur:
        runs.append(tuple(cur))
    completed = [r for r in runs if r[2]]
    if completed:
        span_start = datetime.date.fromisoformat(completed[0][0])
        last_exit_idx = seq.index(completed[-1][1]) + 1
        span_end = datetime.date.fromisoformat(
            seq[min(last_exit_idx, len(seq) - 1)])
        span = (span_end - span_start).days + 1
    else:
        span = 0
    entry(E, "sonnet-joint-round-trips",
          "%s round trips in %s days"
          % (word(len(completed)), word(span)),
          {"joint_away_runs": runs, "completed": len(completed),
           "span_days": span},
          "joint-away day: fraud modal A and vuln modal D, the "
          "recurring pair state; a round trip is a joint-away run "
          "that exits within the record; span runs first entry to "
          "the day the last completed trip exited",
          note="the abstract's 'seven days' counted from the "
               "Jul 30 pre-baseline observation; the committed "
               "record starts 2026-08-02")
    entry(E, "sonnet-joint-reentries",
          "%s in %s days" % ("twice" if len(completed) == 2 else
                             "%s times" % word(len(completed)),
                             word(span)),
          {"reentries": len(completed), "span_days": span},
          "the sonnet-joint-round-trips facts phrased for the 3.1 "
          "sentence (re-entered it N times in M days)")

    # ---- exact vector recurrence, gpt and haiku ------------------
    off_breach_days = sorted(breaches.get((GPT, OFFBOARD), {}))
    off_vecs = collections.Counter(
        vec(daily[(d, GPT, OFFBOARD)]) for d in off_breach_days
        if (d, GPT, OFFBOARD) in daily)
    repeats = [(v, c) for v, c in off_vecs.most_common() if c >= 2]
    entry(E, "offboarding-vector-repeats",
          ", ".join("%s %s times" % (v, word(c)) if c != 2
                    else "%s twice" % v for v, c in repeats),
          dict(off_vecs),
          "exact probe vectors on gpt offboarding breach days, "
          "multiplicity >= 2")

    spend_away = sorted(
        d for (d, m, i), c in daily.items()
        if m == HAIKU and i == SPEND and c == {"B": 6, "D": 4})
    entry(E, "spend-away-vector",
          "0/6/0/4, %s times (%s)" % (word(len(spend_away)),
                                      month_days(spend_away)),
          spend_away,
          "days whose probe vector is exactly 0/6/0/4 on the haiku "
          "spend slot, either reference epoch")

    # ---- state probabilities under the frozen baselines ----------
    fraud_ref = qualified_ref(baselines[SONNET][FRAUD])
    p_pure_a = math.exp(log_multinomial(
        {"A": 10}, smoothed_probs(fraud_ref["baseline_counts"],
                                  fraud_ref["n"])))
    entry(E, "fraud-pure-a-prob", sci(p_pure_a), p_pure_a,
          "P(10/0/0/0) under the Laplace-smoothed frozen sonnet "
          "fraud baseline, exact")
    vuln_ref = qualified_ref(baselines[SONNET][VULN])
    p_10d = math.exp(log_multinomial(
        {"D": 10}, smoothed_probs(vuln_ref["baseline_counts"],
                                  vuln_ref["n"])))
    entry(E, "vuln-10d-prob", sci(p_10d), p_10d,
          "P(0/0/0/10) under the Laplace-smoothed frozen sonnet "
          "vuln baseline, exact")
    entry(E, "vuln-10d-prob-pair", sci(p_10d * p_10d),
          p_10d * p_10d, "the same state across an independent "
          "probe-rerun pair")

    # ---- haiku return watch --------------------------------------
    spend_rec = baselines[HAIKU][SPEND]
    old = spend_rec["superseded"][0]
    post = sorted(d for (d, m, i) in daily
                  if m == HAIKU and i == SPEND
                  and d > old["valid_through"])
    returns = []
    for d in post:
        c = daily[(d, HAIKU, SPEND)]
        if (fd.tvd(c, old["baseline_counts"]) <= old["band"]["p99"]
                and fd.modal(c) == fd.modal(old["baseline_counts"])):
            returns.append(d)
    entry(E, "return-watch",
          ("a return day on %s" % month_days(returns[:1]))
          if returns else
          "no return observed in %s post-transition probe days"
          % word(len(post)),
          {"post_days": len(post), "return_days": returns},
          "the pre-registered return criterion of "
          "REBASELINE_DECISION_2026-08-23.md against the committed "
          "counts (probe/scripts/return_watch.py is the standalone "
          "check)")

    # ---- section 4: instrument corrections -----------------------
    efb = {}
    for cfg, ref_of in (("qualified", qualified_ref),
                        ("active", lambda r: r)):
        for truth in ("smoothed", "empirical"):
            efb[(cfg, truth)] = sum(
                false_breach_mass(ref_of(rec), truth)
                for items in baselines.values()
                for rec in items.values())
    entry(E, "expected-false-breaches",
          "%.2f expected false breaches per day if the smoothed "
          "baseline is truth, %.2f if the empirical baseline is "
          "truth" % (efb[("qualified", "smoothed")],
                     efb[("qualified", "empirical")]),
          {"%s-%s" % k: round(v, 4) for k, v in efb.items()},
          "exact enumeration, expected_false_breaches.py method, "
          "as-qualified references",
          note="under the ACTIVE references (post re-baseline) the "
               "smoothed figure is %.2f; the draft cites the "
               "as-qualified 1.64 and should say so at the freeze"
               % efb[("active", "smoothed")])

    ge_mass = sum(false_breach_mass(rec, "smoothed", strict=False)
                  for items in baselines.values()
                  for rec in items.values())
    ratio = ge_mass / efb[("active", "smoothed")]
    entry(E, "ge-vs-gt-ratio", "%.1fx" % ratio, ratio,
          "smoothed null breach mass at >= divided by strict >, "
          "active references, exact enumeration")

    # ---- K=30 bands: replicate, validate, recompute --------------
    checked, band_bad = 0, []
    for items in baselines.values():
        for rec in items.values():
            for ref in [qualified_ref(rec)] + (
                    [rec] if rec.get("superseded") else []):
                p95, p99 = band_replica(
                    ref["baseline_counts"], ref["n"],
                    ref["band"]["seed"], k=10)
                if (p95 != ref["band"]["p95"]
                        or p99 != ref["band"]["p99"]):
                    band_bad.append(ref["band"]["seed"])
                checked += 1
    gate(not band_bad,
         "band replica reproduces all %d committed K=10 bands "
         "from stored seeds (bad: %s)" % (checked, band_bad[:3]))
    k30 = []
    for items in baselines.values():
        for rec in items.values():
            ref = qualified_ref(rec)
            k30.append(band_replica(ref["baseline_counts"],
                                    ref["n"], ref["band"]["seed"],
                                    k=30)[1])
    entry(E, "k30-bands-range",
          "%.3f to %.3f" % (min(k30), max(k30)),
          [min(k30), max(k30)],
          "p99 bands recomputed at K=30 from the stored per-item "
          "band seeds, as-qualified references, monitor.py band "
          "simulation replicated (validated against every committed "
          "K=10 band first)")

    # ---- between-day variance lane -------------------------------
    eq_pooled = re.search(
        r"quiet pooled TVD class=eq n=(\d+) p50=[\d.]+ "
        r"p90=[\d.]+ p95=[\d.]+ p99=([\d.]+)", var_out)
    eq_n, eq_p99 = int(eq_pooled.group(1)), float(eq_pooled.group(2))
    entry(E, "between-day-eq-p99", "%.2f" % eq_p99, eq_p99,
          "between_day_variance.py: pooled quiet eq slot-day TVD "
          "p99, full window",
          note="this percentile moves with window length (0.35 in "
               "the validated 12-day window); if it sits inside the "
               "proposed K=30 band range the draft's section 4(b) "
               "sentence needs rewording, and the alarms-per-day "
               "figure below is the sturdier support")

    curves = {}
    for cls in ("eq", "decisive"):
        cm = re.search(r"false-alarm curve class=%s frac=(\{.*\})"
                       % cls, var_out)
        curves[cls] = {float(k): v for k, v
                       in json.loads(cm.group(1)).items()}
    dec_pooled = re.search(r"quiet pooled TVD class=decisive n=(\d+)",
                           var_out)
    dec_n = int(dec_pooled.group(1))
    alarms = {}
    for w in (0.267, 0.317):
        alarms[w] = (curves["eq"][w] * eq_n
                     + curves["decisive"][w] * dec_n) / n_days
    entry(E, "k30-false-alarms",
          "%.1f to %.1f" % (alarms[0.317], alarms[0.267]),
          {str(w): round(a, 3) for w, a in alarms.items()},
          "quiet slot-day TVDs strictly above the proposed K=30 "
          "band, per probe day, from the between_day_variance.py "
          "false-alarm curve (0.317 gives the low end, 0.267 the "
          "high)")

    shrink = float(re.search(
        r"decomposition class=eq .*k30_vs_k10_shrink=([\d.]+)",
        var_out).group(1))
    entry(E, "eq-k30-shrink", "%.2f" % shrink, shrink,
          "between_day_variance.py decomposition: projected K=30 "
          "eq mean TVD over the K=10 mean; sqrt-K predicts 0.577",
          note="the sqrt-K-scaling-is-wrong claim in section 5")

    # ---- baseline shapes -----------------------------------------
    eq_slots = [(m, i) for m, items in baselines.items()
                for i in items if fd.is_equipoise(i)]
    unanimous = 0
    for m, i in eq_slots:
        ref = qualified_ref(baselines[m][i])
        if max(ref["baseline_counts"].values()) == ref["n"]:
            unanimous += 1
    entry(E, "eq-unanimous-baseline",
          "%d of %d" % (unanimous, len(eq_slots)),
          [unanimous, len(eq_slots)],
          "equipoise slots whose as-qualified n=20 reference is "
          "unanimous")

    for cfg, ref_of in (("qualified", qualified_ref),
                        ("active", lambda r: r)):
        hist = collections.Counter(
            round(ref_of(rec)["band"]["p99"], 2)
            for items in baselines.values()
            for rec in items.values())
        entry(E, "band-histogram-" + cfg,
              ", ".join("%.2f x%d" % (b, c)
                        for b, c in sorted(hist.items())),
              {"%.2f" % b: c for b, c in sorted(hist.items())},
              "p99 histogram over the 340 slots, %s references"
              % cfg, provenance="constant")

    # ---- published-only figures (not regenerable here) -----------
    entry(E, "rerun-gap-minutes", "0.43 to 5.28",
          {"min": 0.43, "max": 5.28, "median": 2.4},
          "item-level gap, last probe sample to first rerun sample; "
          "12-day figures from probe/DRIFT_WINDOW_2026-08-07_to_13"
          ".md", provenance="raw-rows",
          note="regenerate from the local row store at the freeze; "
               "the verdict log holds only run-level start times")
    entry(E, "rerun-gap-median", "2.4", 2.4,
          "median of the same item-level gaps",
          provenance="raw-rows")
    entry(E, "rerun-gap-coarse", "0.4 to 5.3",
          {"min": 0.4, "max": 5.3},
          "the same range at one decimal, as section 3.4 prints it",
          provenance="raw-rows")
    entry(E, "event-power", "p = 0.68", 0.68,
          "EVENT/TRANSIENT discriminating power under the "
          "serving-state correlation model; session analysis, "
          "2026-08-16 deep read", provenance="no-script",
          note="numbers policy blocks this from the PDF until the "
               "analysis lands as a committed script")
    entry(E, "vuln-lockstep", "148 of 150",
          [148, 150],
          "answer-format lockstep samples on the sonnet vuln slot; "
          "12-day figure from the deep read", provenance="raw-rows",
          note="row lengths never enter the committed derived "
               "counts; regenerate from the local row store")

    # ---- write ---------------------------------------------------
    os.makedirs(fd.OUT, exist_ok=True)
    doc = {"data_through": end, "window": [start, end],
           "probe_days": n_days, "entries": E}
    with open(os.path.join(fd.OUT, "freeze_numbers.json"), "w",
              encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2, sort_keys=True)
        fh.write("\n")

    lines = ["# Freeze-number manifest",
             "",
             "Data through %s (%d probe days). Generated by "
             "paper/figures/freeze_numbers.py from the committed "
             "record; regenerate at the freeze and run "
             "check_draft_numbers.py." % (end, n_days), ""]
    by_prov = collections.defaultdict(list)
    for key in sorted(E):
        by_prov[E[key]["provenance"]].append(key)
    for prov in ("record", "constant", "raw-rows", "no-script"):
        if prov not in by_prov:
            continue
        lines += ["## %s" % prov, ""]
        lines += ["| key | renders as | source |",
                  "| --- | --- | --- |"]
        for key in by_prov[prov]:
            e = E[key]
            lines.append("| %s | %s | %s |"
                         % (key, e["render"], e["source"]))
        lines.append("")
        for key in by_prov[prov]:
            if "note" in E[key]:
                lines.append("- %s: %s" % (key, E[key]["note"]))
        lines.append("")
    with open(os.path.join(fd.OUT, "freeze_numbers.md"), "w",
              encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print("wrote freeze_numbers.{json,md} in %s"
          % os.path.relpath(fd.OUT, fd.REPO))
    print("%d entries: %s" % (len(E), ", ".join(
        "%d %s" % (len(v), k) for k, v in sorted(by_prov.items()))))


if __name__ == "__main__":
    main()
