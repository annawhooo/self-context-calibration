"""
Continuous drift monitor over the probing harness
(probe/claude_code_handoff_monitor.md). Companions: probe/ARCHITECTURE.md
(design), probe/NOISE_FLOOR.md (noise characterization and the per-item-band
rationale), probe/DRIFT_EVENT_2026-07-31.md (the three-run qualification
rationale), probe/REPORTING_COMMITMENT.md (quiet windows get published).

Commands (run from the repo root; scheduling is documented in
probe/monitor/README.md, no scheduler code lives here):

  monitor.py check-env
      SET or MISSING per required environment variable for every roster
      provider. Never prints values. Exit nonzero on any missing. Run once
      under the scheduled task's account when installing the task.

  monitor.py baseline --model <id>   (or --all)
      Baseline qualification for one roster model (or every roster model):
      two same-day K=10 bank runs, per-item smoothed simulation bands from
      run1, run-pair TVD checked against the p99 band, and a same-day third
      run of only the out-of-band items to disambiguate. Baselines land in
      probe/monitor/baselines/<model>.json: committed qualification records.

  monitor.py probe
      One K=10 bank run per roster model against its baseline, once daily
      via the scheduled task. Per alarm-set item, TVD against the baseline
      distribution is compared to that item's p99 band; any breach fires an
      immediate same-day rerun of the breached items only. One verdict line
      per model is appended to probe/monitor/verdicts.jsonl (committed; the
      longitudinal record is the point). Raw rows append under
      probe/monitor/rows/ (gitignored).

Reuse: request shaping, sending, retries, parsing, and row assembly are the
convergence collection machinery, imported (collect_row, build_request via
collect_row, post_with_retries, PROVIDERS, ITEMS, the parse path). Nothing
here shapes a request. The monitor carries its own roster
(probe/monitor/roster.json); convergence/models.json is not read.

Bands: Laplace-smoothed multinomial plug-in simulation, the
probe/scripts/validate_sim_thresholds.py method: the observed distribution
is smoothed (+1 per option), SIMS K-sized re-draws are simulated, and the
per-item p95/p99 of TVD-to-baseline are the bands. Seeds are deterministic
per model and item (seed_rule below) and recorded in the baseline file.

Baseline qualification per item (DRIFT_EVENT_2026-07-31.md, design
consequence 1):
  - run-pair TVD inside run1's p99 band: qualified for the alarm set;
    baseline distribution is run1+run2 pooled.
  - outside: third same-day run of that item.
      third matches run2, not run1: a drift event straddled calibration;
        the baseline is the post-event state (run2+run3), event recorded in
        the baseline file's events list.
      third matches run1: transient; pooled baseline (all three same-day
        runs), item qualified.
      matches neither: item classed sentinel; monitored and reported
        descriptively in every verdict, never a sole alarm trigger, never
        fires disambiguation.
  "Matches run X" is pinned as: TVD(run3, runX) <= the p99 smoothed
  simulation band computed from runX's distribution. The bullets apply in
  the order written, so a third run inside both bands reads as transient.

Daily verdicts: CLEAN, EVENT, TRANSIENT, UNSTABLE, ECHO_CHANGE, ERROR.
Disambiguation rerun, per breached item, same matching rule and bullet
order: matches the probe and not the baseline -> EVENT (re-baseline
recommended, never automatic); matches the baseline -> TRANSIENT; matches
neither -> UNSTABLE (flagged for sentinel review). A model's verdict is the
worst item verdict (EVENT > UNSTABLE > TRANSIENT).

Echo tripwire, as in collection: the baseline records the served model id
echo; a probe response echoing a different id halts that model's probe
immediately and ECHO_CHANGE is its own verdict. A response with no
parseable echo is absence, not change: counted, never a halt.

Exit codes (probe): 0 all CLEAN or TRANSIENT; 1 any EVENT, UNSTABLE, or
ECHO_CHANGE; 2 any ERROR (credentials, network exhaustion, parse collapse:
an item with zero parsed samples in a run). ERROR dominates when mixed.
Baseline uses the same scheme (1 echo tripwire, 2 error). Roster and
configuration refusals exit 2.

Credentials: fail-closed exactly as collection. Every required environment
variable is read before the first call; a missing one names itself and
issues zero requests. Keys live in request headers only; nothing here logs
or persists one.

Human-readable reporting goes to stderr. stdout stays quiet except for
check-env's SET/MISSING listing.
"""

