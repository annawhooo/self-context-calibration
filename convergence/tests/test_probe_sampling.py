"""
Sampling-variance probe test for convergence/collect.py --probe-sampling.
No network: requests.post is replaced with scripted fakes; a stray real call
fails the test.

Pins:
  1. The probe prompt is byte-pinned against a literal in this file, like
     the vendor_access stimulus pin.
  2. Probe request shaping per provider per arm is exactly the collection
     shaping: identical url and headers, identical body with only the prompt
     swapped, asserted against fixtures/expected_requests.json.
  3. Verdict logic: all three byte-identical gives DEGENERATE; two same one
     different gives VARIED; all different gives VARIED; any call failing
     after retries gives ERROR, reported without folding into either state.
  4. Per-arm iteration: an entry listing A and B is probed on both arms.
  5. Full probe outputs land in one timestamped jsonl under the probe dir
     (Windows-safe name, no colon), three rows per model per arm, full text
     retained, no collection output path touched.
  6. Credentials: a missing env var fails closed naming itself with zero
     requests and no report file (same behavior as collection).
  7. Exit codes: probe_failed is False for all-VARIED, True when any
     DEGENERATE or ERROR; the CLI exits 1 on the credential gate with the
     variable named, and exits 2 when --probe-sampling and
     --verify-reasoning are combined.

Run: python convergence/tests/test_probe_sampling.py   (plain asserts,
exit 1 on failure; also collectable by pytest).
"""
import os
import sys
import copy
import json
import glob
import shutil
import tempfile
import subprocess

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "harness"))

from convergence import collect, providers  # noqa: E402

FIXTURE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "fixtures", "expected_requests.json")

KEY = "TESTKEY-not-a-real-credential"

# Pinned probe prompt, byte for byte. Never derive this from the import; the
# literal is the tripwire.
PINNED_PROBE_PROMPT = ("In two or three sentences, describe an imaginary "
                       "small town, including its name and one notable "
                       "landmark.")

CFGS = {
    "anthropic": {"model": "anthropic-model-under-test", "provider": "anthropic",
                  "temperature_mode": "omit",
                  "thinking_on": {"type": "enabled", "budget_tokens": 3000}},
    "openai": {"model": "openai-model-under-test", "provider": "openai",
               "temperature_mode": "omit"},
    "deepseek": {"model": "deepseek-model-under-test", "provider": "deepseek",
                 "temperature_mode": "send"},
    "zai": {"model": "zai-model-under-test", "provider": "zai",
            "temperature_mode": "send"},
    "google": {"model": "google-model-under-test", "provider": "google",
               "temperature_mode": "send"},
}

CASES = ["anthropic_A", "anthropic_B", "openai_A", "openai_B",
         "deepseek_A", "deepseek_B", "zai_A", "zai_B", "google_B"]


