"""
Echo-change halt test for convergence/collect.py run_collection. No
network: requests.post is replaced with scripted fakes.

The pre-registration's preview-id tripwire: the model id echoed per response
is the aliasing signal; if it changes mid-collection, collection halts for
that model and completed rows form their own cell. Pins:

  1. Reference from prior rows (fixtures/prior_rows/single_echo.jsonl): a
     resumed run whose echoes match the prior file's single distinct
     model_id_exact runs clean.
  2. Resume-spanning halt: same prior file, a new response echoing a
     different id writes that row durably as evidence, then stops that
     model.
  3. Refuse-to-start on a pre-split prior file
     (fixtures/prior_rows/pre_split.jsonl): both ids named, zero calls for
     that model, remaining models still collect.
  4. Mid-run halt: reference set by the first echoed response of the run;
     on divergence the divergent row is written, no further calls for that
     model are issued, remaining models continue, and the halt report
     carries the row counts on each side.
  5. Missing echo: never halts, never sets or updates the reference, is
     counted and reported per model.
  6. Scope: --verify-reasoning and --probe-sampling are not subject to the
     check; differing echoes there run to completion.
  7. Exit codes: collection_failed is False for a clean run, True for
     halted and for refuse-to-start; the CLI exits 1 on a pre-split prior
     file with both ids on stderr, before any call.

Run: python convergence/tests/test_echo_halt.py   (plain asserts, exit 1
on failure; also collectable by pytest).
"""
import io
import os
import sys
import json
import shutil
import tempfile
import subprocess

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "harness"))

from convergence import collect, providers  # noqa: E402
from items.items import ITEMS  # noqa: E402

FIXDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "fixtures", "prior_rows")
KEY = "TESTKEY-fake-key-material-never-real"

REF_ID = "openai-model-under-test-0601"      # reference id in both fixtures
SPLIT_ID = "openai-model-under-test-0715"    # second id in pre_split.jsonl


def cfg(provider):
    c = {"model": provider + "-model-under-test", "provider": provider,
         "arms": ["A", "B"], "host": None, "temperature_mode": "send"}
    if provider == "anthropic":
        c["temperature_mode"] = "omit"
        c["thinking_on"] = {"type": "enabled", "budget_tokens": 3000}
    return c


def pay(text, model_id=None):
    """openai_compat chat-completion payload; model_id None omits the echo."""
    p = {"choices": [{"index": 0,
                      "message": {"role": "assistant", "content": text},
                      "finish_reason": "stop"}],
         "usage": {"prompt_tokens": 1, "completion_tokens": 1,
                   "total_tokens": 2,
                   "completion_tokens_details": {"reasoning_tokens": 0}}}
    if model_id is not None:
        p["model"] = model_id
    return p


class ScriptedPost:
    def __init__(self, payloads):
        self.queue = list(payloads)
        self.calls = 0

    def __call__(self, url, headers=None, data=None, timeout=None):
        self.calls += 1
        if not self.queue:
            raise AssertionError("more calls than scripted payloads")
        item = self.queue.pop(0)

        class _Resp:
            status_code = 200

            def json(self):
                return item
        return _Resp()