import os
import sys
import json
import random
import argparse
import datetime
import collections

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "harness"))

from confab_harness_faithful import write_row, now_iso  # noqa: E402
from items.items import ITEMS  # noqa: E402
from convergence.providers import PROVIDERS, ProviderConfigError  # noqa: E402
from convergence.collect import (  # noqa: E402
    CredentialError, collect_row, load_roster, read_keys, select_models,
    validate_model_cfg,
)

HERE = os.path.dirname(os.path.abspath(__file__))
ROSTER_PATH = os.path.join(HERE, "roster.json")
BASELINES_DIR = os.path.join(HERE, "baselines")
ROWS_DIR = os.path.join(HERE, "rows")
VERDICTS_PATH = os.path.join(HERE, "verdicts.jsonl")

OPTIONS = ("A", "B", "C", "D")
K_SAMPLES = 10       # handoff: K=10, matching the convergence pre-registration
SIMS = 10000         # simulated re-draws per band (validate_sim_thresholds.py)
SMOOTH = 1.0         # Laplace smoothing per option
SEED_BASE = 20260802  # baseline files record the derived per-item seed
SEED_RULE = ("random.Random('<seed_base>:<model>:<item_id>' plus a purpose "
             "suffix ':run2', ':band', or ':disamb:<date>')")

VERDICTS = ("CLEAN", "EVENT", "TRANSIENT", "UNSTABLE", "ECHO_CHANGE", "ERROR")
_SEVERITY = {"TRANSIENT": 1, "UNSTABLE": 2, "EVENT": 3}


class MonitorError(RuntimeError):
    """A condition that voids a monitor run for one model: missing or stale
    baseline, bank/baseline item mismatch, or parse collapse (an item with
    zero parsed samples in a run). Maps to the ERROR verdict, exit 2."""


class EchoChange(RuntimeError):
    """The echo tripwire fired during a baseline run. Carries the halt
    detail; the baseline is not written."""

    def __init__(self, detail):
        self.detail = detail
        super().__init__(
            "ECHO CHANGE [{model}]: response echoed {divergent} against "
            "reference {reference} at item {item_id}; run halted, no "
            "baseline written.".format(**detail))


def local_date():
    return datetime.date.today().isoformat()


def item_seed(model, iid, suffix=None):
    """Deterministic per-model, per-item simulation seed, recorded in the
    baseline file so bands are reproducible (SEED_RULE)."""
    seed = "{}:{}:{}".format(SEED_BASE, model, iid)
    return "{}:{}".format(seed, suffix) if suffix else seed


def tvd(counts_a, counts_b, n_a, n_b):
    """Per-item total variation distance over the four options, each side
    normalized by its own parsed count (the analyzer/validate_sim_thresholds
    convention)."""
    return 0.5 * sum(abs(counts_a.get(o, 0) / n_a - counts_b.get(o, 0) / n_b)
                     for o in OPTIONS)


def observed_tvd(counts_a, counts_b):
    return tvd(counts_a, counts_b,
               sum(counts_a.values()), sum(counts_b.values()))


def smoothed_bands(counts, seed, k=K_SAMPLES, sims=SIMS, smooth=SMOOTH):
    """Laplace-smoothed plug-in bands, the validate_sim_thresholds.py method:
    smooth the observed distribution (+smooth per option), simulate sims
    K-sized re-draws, TVD each against the observed counts, and return the
    (p95, p99) percentiles with that script's index convention. smooth=0
    recovers the naive plug-in."""
    n = sum(counts.values())
    if n <= 0:
        raise MonitorError(
            "empty distribution: no parsed samples to simulate bands from")
    probs = [(counts.get(o, 0) + smooth) / (n + smooth * len(OPTIONS))
             for o in OPTIONS]
    rng = random.Random(seed)
    tvds = []
    for _ in range(sims):
        draw = collections.Counter(rng.choices(OPTIONS, weights=probs, k=k))
        tvds.append(tvd(counts, draw, n, k))
    tvds.sort()
    return tvds[int(0.95 * sims) - 1], tvds[int(0.99 * sims) - 1]