def openai_payload(text):
    return {"model": "openai-model-under-test",
            "choices": [{"index": 0,
                         "message": {"role": "assistant", "content": text},
                         "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1,
                      "total_tokens": 2,
                      "completion_tokens_details": {"reasoning_tokens": 0}}}


class ScriptedPost:
    """Returns queued outcomes in order. An outcome is a payload dict (200)
    or ("http", status, text) for a failing status. Fails loudly when
    exhausted."""
    def __init__(self, outcomes):
        self.queue = list(outcomes)
        self.calls = 0

    def __call__(self, url, headers=None, data=None, timeout=None):
        self.calls += 1
        if not self.queue:
            raise AssertionError("more calls than scripted outcomes")
        item = self.queue.pop(0)

        class _Resp:
            pass
        r = _Resp()
        if isinstance(item, tuple) and item[0] == "http":
            r.status_code = item[1]
            r.text = item[2]
        else:
            r.status_code = 200
            r.json = lambda payload=item: payload
        return r


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


def probe_cfg(arms):
    return dict(CFGS["openai"], arms=list(arms), host=None)


def run():
    fails = []

    def check(name, cond, got=None):
        if cond:
            print("  PASS: %s" % name)
        else:
            print("  FAIL: %s | got %r" % (name, got))
            fails.append(name)

    tmp = tempfile.mkdtemp(prefix="convergence_probe_test_")
    orig_post = providers.requests.post
    default_out_existed = os.path.exists(collect.DEFAULT_OUT)
    try:
        print("=== probe prompt is byte-pinned ===")
        check("PROBE_PROMPT matches the pinned literal",
              collect.PROBE_PROMPT == PINNED_PROBE_PROMPT,
              collect.PROBE_PROMPT)
        check("utf-8 encodings identical as well",
              collect.PROBE_PROMPT.encode("utf-8")
              == PINNED_PROBE_PROMPT.encode("utf-8"))

        print("=== probe shaping equals collection shaping, prompt swapped ===")
        with open(FIXTURE_PATH, encoding="utf-8") as f:
            expected = json.load(f)
        for case in CASES:
            provider, arm = case.rsplit("_", 1)
            exp = copy.deepcopy(expected[case])
            if provider == "google":
                exp["body"]["contents"][0]["parts"][0]["text"] = \
                    collect.PROBE_PROMPT
            else:
                exp["body"]["messages"][0]["content"] = collect.PROBE_PROMPT
            url, headers, body, temperature_sent = providers.build_request(
                CFGS[provider], arm, collect.PROBE_PROMPT, KEY)
            check("%s url and headers unchanged" % case,
                  url == exp["url"] and headers == exp["headers"])
            check("%s body identical apart from the prompt" % case,
                  body == exp["body"], body)
            check("%s temperature handling unchanged" % case,
                  temperature_sent == exp["temperature_sent"], temperature_sent)

        print("=== verdict logic ===")
        scenarios = [
            ("all identical gives DEGENERATE",
             [openai_payload("Same town."), openai_payload("Same town."),
              openai_payload("Same town.")], "DEGENERATE"),
            ("two same one different gives VARIED",
             [openai_payload("Same town."), openai_payload("Same town."),
              openai_payload("Other town.")], "VARIED"),
            ("all different gives VARIED",
             [openai_payload("Town one."), openai_payload("Town two."),
              openai_payload("Town three.")], "VARIED"),
            ("a failed call gives ERROR, not folded",
             [openai_payload("Town one."), ("http", 400, "bad request"),
              openai_payload("Town three.")], "ERROR"),
        ]
        with EnvGuard(set_vars={"OPENAI_API_KEY": KEY}):
            for name, script, want in scenarios:
                probe_dir = os.path.join(tmp, "verdict_" + want + name[:8])
                providers.requests.post = ScriptedPost(script)
                verdicts = collect.run_probe_sampling(
                    [probe_cfg(["A"])], out_dir=probe_dir,
                    run_id="probe-test")
                check(name,
                      verdicts == {("openai-model-under-test", "A"): want},
                      verdicts)

            print("=== per-arm iteration ===")
            probe_dir = os.path.join(tmp, "arms")
            providers.requests.post = ScriptedPost(
                [openai_payload("t%d" % i) for i in range(6)])
            verdicts = collect.run_probe_sampling(
                [probe_cfg(["A", "B"])], out_dir=probe_dir,
                run_id="probe-test")
            check("both listed arms probed",
                  sorted(verdicts) == [("openai-model-under-test", "A"),
                                       ("openai-model-under-test", "B")],
                  sorted(verdicts))
            check("six calls for two arms", True)

            print("=== report file ===")
            files = glob.glob(os.path.join(probe_dir, "*"))
            check("exactly one report file per run", len(files) == 1, files)
            fname = os.path.basename(files[0])
            check("windows-safe filename, no colon", ":" not in fname, fname)
            check("filename carries the run timestamp id",
                  "probe-test" in fname, fname)
            with open(files[0], encoding="utf-8") as f:
                rows = [json.loads(line) for line in f if line.strip()]
            check("three rows per model per arm", len(rows) == 6, len(rows))
            check("rows retain full output text",
                  sorted(r["text"] for r in rows)
                  == sorted("t%d" % i for i in range(6)),
                  sorted(r.get("text") for r in rows))
            check("rows carry model, arm, call_index",
                  all(r["model"] == "openai-model-under-test"
                      and r["arm"] in ("A", "B")
                      and r["call_index"] in (0, 1, 2) for r in rows))
            check("no key material in the report file",
                  KEY not in open(files[0], encoding="utf-8").read())
            check("collection output path untouched",
                  os.path.exists(collect.DEFAULT_OUT) == default_out_existed)

        print("=== credentials fail closed ===")
        probe_dir = os.path.join(tmp, "creds")
        bomb = ScriptedPost([])
        providers.requests.post = bomb
        with EnvGuard(remove=["OPENAI_API_KEY"]):
            try:
                collect.run_probe_sampling([probe_cfg(["A"])],
                                           out_dir=probe_dir)
                check("missing key raises CredentialError", False,
                      "no exception")
            except collect.CredentialError as exc:
                check("missing key error names OPENAI_API_KEY",
                      "OPENAI_API_KEY" in str(exc), str(exc))
        check("no request issued", bomb.calls == 0, bomb.calls)
        check("no report file created", not os.path.exists(probe_dir))

        print("=== exit codes ===")
        check("probe_failed False for all VARIED",
              collect.probe_failed({("m", "A"): "VARIED",
                                    ("m", "B"): "VARIED"}) is False)
        check("probe_failed True on DEGENERATE",
              collect.probe_failed({("m", "A"): "VARIED",
                                    ("m", "B"): "DEGENERATE"}) is True)
        check("probe_failed True on ERROR",
              collect.probe_failed({("m", "A"): "ERROR"}) is True)

        env = {k: v for k, v in os.environ.items()
               if k not in [p["env"] for p in providers.PROVIDERS.values()]}
        script = os.path.join(REPO, "convergence", "collect.py")
        proc = subprocess.run(
            [sys.executable, script, "--probe-sampling",
             "--probe-dir", os.path.join(tmp, "cli")],
            capture_output=True, text=True, env=env, cwd=REPO, timeout=60)
        check("CLI probe exits 1 at the credential gate",
              proc.returncode == 1, proc.returncode)
        check("CLI probe stderr names ANTHROPIC_API_KEY",
              "ANTHROPIC_API_KEY" in proc.stderr, proc.stderr[-300:])
        proc = subprocess.run(
            [sys.executable, script, "--probe-sampling", "--verify-reasoning"],
            capture_output=True, text=True, env=env, cwd=REPO, timeout=60)
        check("CLI rejects --probe-sampling with --verify-reasoning (exit 2)",
              proc.returncode == 2, (proc.returncode, proc.stderr[-200:]))
    finally:
        providers.requests.post = orig_post
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    print("FAILURES: %d %s" % (len(fails), fails if fails else "- ALL PASS"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(run())


def test_probe_sampling():  # pytest entry point
    assert run() == 0