class EnvGuard:
    def __init__(self, remove=(), set_vars=None):
        self.remove = remove
        self.set_vars = set_vars or {}
        self.saved = {}

    def __enter__(self):
        for k in list(self.remove) + list(self.set_vars):
            self.saved[k] = os.environ.pop(k, None)
        for k, v in self.set_vars.items():
            os.environ[k] = v
        return self

    def __exit__(self, *exc):
        for k, v in self.saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def rows_in(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def run():
    fails = []

    def check(name, cond, got=None):
        if cond:
            print("  PASS: %s" % name)
        else:
            print("  FAIL: %s | got %r" % (name, got))
            fails.append(name)

    tmp = tempfile.mkdtemp(prefix="convergence_echo_test_")
    orig_post = providers.requests.post
    keys_env = {"OPENAI_API_KEY": KEY, "DEEPSEEK_API_KEY": KEY}
    try:
        with EnvGuard(set_vars=keys_env):
            print("=== reference from prior rows: matching echoes run clean ===")
            out = os.path.join(tmp, "clean.jsonl")
            shutil.copy(os.path.join(FIXDIR, "single_echo.jsonl"), out)
            providers.requests.post = ScriptedPost(
                [pay("ANSWER: A", REF_ID), pay("ANSWER: B", REF_ID)])
            status = collect.run_collection([cfg("openai")], "A", out, k=2,
                                            items=[ITEMS[0]],
                                            run_id="echo-test")
            check("clean run: nothing refused or halted",
                  status["refused"] == [] and status["halted"] == [], status)
            check("clean run: no missing echoes", status["missing_echo"] == {},
                  status["missing_echo"])
            check("clean run: 2 prior + 2 new rows on disk",
                  len(rows_in(out)) == 4, len(rows_in(out)))
            check("collection_failed False for a clean run",
                  collect.collection_failed(status) is False)

            print("=== resume-spanning halt: prior reference, divergent new echo ===")
            out = os.path.join(tmp, "resume_halt.jsonl")
            shutil.copy(os.path.join(FIXDIR, "single_echo.jsonl"), out)
            post = ScriptedPost([pay("ANSWER: A", SPLIT_ID)])
            providers.requests.post = post
            err = io.StringIO()
            saved_err = sys.stderr
            sys.stderr = err
            try:
                status = collect.run_collection([cfg("openai")], "A", out, k=2,
                                                items=[ITEMS[0]],
                                                run_id="echo-test")
            finally:
                sys.stderr = saved_err
            check("halt on first divergent response, no further calls",
                  post.calls == 1, post.calls)
            check("divergent row written durably as evidence",
                  len(rows_in(out)) == 3 and
                  rows_in(out)[-1]["model_id_exact"] == SPLIT_ID,
                  rows_in(out)[-1].get("model_id_exact"))
            check("halt status names model, reference, divergent, counts",
                  status["halted"] == [{"model": "openai-model-under-test",
                                        "reference": REF_ID,
                                        "divergent": SPLIT_ID,
                                        "reference_rows": 2,
                                        "divergent_rows": 1}],
                  status["halted"])
            check("halt report printed naming both ids",
                  REF_ID in err.getvalue() and SPLIT_ID in err.getvalue(),
                  err.getvalue()[-300:])
            check("collection_failed True for a halted run",
                  collect.collection_failed(status) is True)

            print("=== refuse-to-start on a pre-split prior file ===")
            out = os.path.join(tmp, "presplit.jsonl")
            shutil.copy(os.path.join(FIXDIR, "pre_split.jsonl"), out)
            post = ScriptedPost([pay("ANSWER: A", "deepseek-echo-1"),
                                 pay("ANSWER: B", "deepseek-echo-1")])
            providers.requests.post = post
            err = io.StringIO()
            sys.stderr = err
            try:
                status = collect.run_collection(
                    [cfg("openai"), cfg("deepseek")], "A", out, k=2,
                    items=[ITEMS[0]], run_id="echo-test")
            finally:
                sys.stderr = saved_err
            check("pre-split model refused naming both ids",
                  status["refused"] == [{"model": "openai-model-under-test",
                                         "ids": sorted([REF_ID, SPLIT_ID])}],
                  status["refused"])
            check("refusal printed naming both ids",
                  REF_ID in err.getvalue() and SPLIT_ID in err.getvalue())
            check("no call issued for the refused model; others collected",
                  post.calls == 2, post.calls)
            new_rows = [r for r in rows_in(out) if r["run_id"] == "echo-test"]
            check("remaining model's rows landed",
                  len(new_rows) == 2 and
                  all(r["model"] == "deepseek-model-under-test"
                      for r in new_rows), new_rows)
            check("collection_failed True for refuse-to-start",
                  collect.collection_failed(status) is True)

            print("=== mid-run halt: first echo sets reference, others continue ===")
            out = os.path.join(tmp, "midrun.jsonl")
            post = ScriptedPost([
                pay("ANSWER: A", "openai-echo-X"),
                pay("ANSWER: B", "openai-echo-X"),
                pay("ANSWER: C", "openai-echo-Y"),
                pay("ANSWER: A", "deepseek-echo-Z"),
                pay("ANSWER: B", "deepseek-echo-Z"),
                pay("ANSWER: C", "deepseek-echo-Z"),
                pay("ANSWER: D", "deepseek-echo-Z"),
            ])
            providers.requests.post = post
            err = io.StringIO()
            sys.stderr = err
            try:
                status = collect.run_collection(
                    [cfg("openai"), cfg("deepseek")], "A", out, k=2,
                    items=[ITEMS[0], ITEMS[1]], run_id="echo-test")
            finally:
                sys.stderr = saved_err
            check("openai halted after the divergent third call; deepseek "
                  "ran all four", post.calls == 7 and post.queue == [],
                  (post.calls, len(post.queue)))
            check("mid-run halt status carries 2 vs 1 row counts",
                  status["halted"] == [{"model": "openai-model-under-test",
                                        "reference": "openai-echo-X",
                                        "divergent": "openai-echo-Y",
                                        "reference_rows": 2,
                                        "divergent_rows": 1}],
                  status["halted"])
            by_model = {}
            for r in rows_in(out):
                by_model[r["model"]] = by_model.get(r["model"], 0) + 1
            check("3 openai rows (divergent included) and 4 deepseek rows",
                  by_model == {"openai-model-under-test": 3,
                               "deepseek-model-under-test": 4}, by_model)

            print("=== missing echo: counted, never halts, never sets reference ===")
            out = os.path.join(tmp, "missing.jsonl")
            providers.requests.post = ScriptedPost([
                pay("ANSWER: A"), pay("ANSWER: B", "openai-echo-X"),
                pay("ANSWER: C"), pay("ANSWER: D", "openai-echo-X")])
            status = collect.run_collection([cfg("openai")], "A", out, k=4,
                                            items=[ITEMS[0]],
                                            run_id="echo-test")
            check("missing echoes counted per model",
                  status["missing_echo"] == {"openai-model-under-test": 2},
                  status["missing_echo"])
            check("missing echoes did not halt",
                  status["halted"] == [] and
                  collect.collection_failed(status) is False, status)
            out = os.path.join(tmp, "missing_ref.jsonl")
            post = ScriptedPost([pay("ANSWER: A"),
                                 pay("ANSWER: B", "openai-echo-X"),
                                 pay("ANSWER: C", "openai-echo-Y")])
            providers.requests.post = post
            err = io.StringIO()
            sys.stderr = err
            try:
                status = collect.run_collection([cfg("openai")], "A", out, k=3,
                                                items=[ITEMS[0]],
                                                run_id="echo-test")
            finally:
                sys.stderr = saved_err
            check("missing first response never set the reference: halt is "
                  "X versus Y, not fallback versus X",
                  status["halted"] == [{"model": "openai-model-under-test",
                                        "reference": "openai-echo-X",
                                        "divergent": "openai-echo-Y",
                                        "reference_rows": 1,
                                        "divergent_rows": 1}],
                  status["halted"])

            print("=== scope: verify and probe modes are not subject to the check ===")
            providers.requests.post = ScriptedPost([
                pay("ANSWER: A", "echo-1"), pay("ANSWER: B", "echo-2"),
                pay("ANSWER: C", "echo-3")])
            verdicts = collect.verify_reasoning(
                [cfg("openai")], out_path=os.path.join(tmp, "verify.jsonl"),
                n=3, items=[ITEMS[0]], run_id="echo-test")
            check("verify_reasoning completes across differing echoes",
                  verdicts == {"openai-model-under-test": "verified_off"},
                  verdicts)
            providers.requests.post = ScriptedPost([
                pay("town one", "echo-1"), pay("town two", "echo-2"),
                pay("town three", "echo-3")])
            verdicts = collect.run_probe_sampling(
                [dict(cfg("openai"), arms=["A"])],
                out_dir=os.path.join(tmp, "probe"), run_id="echo-test")
            check("probe completes across differing echoes",
                  verdicts == {("openai-model-under-test", "A"): "VARIED"},
                  verdicts)

        print("=== CLI: pre-split prior file exits 1 before any call ===")
        cli_out = os.path.join(tmp, "cli_presplit.jsonl")
        with open(cli_out, "w", encoding="utf-8") as f:
            for idx, echo in enumerate(["claude-haiku-4-5-20251001",
                                        "claude-haiku-4-5-20251115"]):
                f.write(json.dumps({
                    "run_id": "prior", "phase": "baseline",
                    "model": "claude-haiku-4-5-20251001",
                    "item_id": "deploy_path", "item_cell": "derivable",
                    "sample_index": idx, "parsed": "D",
                    "raw_text": "ANSWER: D", "ts": "2026-07-20T10:00:01+00:00",
                    "provider": "anthropic", "model_id_exact": echo,
                    "host": None, "arm": "A", "reasoning_requested": "off",
                    "reasoning_detected": False,
                    "temperature_sent": None}) + "\n")
        env = {k: v for k, v in os.environ.items()
               if k not in [p["env"] for p in providers.PROVIDERS.values()]}
        env["ANTHROPIC_API_KEY"] = KEY
        proc = subprocess.run(
            [sys.executable, os.path.join(REPO, "convergence", "collect.py"),
             "--arm", "A", "--models", "claude-haiku-4-5-20251001",
             "--out", cli_out],
            capture_output=True, text=True, env=env, cwd=REPO, timeout=60)
        check("CLI exits 1 on refuse-to-start", proc.returncode == 1,
              proc.returncode)
        check("CLI stderr names both echo ids",
              "claude-haiku-4-5-20251001" in proc.stderr
              and "claude-haiku-4-5-20251115" in proc.stderr,
              proc.stderr[-400:])
        check("CLI wrote no new rows", len(rows_in(cli_out)) == 2,
              len(rows_in(cli_out)))
    finally:
        providers.requests.post = orig_post
        sys.stderr = sys.__stderr__
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    print("FAILURES: %d %s" % (len(fails), fails if fails else "- ALL PASS"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(run())


def test_echo_halt():  # pytest entry point
    assert run() == 0
