"""
Convergence study collection runner (convergence/PRE_REGISTRATION_CONVERGENCE.md).

Runs the existing 68-item bank as fresh single-turn judgment against models
from five providers in two arms, writing rows schema-compatible with the
faithful baseline arm. The stimulus (item bank, prompt text, parse rule) is
IMPORTED from the faithful harness and the shared bank, never copied, so it
stays byte-identical by construction; convergence/tests/test_byte_identity.py
pins the bytes. The faithful harness, analyzer, item bank, and their tests
are read-only for this study; this module only imports from them.

Usage:
  python convergence/collect.py --arm A                 collect Arm A (reasoning off)
  python convergence/collect.py --arm B                 collect Arm B (reasoning on)
  python convergence/collect.py --verify-reasoning      Arm A disable smoke test
  python convergence/collect.py --probe-sampling        sampling-variance probe
Options: --config (roster json), --models (comma-separated roster ids),
--out (rows jsonl), --k (samples per item per model, default 10 per the
pre-registration), --verify-n, --verify-out.

Roster: convergence/models.json. Exact OpenAI, Google, DeepSeek, and Z.ai
model ids are lock-day configuration; entries ship as PIN_AT_LOCK
placeholders that this runner refuses to run.

Row schema: the faithful baseline fields unchanged (run_id, phase, model,
item_id, item_cell, sample_index, parsed, raw_text, ts) extended with
provider, model_id_exact (the id the provider's response reports, falling
back to the requested id when the response carries none), host (for
open-weight models, including any quantization string the host reports),
arm ("A" or "B"), reasoning_requested ("off" or "on"), reasoning_detected
(bool, or null when the response exposes no detection surface), and
temperature_sent (1.0 or null).

Credentials: one environment variable per provider (see providers.PROVIDERS),
read once at start for every provider in the selection, before any request
and before the output file is opened. A missing variable fails closed with
CredentialError naming it. Keys are never logged and never written to any
row or log line; they exist only in request headers.

Recovery: every completed row is appended and flushed immediately
(write_row), so an aborted run leaves all completed rows on disk. A rerun
scans the output file and tops up only missing (provider, model, arm,
item_id, sample_index) slots, regardless of run_id.

Echo-change halt (collection only, always on; the pre-registration's
preview-id tripwire): each model holds a reference echo id. Before a
model's first call the existing output file is read: exactly one distinct
prior model_id_exact is the reference (so the rule spans resumed runs);
more than one refuses collection for that model, naming the ids, because
the data is already split and needs human partitioning; no prior rows means
the first echoed response of the run sets the reference. On divergence the
divergent row is written durably as evidence, collection stops for that
model, remaining models continue, and the run exits nonzero at the end.
Analysis partitions rows by model_id_exact, so the divergent row forms its
own cell. A response with no parseable echo never halts and never sets or
updates the reference; it is counted and reported per model.
--verify-reasoning and --probe-sampling are not subject to the check.

Reasoning-disable verification (--verify-reasoning): the pre-registration
makes reasoning-off a void condition requiring positive verification. For
each Arm A model this mode issues a small number of calls with reasoning
disabled and reports, per the provider's pinned detection surface, whether
reasoning content appeared anyway. An undetectable state is reported as
unverifiable, never as success.

Sampling-variance probe (--probe-sampling): the pre-registration's
non-greedy sampling check at smoke. For every roster model and every arm it
lists, the pinned probe prompt is issued three times through the exact
collection request shaping (same adapter, reasoning config,
temperature_mode, retry sender). VARIED when any two outputs differ at byte
level; DEGENERATE when all three are byte-identical; ERROR when any call
fails after retries, reported without a verdict rather than folded into
either state. DEGENERATE or ERROR anywhere exits nonzero. Full outputs land
in a timestamped jsonl under convergence/probe_reports/ (gitignored); probe
calls write no collection rows and touch no collection output paths. When
investigating a DEGENERATE verdict, consider provider-side response caching
of identical requests before concluding greedy decoding.
"""

import os
import sys
import json
import argparse

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "harness"))