def validate_monitor_model(m):
    """Collection validation plus the monitor's single-arm pin."""
    validate_model_cfg(m)
    arms = m.get("arms") or []
    if len(arms) != 1:
        raise ProviderConfigError(
            "monitor roster entry {!r} pins {} arms; the monitor requires "
            "exactly one arm per entry".format(m.get("model"), len(arms)))


def run_bank(m, arm, items, k, api_key, run_id, fh, phase,
             reference_echo=None):
    """One K-sample pass over items for one model, through collect_row (the
    exact collection request shaping, sending, and parse path). Every row is
    appended durably before anything else happens to it.

    Echo tripwire: reference_echo, when given (probe: the baseline's recorded
    echo; baseline runs 2 and 3: run1's reference), is the reference. When
    None, the first parseable echo of the run sets it. A missing echo is
    counted, never sets or updates the reference, and never halts. On
    divergence the divergent row is already on disk as evidence; the run
    stops and echo_change carries the detail.

    Returns {"counts": {item_id: Counter}, "unparsed": {item_id: n},
    "reference": echo-or-None, "missing_echo": n, "calls": n,
    "echo_change": None-or-detail}.
    """
    counts = {item["id"]: collections.Counter() for item in items}
    unparsed = {}
    reference = reference_echo
    missing_echo = 0
    calls = 0
    echo_change = None
    for item in items:
        if echo_change:
            break
        for sample_index in range(k):
            row, echo = collect_row(m, arm, item, sample_index, api_key,
                                    run_id)
            row["phase"] = phase
            write_row(fh, row)
            calls += 1
            if row["parsed"] in OPTIONS:
                counts[item["id"]][row["parsed"]] += 1
            else:
                unparsed[item["id"]] = unparsed.get(item["id"], 0) + 1
            if echo is None:
                missing_echo += 1
            elif reference is None:
                reference = echo
            elif echo != reference:
                echo_change = {"model": m["model"], "reference": reference,
                               "divergent": echo, "item_id": item["id"]}
                break
    return {"counts": counts, "unparsed": unparsed, "reference": reference,
            "missing_echo": missing_echo, "calls": calls,
            "echo_change": echo_change}


def check_parse_collapse(run, items, mid, run_name):
    """An item with zero parsed samples cannot be compared: parse collapse,
    ERROR for the model, naming the items."""
    dead = [item["id"] for item in items
            if sum(run["counts"][item["id"]].values()) == 0]
    if dead:
        raise MonitorError(
            "parse collapse [{}] {}: zero parsed samples for item(s) "
            "{}".format(mid, run_name, ", ".join(dead)))


def baseline_path(mid, baselines_dir=None):
    return os.path.join(baselines_dir or BASELINES_DIR, mid + ".json")