# Stimulus and row plumbing, imported from the faithful harness (byte-identity
# by import, per the pre-registration's analysis-side controls) and the shared
# item bank.
from confab_harness_faithful import (  # noqa: E402
    baseline_prompt, parse_baseline_answer, write_row, now_iso,
)
from items.items import ITEMS  # noqa: E402
from convergence.providers import (  # noqa: E402
    PROVIDERS, ProviderConfigError, build_request, parse_response,
    post_with_retries,
)

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG = os.path.join(HERE, "models.json")
DEFAULT_OUT = os.path.join(HERE, "results", "convergence_rows.jsonl")
DEFAULT_VERIFY_OUT = os.path.join(HERE, "results", "verify_reasoning.jsonl")

K_SAMPLES = 10          # pre-registration: K = 10 samples per item per model per arm
VERIFY_N = 3            # verification mode: calls per Arm A model

PLACEHOLDER_PREFIX = "PIN_AT_LOCK"

# Sampling-variance probe (pre-registration, Voids). One fixed open-ended
# prompt, pinned byte-for-byte like the vendor_access stimulus
# (convergence/tests/test_probe_sampling.py holds the tripwire literal), three
# calls per model per arm.
PROBE_PROMPT = ("In two or three sentences, describe an imaginary small "
                "town, including its name and one notable landmark.")
PROBE_N = 3
DEFAULT_PROBE_DIR = os.path.join(HERE, "probe_reports")


class CredentialError(RuntimeError):
    """A provider key is missing from the environment. Raised before any
    request is issued and before any output file is touched."""


def get_api_key(provider):
    """Read the provider's key from its single pinned environment variable.
    Fail closed naming the variable; never log or persist the value."""
    env = PROVIDERS[provider]["env"]
    key = os.environ.get(env)
    if not key:
        raise CredentialError(
            "{} is not set. Export the {} API key before running; the runner "
            "fails closed and no request was issued.".format(env, provider))
    return key


def validate_model_cfg(m):
    """Reject a roster entry that must never reach the network. Runs before
    the credential read, which runs before any request."""
    provider = m.get("provider")
    if provider not in PROVIDERS:
        raise ProviderConfigError(
            "unknown provider {!r} in roster entry {!r}; valid: {}".format(
                provider, m.get("model"), ", ".join(sorted(PROVIDERS))))
    model = m.get("model") or ""
    if model.startswith(PLACEHOLDER_PREFIX):
        raise ProviderConfigError(
            "placeholder model id {!r}: exact ids are pinned on lock day in "
            "models.json, not in code. Refusing to run until it is "
            "replaced.".format(model))
    if not model:
        raise ProviderConfigError("roster entry with empty model id")
    arms = m.get("arms") or []
    if not arms or not set(arms) <= {"A", "B"}:
        raise ProviderConfigError(
            "roster entry {!r} has invalid arms {!r}; valid: subsets of "
            "A, B".format(model, arms))
    if provider == "google" and "A" in arms:
        raise ProviderConfigError(
            "roster entry {!r}: google runs Arm B only (reasoning cannot be "
            "disabled on Gemini 3.x)".format(model))
    if m.get("temperature_mode") not in ("send", "omit"):
        raise ProviderConfigError(
            "roster entry {!r} needs temperature_mode 'send' or 'omit' "
            "(pinned per model; 1.0 where the API accepts it, omitted where "
            "it rejects it; never 0)".format(model))
    if provider == "anthropic" and "B" in arms and not m.get("thinking_on"):
        raise ProviderConfigError(
            "roster entry {!r}: anthropic Arm B requires thinking_on "
            "(adaptive, or enabled with a budget)".format(model))


def load_roster(path):
    """Load the roster json. Entries are validated per selected model at run
    entry, not here, so a template holding placeholders still loads."""
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    models = cfg.get("models")
    if not models:
        raise ProviderConfigError("no models in roster {}".format(path))
    return models


def select_models(roster, models_arg):
    """Resolve a comma-separated id list against the roster, preserving the
    order given (mirrors the harness resolve_models semantics). None selects
    the whole roster."""
    if models_arg is None:
        return list(roster)
    requested = [m.strip() for m in models_arg.split(",") if m.strip()]
    if not requested:
        raise ProviderConfigError(
            "--models was given but contains no model ids: {!r}".format(models_arg))
    by_id = {m["model"]: m for m in roster}
    unknown = [m for m in requested if m not in by_id]
    if unknown:
        raise ProviderConfigError(
            "unknown model id(s): {}. Roster ids: {}".format(
                ", ".join(unknown), ", ".join(sorted(by_id))))
    return [by_id[m] for m in requested]