def baseline_one(m, items, k, api_key, rows_dir, date):
    """Two same-day bank runs, band qualification, and the third-run
    disambiguation for out-of-band items. Returns the baseline record dict;
    raises EchoChange or MonitorError without writing one."""
    mid = m["model"]
    arm = m["arms"][0]
    os.makedirs(rows_dir, exist_ok=True)
    rows_path = os.path.join(rows_dir, "baseline_{}_{}.jsonl".format(mid, date))
    run_ids = {}
    fh = open(rows_path, "a", encoding="utf-8")
    try:
        run_ids["run1"] = now_iso()
        run1 = run_bank(m, arm, items, k, api_key, run_ids["run1"], fh,
                        "monitor_baseline_run1")
        if run1["echo_change"]:
            raise EchoChange(run1["echo_change"])
        check_parse_collapse(run1, items, mid, "run1")

        run_ids["run2"] = now_iso()
        run2 = run_bank(m, arm, items, k, api_key, run_ids["run2"], fh,
                        "monitor_baseline_run2",
                        reference_echo=run1["reference"])
        if run2["echo_change"]:
            raise EchoChange(run2["echo_change"])
        check_parse_collapse(run2, items, mid, "run2")

        records = {}
        events = []
        third_items = []
        for item in items:
            iid = item["id"]
            c1, c2 = run1["counts"][iid], run2["counts"][iid]
            p95, p99 = smoothed_bands(c1, item_seed(mid, iid))
            obs = observed_tvd(c1, c2)
            rec = {
                "class": None,
                "runs": {"run1": dict(c1), "run2": dict(c2)},
                "unparsed": {"run1": run1["unparsed"].get(iid, 0),
                             "run2": run2["unparsed"].get(iid, 0)},
                "qualification": {"seed": item_seed(mid, iid),
                                  "p95": p95, "p99": p99,
                                  "observed_run_pair_tvd": obs,
                                  "third_run": None},
            }
            if obs <= p99:
                rec["class"] = "alarm"
                rec["_pooled"] = c1 + c2
            else:
                third_items.append(item)
            records[iid] = rec

        if third_items:
            run_ids["run3"] = now_iso()
            run3 = run_bank(m, arm, third_items, k, api_key, run_ids["run3"],
                            fh, "monitor_baseline_run3",
                            reference_echo=run1["reference"])
            if run3["echo_change"]:
                raise EchoChange(run3["echo_change"])
            check_parse_collapse(run3, third_items, mid, "run3")
            for item in third_items:
                iid = item["id"]
                rec = records[iid]
                c1 = run1["counts"][iid]
                c2 = run2["counts"][iid]
                c3 = run3["counts"][iid]
                p95_2, p99_2 = smoothed_bands(c2, item_seed(mid, iid, "run2"))
                t31 = observed_tvd(c1, c3)
                t32 = observed_tvd(c2, c3)
                matches1 = t31 <= rec["qualification"]["p99"]
                matches2 = t32 <= p99_2
                third = {"run2_seed": item_seed(mid, iid, "run2"),
                         "run2_p95": p95_2, "run2_p99": p99_2,
                         "tvd_vs_run1": t31, "tvd_vs_run2": t32}
                if matches2 and not matches1:
                    third["outcome"] = "drift_during_calibration"
                    rec["class"] = "alarm"
                    rec["_pooled"] = c2 + c3
                    events.append({
                        "item_id": iid, "date": date,
                        "detail": "run-pair TVD {} exceeded p99 {}; third "
                                  "run matched run2 (TVD {}) and not run1 "
                                  "(TVD {}): a drift event straddled "
                                  "calibration; baseline is the post-event "
                                  "state (run2+run3)".format(
                                      round(obs_of(rec), 4),
                                      round(rec["qualification"]["p99"], 4),
                                      round(t32, 4), round(t31, 4)),
                    })
                elif matches1:
                    third["outcome"] = "transient"
                    rec["class"] = "alarm"
                    rec["_pooled"] = c1 + c2 + c3
                else:
                    third["outcome"] = "sentinel"
                    rec["class"] = "sentinel"
                    rec["_pooled"] = c1 + c2 + c3
                rec["runs"]["run3"] = dict(c3)
                rec["unparsed"]["run3"] = run3["unparsed"].get(iid, 0)
                rec["qualification"]["third_run"] = third
    finally:
        fh.close()

    for iid, rec in records.items():
        pooled = rec.pop("_pooled")
        band_seed = item_seed(mid, iid, "band")
        p95, p99 = smoothed_bands(pooled, band_seed)
        rec["baseline_counts"] = dict(pooled)
        rec["n"] = sum(pooled.values())
        rec["band"] = {"seed": band_seed, "p95": p95, "p99": p99}

    return {
        "model": mid,
        "provider": m["provider"],
        "arm": arm,
        "k": k,
        "sims": SIMS,
        "smooth": SMOOTH,
        "seed_base": SEED_BASE,
        "seed_rule": SEED_RULE,
        "options": list(OPTIONS),
        "date": date,
        "run_ids": run_ids,
        "model_id_echo": run1["reference"],
        "missing_echo": {name: r for name, r in
                         (("run1", run1["missing_echo"]),
                          ("run2", run2["missing_echo"])) if r},
        "rows": os.path.relpath(rows_path, REPO).replace(os.sep, "/"),
        "events": events,
        "items": records,
    }


def obs_of(rec):
    return rec["qualification"]["observed_run_pair_tvd"]


def run_baseline(models, items=None, k=K_SAMPLES, baselines_dir=None,
                 rows_dir=None):
    """Baseline command over the selected roster models. Validation, then
    credentials for every selected provider, then the first request, in that
    order; a failure on one model is reported and the rest continue. Returns
    the exit code (0 ok everywhere, 1 echo tripwire, 2 error; 2 dominates)."""
    items = list(items) if items is not None else list(ITEMS)
    baselines_dir = baselines_dir or BASELINES_DIR
    rows_dir = rows_dir or ROWS_DIR
    for m in models:
        validate_monitor_model(m)
    keys = read_keys(models)
    date = local_date()
    code = 0
    for m in models:
        mid = m["model"]
        try:
            baseline = baseline_one(m, items, k, keys[m["provider"]],
                                    rows_dir, date)
        except EchoChange as exc:
            sys.stderr.write(str(exc) + "\n")
            code = max(code, 1)
            continue
        except (MonitorError, RuntimeError) as exc:
            sys.stderr.write("BASELINE ERROR [{}]: {}\n".format(mid, exc))
            code = 2
            continue
        os.makedirs(baselines_dir, exist_ok=True)
        path = baseline_path(mid, baselines_dir)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(baseline, f, indent=2)
            f.write("\n")
        classes = collections.Counter(
            rec["class"] for rec in baseline["items"].values())
        sys.stderr.write(
            "BASELINE [{}]: {} items qualified for the alarm set, {} "
            "sentinel, {} calibration-window drift event(s); echo {}; "
            "written to {} (a committed qualification record).\n".format(
                mid, classes.get("alarm", 0), classes.get("sentinel", 0),
                len(baseline["events"]), baseline["model_id_echo"],
                os.path.relpath(path, REPO)))
        for event in baseline["events"]:
            sys.stderr.write("BASELINE EVENT [{}] {}: {}\n".format(
                mid, event["item_id"], event["detail"]))
    return code


def probe_one(m, baseline, items, k, api_key, fh, date):
    """One daily bank run for one model against its baseline, with the
    same-day disambiguation rerun for breached alarm items. Returns the
    verdict line dict."""
    mid = m["model"]
    arm = m["arms"][0]
    if baseline.get("arm") != arm:
        raise MonitorError(
            "baseline for {} was qualified on arm {} but the roster now "
            "pins arm {}; re-baseline before probing".format(
                mid, baseline.get("arm"), arm))
    by_id = {item["id"]: item for item in items}
    missing = [iid for iid in baseline["items"] if iid not in by_id]
    if missing:
        raise MonitorError(
            "bank/baseline mismatch [{}]: baseline item(s) {} not in the "
            "current bank; re-baseline before probing".format(
                mid, ", ".join(missing)))

    run_ids = {"probe": now_iso()}
    probe_items = [by_id[iid] for iid in baseline["items"]]
    run = run_bank(m, arm, probe_items, k, api_key, run_ids["probe"], fh,
                   "monitor_probe", reference_echo=baseline["model_id_echo"])
    calls = run["calls"]
    line = {"date": date, "model": mid,
            "model_id_echo": run["reference"], "verdict": None,
            "breached": [], "sentinels": {}, "unparsed": 0,
            "calls": calls, "run_ids": run_ids}
    if run["echo_change"]:
        line["verdict"] = "ECHO_CHANGE"
        line["echo_change"] = run["echo_change"]
        return line
    check_parse_collapse(run, probe_items, mid, "probe")
    line["unparsed"] = sum(run["unparsed"].values())

    breached = []
    for iid, rec in baseline["items"].items():
        base = collections.Counter(rec["baseline_counts"])
        t = observed_tvd(base, run["counts"][iid])
        if rec["class"] == "sentinel":
            # Reported descriptively in every verdict, never a sole alarm
            # trigger, never fires disambiguation.
            line["sentinels"][iid] = {"observed_tvd": t,
                                      "p99": rec["band"]["p99"]}
        elif t > rec["band"]["p99"]:
            breached.append({"item_id": iid, "observed_tvd": t,
                             "p99": rec["band"]["p99"]})
    line["breached"] = breached
    if not breached:
        line["verdict"] = "CLEAN"
        return line

    run_ids["rerun"] = now_iso()
    rerun_items = [by_id[b["item_id"]] for b in breached]
    rerun = run_bank(m, arm, rerun_items, k, api_key, run_ids["rerun"], fh,
                     "monitor_rerun", reference_echo=baseline["model_id_echo"])
    line["calls"] = calls + rerun["calls"]
    if rerun["echo_change"]:
        line["verdict"] = "ECHO_CHANGE"
        line["echo_change"] = rerun["echo_change"]
        return line
    check_parse_collapse(rerun, rerun_items, mid, "rerun")
    line["unparsed"] += sum(rerun["unparsed"].values())

    worst = 0
    for b in breached:
        iid = b["item_id"]
        rec = baseline["items"][iid]
        base = collections.Counter(rec["baseline_counts"])
        probe_counts = run["counts"][iid]
        rerun_counts = rerun["counts"][iid]
        seed = item_seed(mid, iid, "disamb:" + date)
        _p95, probe_p99 = smoothed_bands(probe_counts, seed)
        t_probe = observed_tvd(probe_counts, rerun_counts)
        t_base = observed_tvd(base, rerun_counts)
        matches_probe = t_probe <= probe_p99
        matches_base = t_base <= rec["band"]["p99"]
        if matches_probe and not matches_base:
            item_verdict = "EVENT"
        elif matches_base:
            item_verdict = "TRANSIENT"
        else:
            item_verdict = "UNSTABLE"
        b.update({"rerun_tvd_vs_probe": t_probe,
                  "rerun_probe_p99": probe_p99, "rerun_probe_seed": seed,
                  "rerun_tvd_vs_baseline": t_base,
                  "item_verdict": item_verdict})
        worst = max(worst, _SEVERITY[item_verdict])
    line["verdict"] = [v for v, s in _SEVERITY.items() if s == worst][0]
    return line