def read_keys(models):
    """Read every selected provider's key up front, so a missing credential
    fails the whole run before the first request."""
    keys = {}
    for m in models:
        provider = m["provider"]
        if provider not in keys:
            keys[provider] = get_api_key(provider)
    return keys


def completed_slots(out_path):
    """Slots already on disk, keyed (provider, model, arm, item_id,
    sample_index) across all run_ids: the recovery convention tops up only
    missing slots. A torn final line from an aborted run is skipped."""
    done = set()
    if not os.path.exists(out_path):
        return done
    with open(out_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            done.add((r.get("provider"), r.get("model"), r.get("arm"),
                      r.get("item_id"), r.get("sample_index")))
    return done


def collect_row(m, arm, item, sample_index, api_key, run_id):
    """One single-turn call. Returns (row, echo): the finished row dict and
    the raw model id echo before the requested-id fallback, which the echo
    tripwire needs because a missing echo must read as absence, never as
    change."""
    provider = m["provider"]
    url, headers, body, temperature_sent = build_request(
        m, arm, baseline_prompt(item), api_key)
    data = post_with_retries(url, headers, body, PROVIDERS[provider]["retryable"])
    parsed_resp = parse_response(provider, data)
    echo = parsed_resp["model_id_exact"]
    row = {
        "run_id": run_id, "phase": "baseline", "model": m["model"],
        "item_id": item["id"], "item_cell": item.get("cell"),
        "sample_index": sample_index,
        "parsed": parse_baseline_answer(parsed_resp["text"]),
        "raw_text": parsed_resp["text"], "ts": now_iso(),
        "provider": provider,
        "model_id_exact": echo or m["model"],
        "host": m.get("host"), "arm": arm,
        "reasoning_requested": "off" if arm == "A" else "on",
        "reasoning_detected": parsed_resp["reasoning_present"],
        "temperature_sent": temperature_sent,
    }
    return row, echo


def scan_echoes(out_path):
    """Per-model counts of model_id_exact over the existing output file,
    keyed model -> {id: n}. The reference scan for the echo tripwire; spans
    resumed runs because it reads whatever is already on disk. Tolerates a
    torn final line like completed_slots."""
    counts = {}
    if not os.path.exists(out_path):
        return counts
    with open(out_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            model = r.get("model")
            echoed = r.get("model_id_exact")
            if model is None or echoed is None:
                continue
            per_model = counts.setdefault(model, {})
            per_model[echoed] = per_model.get(echoed, 0) + 1
    return counts


def collection_failed(status):
    """True when the echo tripwire refused or halted anything: the run
    exits nonzero at the end per the pre-registered rule."""
    return bool(status["refused"] or status["halted"])


def run_collection(models, arm, out_path, k=K_SAMPLES, items=None, run_id=None):
    """Collect k samples per item per selected model on one arm, appending
    each row durably as it completes. Validation, then credentials, then the
    first request, in that order; an abort at any point leaves every
    completed row on disk."""
    items = list(items) if items is not None else list(ITEMS)
    for m in models:
        validate_model_cfg(m)
    runnable = []
    for m in models:
        if arm in m["arms"]:
            runnable.append(m)
        else:
            sys.stderr.write("ARM SKIP [{}]: not configured for arm {}"
                             " (arms: {}).\n".format(m["model"], arm,
                                                     ",".join(m["arms"])))
    if not runnable:
        raise ProviderConfigError(
            "no selected model is configured for arm {}".format(arm))
    keys = read_keys(runnable)
    run_id = run_id or now_iso()
    done = completed_slots(out_path)

    # Echo tripwire references (pre-registration, preview-id mitigations).
    # One distinct prior echo is the reference; more than one refuses the
    # model; none means the first echoed response of this run sets it.
    echo_counts = scan_echoes(out_path)
    references = {}
    status = {"refused": [], "halted": [], "missing_echo": {}}
    kept = []
    for m in runnable:
        prior = echo_counts.get(m["model"]) or {}
        if len(prior) > 1:
            ids = sorted(prior)
            status["refused"].append({"model": m["model"], "ids": ids})
            sys.stderr.write(
                "ECHO REFUSAL [{}]: prior rows in {} carry {} distinct "
                "model_id_exact values: {}. The data is already split and "
                "needs human partitioning before more rows land; refusing to "
                "start collection for this model.\n".format(
                    m["model"], out_path, len(ids), ", ".join(ids)))
            continue
        if prior:
            references[m["model"]] = next(iter(prior))
        kept.append(m)
    runnable = kept

    tally = {}   # (model, label) -> count, label in A..D, "null"
    detect = {}  # model -> {True/False/None: count}
    skipped = 0

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    fh = open(out_path, "a", encoding="utf-8")
    try:
        for m in runnable:
            provider = m["provider"]
            mid = m["model"]
            halted = False
            for item in items:
                if halted:
                    break
                for sample_index in range(k):
                    slot = (provider, mid, arm, item["id"], sample_index)
                    if slot in done:
                        skipped += 1
                        continue
                    row, echo = collect_row(m, arm, item, sample_index,
                                            keys[provider], run_id)
                    # The divergent row is written first, durable append, so
                    # it remains on disk as evidence; the halt check runs on
                    # the raw echo afterwards.
                    write_row(fh, row)
                    label = row["parsed"] if row["parsed"] else "null"
                    tally[(mid, label)] = tally.get((mid, label), 0) + 1
                    d = detect.setdefault(mid, {})
                    d[row["reasoning_detected"]] = d.get(row["reasoning_detected"], 0) + 1
                    per_model = echo_counts.setdefault(mid, {})
                    per_model[row["model_id_exact"]] = \
                        per_model.get(row["model_id_exact"], 0) + 1
                    if echo is None:
                        # Absence is not change: counted, reported at the
                        # end, and the reference is never set from it.
                        status["missing_echo"][mid] = \
                            status["missing_echo"].get(mid, 0) + 1
                    elif references.get(mid) is None:
                        references[mid] = echo
                    elif echo != references[mid]:
                        ref = references[mid]
                        status["halted"].append({
                            "model": mid, "reference": ref,
                            "divergent": echo,
                            "reference_rows": per_model.get(ref, 0),
                            "divergent_rows": per_model.get(echo, 0),
                        })
                        sys.stderr.write(
                            "ECHO HALT [{}]: response echoed {} against "
                            "reference {}; {} row(s) on the reference side, "
                            "{} on the divergent side. The divergent row is "
                            "written and forms its own cell per the "
                            "pre-registered rule; collection stopped for "
                            "this model, continuing with any remaining "
                            "models.\n".format(
                                mid, echo, ref, per_model.get(ref, 0),
                                per_model.get(echo, 0)))
                        halted = True
                        break
    finally:
        fh.close()

    print("\nConvergence collection, arm {}, run {}".format(arm, run_id))
    if skipped:
        print("Topped up around {} already-completed slots.".format(skipped))
    for m in runnable:
        model = m["model"]
        dist = {lab: n for (mod, lab), n in sorted(tally.items()) if mod == model}
        if not dist:
            print("{:<34} all slots already on disk".format(model))
            continue
        total = sum(dist.values())
        dist_str = ", ".join("{}={}".format(lab, n) for lab, n in sorted(dist.items()))
        print("{:<34} n={} {}".format(model, total, dist_str))
        d = detect.get(model, {})
        if arm == "A" and d.get(True):
            sys.stderr.write(
                "REASONING WARNING [{}]: reasoning content detected on {} Arm A "
                "row(s) despite the disable. Void condition; exclude from Arm A "
                "and report.\n".format(model, d[True]))
        if d.get(None):
            sys.stderr.write(
                "DETECTION NOTE [{}]: {} row(s) exposed no reasoning-presence "
                "surface (reasoning_detected null). Positive verification is "
                "unavailable for those rows; report per the "
                "pre-registration.\n".format(model, d[None]))
    for mid, n_missing in sorted(status["missing_echo"].items()):
        sys.stderr.write(
            "MISSING ECHO NOTE [{}]: {} response(s) carried no parseable "
            "model id echo; recorded with the requested id, never setting "
            "or updating the reference.\n".format(mid, n_missing))
    print("Rows: {}".format(out_path))
    return status


def verify_reasoning(models, out_path=DEFAULT_VERIFY_OUT, n=VERIFY_N,
                     items=None, run_id=None):
    """Arm A reasoning-disable smoke test (pre-registration void condition).
    Issues n reasoning-off calls per Arm A model and reports, per the
    provider's pinned detection surface, whether reasoning content appeared
    despite being disabled. Rows are appended durably with phase
    verify_reasoning. Returns {model: verdict} with verdict one of
    verified_off, reasoning_present, undetectable."""
    items = list(items) if items is not None else list(ITEMS)
    for m in models:
        validate_model_cfg(m)
    arm_a = [m for m in models if "A" in m["arms"]]
    if not arm_a:
        raise ProviderConfigError(
            "no selected model is configured for Arm A; nothing to verify")
    keys = read_keys(arm_a)
    run_id = run_id or now_iso()
    item = items[0]

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    verdicts = {}
    fh = open(out_path, "a", encoding="utf-8")
    try:
        print("\nReasoning-disable verification (Arm A), run {}".format(run_id))
        for m in arm_a:
            detections = []
            for sample_index in range(n):
                row, _echo = collect_row(m, "A", item, sample_index,
                                         keys[m["provider"]], run_id)
                row["phase"] = "verify_reasoning"
                write_row(fh, row)
                detections.append(row["reasoning_detected"])
            if any(d is True for d in detections):
                verdict = "reasoning_present"
                msg = ("VOID: reasoning content appeared in {}/{} responses "
                       "despite the disable. Exclude from Arm A and report."
                       .format(sum(1 for d in detections if d is True), n))
            elif any(d is None for d in detections):
                verdict = "undetectable"
                msg = ("UNVERIFIABLE: {}/{} responses exposed no "
                       "reasoning-presence surface. Positive verification is "
                       "unavailable; report this, do not assume success."
                       .format(sum(1 for d in detections if d is None), n))
            else:
                verdict = "verified_off"
                msg = ("verified off: no reasoning content in {}/{} responses."
                       .format(n, n))
            verdicts[m["model"]] = verdict
            print("{:<34} {}".format(m["model"], msg))
    finally:
        fh.close()
    print("Verification rows: {}".format(out_path))
    return verdicts


def probe_verdict(results):
    """Verdict for one model and arm from three call results, each ("ok",
    text) or ("error", message). ERROR when any call failed after retries,
    reported without a verdict rather than folded into either state.
    DEGENERATE when all outputs are byte-identical; VARIED when any two
    differ at byte level (two-same-one-different is VARIED)."""
    if any(status == "error" for status, _ in results):
        return "ERROR"
    texts = [text for _, text in results]
    return "DEGENERATE" if len(set(texts)) == 1 else "VARIED"


def probe_failed(verdicts):
    """True when any model and arm is DEGENERATE or ERROR: the probe exits
    nonzero in that case."""
    return any(v in ("DEGENERATE", "ERROR") for v in verdicts.values())


def run_probe_sampling(models, out_dir=DEFAULT_PROBE_DIR, n=PROBE_N,
                       run_id=None):
    """Sampling-variance probe: n identical calls of PROBE_PROMPT per model
    per listed arm, through the exact collection request shaping. Validation,
    then credentials for every selected provider, then the first request, in
    that order (identical fail-closed behavior to collection). Full outputs
    append durably to one timestamped jsonl under out_dir; no collection row
    or path is touched. Returns {(model, arm): verdict}."""
    for m in models:
        validate_model_cfg(m)
    keys = read_keys(models)
    run_id = run_id or now_iso()

    os.makedirs(out_dir, exist_ok=True)
    fname = "probe_sampling_{}.jsonl".format(
        run_id.replace(":", "-").replace("+", "-"))
    report_path = os.path.join(out_dir, fname)

    verdicts = {}
    fh = open(report_path, "a", encoding="utf-8")
    try:
        print("\nSampling-variance probe, {} calls per model per arm, run {}"
              .format(n, run_id))
        for m in models:
            provider = m["provider"]
            for arm in m["arms"]:
                results = []
                for call_index in range(n):
                    try:
                        url, headers, body, temperature_sent = build_request(
                            m, arm, PROBE_PROMPT, keys[provider])
                        data = post_with_retries(
                            url, headers, body, PROVIDERS[provider]["retryable"])
                        parsed_resp = parse_response(provider, data)
                        results.append(("ok", parsed_resp["text"]))
                        row = {
                            "run_id": run_id, "phase": "probe_sampling",
                            "model": m["model"], "provider": provider,
                            "arm": arm, "call_index": call_index, "ok": True,
                            "text": parsed_resp["text"],
                            "text_len": len(parsed_resp["text"]),
                            "model_id_exact": (parsed_resp["model_id_exact"]
                                               or m["model"]),
                            "reasoning_detected": parsed_resp["reasoning_present"],
                            "temperature_sent": temperature_sent,
                            "ts": now_iso(),
                        }
                    except RuntimeError as exc:
                        results.append(("error", str(exc)))
                        row = {
                            "run_id": run_id, "phase": "probe_sampling",
                            "model": m["model"], "provider": provider,
                            "arm": arm, "call_index": call_index, "ok": False,
                            "error": str(exc), "ts": now_iso(),
                        }
                    write_row(fh, row)
                verdict = probe_verdict(results)
                verdicts[(m["model"], arm)] = verdict
                lengths = "/".join(str(len(text)) if status == "ok" else "ERR"
                                   for status, text in results)
                print("{:<26} arm {}  {:<10} lengths {}".format(
                    m["model"], arm, verdict, lengths))
    finally:
        fh.close()

    if any(v == "DEGENERATE" for v in verdicts.values()):
        print("DEGENERATE verdict(s) above: byte-identical outputs across "
              "identical calls. Before concluding greedy decoding, consider "
              "provider-side response caching of identical requests; the full "
              "outputs are in the report file.")
    if any(v == "ERROR" for v in verdicts.values()):
        print("ERROR verdict(s) above: a call failed after retries; reported "
              "without a sampling verdict, not folded into VARIED or "
              "DEGENERATE.")
    print("Probe outputs: {}".format(report_path))
    return verdicts


def main():
    ap = argparse.ArgumentParser(
        description="Convergence study collection: the 68-item bank as fresh "
                    "single-turn judgment across five providers in two arms. "
                    "--verify-reasoning runs the Arm A disable smoke test.")
    ap.add_argument("--config", default=DEFAULT_CONFIG,
                    help="roster json (default convergence/models.json)")
    ap.add_argument("--arm", choices=["A", "B"], default=None,
                    help="A: reasoning off (matched primary). B: reasoning on "
                         "(ecological).")
    ap.add_argument("--models", default=None,
                    help="comma-separated roster model ids, run in the order "
                         "given. Absent: the whole roster.")
    ap.add_argument("--out", default=DEFAULT_OUT,
                    help="rows jsonl, appended durably per row")
    ap.add_argument("--k", type=int, default=K_SAMPLES,
                    help="samples per item per model (default {} per the "
                         "pre-registration)".format(K_SAMPLES))
    ap.add_argument("--verify-reasoning", action="store_true",
                    help="run the Arm A reasoning-disable verification instead "
                         "of collection")
    ap.add_argument("--verify-n", type=int, default=VERIFY_N,
                    help="verification calls per Arm A model (default {})"
                         .format(VERIFY_N))
    ap.add_argument("--verify-out", default=DEFAULT_VERIFY_OUT,
                    help="verification rows jsonl")
    ap.add_argument("--probe-sampling", action="store_true",
                    help="run the sampling-variance probe instead of "
                         "collection: {} calls of the pinned probe prompt per "
                         "model per listed arm; DEGENERATE or ERROR anywhere "
                         "exits nonzero".format(PROBE_N))
    ap.add_argument("--probe-dir", default=DEFAULT_PROBE_DIR,
                    help="directory for timestamped probe output files")
    args = ap.parse_args()

    if args.probe_sampling and args.verify_reasoning:
        ap.error("--probe-sampling and --verify-reasoning are separate "
                 "modes; run one at a time")
    if not args.verify_reasoning and not args.probe_sampling \
            and args.arm is None:
        ap.error("--arm is required unless --verify-reasoning or "
                 "--probe-sampling is given")

    try:
        roster = load_roster(args.config)
        models = select_models(roster, args.models)
        if args.probe_sampling:
            verdicts = run_probe_sampling(models, out_dir=args.probe_dir)
            if probe_failed(verdicts):
                sys.exit(1)
        elif args.verify_reasoning:
            verify_reasoning(models, out_path=args.verify_out, n=args.verify_n)
        else:
            status = run_collection(models, args.arm, args.out, k=args.k)
            if collection_failed(status):
                sys.exit(1)
    except (ProviderConfigError, CredentialError) as exc:
        sys.stderr.write(str(exc) + "\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