def append_verdict(path, line):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        write_row(fh, line)


def report_verdict(line):
    """Human-readable per-model report line on stderr."""
    parts = ["VERDICT [{}] {} ({})".format(line["model"], line["verdict"],
                                           line["date"])]
    if line.get("error"):
        parts.append("error: {}".format(line["error"]))
    if line.get("echo_change"):
        e = line["echo_change"]
        parts.append("echoed {} against reference {} at item {}".format(
            e["divergent"], e["reference"], e["item_id"]))
    for b in line.get("breached", []):
        detail = "{} observed {} vs p99 {}".format(
            b["item_id"], round(b["observed_tvd"], 4), round(b["p99"], 4))
        if "item_verdict" in b:
            detail += " -> {}".format(b["item_verdict"])
        parts.append(detail)
    if line.get("sentinels"):
        parts.append("sentinels: " + ", ".join(
            "{} tvd {}".format(iid, round(s["observed_tvd"], 4))
            for iid, s in sorted(line["sentinels"].items())))
    parts.append("calls {}".format(line["calls"]))
    sys.stderr.write("; ".join(parts) + "\n")
    if line["verdict"] == "EVENT":
        sys.stderr.write(
            "  Re-baseline recommended (never automatic): monitor.py "
            "baseline --model {}\n".format(line["model"]))
    if line["verdict"] == "UNSTABLE":
        sys.stderr.write(
            "  Item(s) flagged for sentinel review; reclassification is a "
            "human decision on the committed baseline file.\n")


def run_probe(models, items=None, k=K_SAMPLES, baselines_dir=None,
              rows_dir=None, verdicts_path=None):
    """Daily probe over the whole roster. Returns the exit code: 0 all
    CLEAN or TRANSIENT; 1 any EVENT, UNSTABLE, or ECHO_CHANGE; 2 any ERROR
    (dominant when mixed)."""
    items = list(items) if items is not None else list(ITEMS)
    baselines_dir = baselines_dir or BASELINES_DIR
    rows_dir = rows_dir or ROWS_DIR
    verdicts_path = verdicts_path or VERDICTS_PATH
    for m in models:
        validate_monitor_model(m)
    date = local_date()
    try:
        keys = read_keys(models)
    except CredentialError as exc:
        # Fail-closed with zero requests, but the outage still lands in the
        # longitudinal record: one ERROR line per model.
        for m in models:
            line = {"date": date, "model": m["model"], "model_id_echo": None,
                    "verdict": "ERROR", "error": str(exc), "breached": [],
                    "sentinels": {}, "unparsed": 0, "calls": 0,
                    "run_ids": {}}
            append_verdict(verdicts_path, line)
            report_verdict(line)
        sys.stderr.write(str(exc) + "\n")
        return 2

    os.makedirs(rows_dir, exist_ok=True)
    rows_path = os.path.join(rows_dir, "probe_{}.jsonl".format(date))
    lines = []
    fh = open(rows_path, "a", encoding="utf-8")
    try:
        for m in models:
            mid = m["model"]
            try:
                path = baseline_path(mid, baselines_dir)
                if not os.path.exists(path):
                    raise MonitorError(
                        "no baseline for {}: expected {}. Run monitor.py "
                        "baseline --model {} first.".format(
                            mid, os.path.relpath(path, REPO), mid))
                with open(path, encoding="utf-8") as f:
                    baseline = json.load(f)
                line = probe_one(m, baseline, items, k, keys[m["provider"]],
                                 fh, date)
            except (MonitorError, RuntimeError) as exc:
                line = {"date": date, "model": mid, "model_id_echo": None,
                        "verdict": "ERROR", "error": str(exc),
                        "breached": [], "sentinels": {}, "unparsed": 0,
                        "calls": None, "run_ids": {}}
            append_verdict(verdicts_path, line)
            report_verdict(line)
            lines.append(line)
    finally:
        fh.close()

    verdicts = {line["verdict"] for line in lines}
    if "ERROR" in verdicts:
        return 2
    if verdicts & {"EVENT", "UNSTABLE", "ECHO_CHANGE"}:
        return 1
    return 0


def run_check_env(models):
    """SET or MISSING per required environment variable, values never
    printed. Exit nonzero on any missing. Issues zero requests. This exists
    because scheduled-task environments have burned us before; the README
    requires running it once under the task's account."""
    for m in models:
        validate_monitor_model(m)
    envs = []
    for m in models:
        env = PROVIDERS[m["provider"]]["env"]
        if env not in envs:
            envs.append(env)
    missing = 0
    for env in envs:
        state = "SET" if os.environ.get(env) else "MISSING"
        if state == "MISSING":
            missing += 1
        print("{} {}".format(env, state))
    return 1 if missing else 0


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="monitor.py",
        description="Continuous drift monitor over the probing harness: "
                    "baseline qualification, daily probes with "
                    "auto-disambiguation, and a committed verdict log. "
                    "Scheduling is documented in probe/monitor/README.md.")
    sub = ap.add_subparsers(dest="command")
    sub.required = True
    pb = sub.add_parser("baseline",
                        help="two same-day bank runs, band qualification, "
                             "third-run disambiguation; writes "
                             "baselines/<model>.json")
    pb.add_argument("--model", default=None,
                    help="one roster model id (comma-separation accepted)")
    pb.add_argument("--all", action="store_true",
                    help="baseline every roster model")
    pb.add_argument("--roster", default=ROSTER_PATH,
                    help="roster json (default probe/monitor/roster.json)")
    pp = sub.add_parser("probe",
                        help="one daily bank run per roster model against "
                             "its baseline; appends verdicts.jsonl")
    pp.add_argument("--roster", default=ROSTER_PATH)
    pc = sub.add_parser("check-env",
                        help="SET/MISSING per required env var, no values, "
                             "nonzero exit on any missing")
    pc.add_argument("--roster", default=ROSTER_PATH)
    args = ap.parse_args(argv)

    try:
        roster = load_roster(args.roster)
        if args.command == "check-env":
            return run_check_env(roster)
        if args.command == "probe":
            return run_probe(list(roster))
        # baseline
        if bool(args.model) == bool(args.all):
            ap.error("baseline requires exactly one of --model <id> or --all")
        models = (select_models(roster, args.model) if args.model
                  else list(roster))
        return run_baseline(models)
    except (ProviderConfigError, CredentialError, MonitorError) as exc:
        sys.stderr.write(str(exc) + "\n")
        return 2


if __name__ == "__main__":
    sys.exit(main())
