"""
Credential handling and runner test for convergence/collect.py. No network:
requests.post is replaced with a recording fake for every path; any real call
attempt fails the test.

Pins:
  1. For each of the five providers, a missing environment variable fails
     closed with CredentialError naming that exact variable, before any
     request is issued and before any output file is created.
  2. Credentials for every provider in the selection are read before the
     first call, so a missing key on model one fails the run even when model
     two's key is present.
  3. A placeholder model id (PIN_AT_LOCK...) is rejected at validation, before
     the credential read: ids are lock-day configuration, never code.
  4. With a canned Anthropic payload, rows carry the full extended schema
     (provider, model_id_exact, host, arm, reasoning_requested,
     reasoning_detected, temperature_sent, plus the unchanged baseline
     fields) and no key material appears anywhere in the output file; the key
     goes to the request headers only.
  5. Top-up convention: a rerun over a file with completed slots issues no
     new calls and appends no duplicate rows.
  6. CLI wiring via subprocess with all provider keys stripped: exit 1 with
     the missing variable named on stderr, and no output file created.

Run: python convergence/tests/test_credentials.py   (plain asserts, exit 1
on failure; also collectable by pytest).
"""
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
from convergence.providers import ProviderConfigError  # noqa: E402
from items.items import ITEMS  # noqa: E402

FIXTURE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "fixtures", "responses", "anthropic_no_thinking.json")
TESTKEY = "TESTKEY-fake-key-material-never-real"

ALL_ENV_VARS = [p["env"] for p in providers.PROVIDERS.values()]


def cfg_for(provider):
    cfg = {"model": provider + "-model-under-test", "provider": provider,
           "arms": ["B"] if provider == "google" else ["A", "B"],
           "host": None, "temperature_mode": "send"}
    if provider == "anthropic":
        cfg["temperature_mode"] = "omit"
        cfg["thinking_on"] = {"type": "enabled", "budget_tokens": 3000}
    return cfg


class RecordingPost:
    """Stands in for requests.post. Records every call; returns the canned
    payload if given, otherwise raises so a stray network attempt is loud."""
    def __init__(self, payload=None):
        self.calls = []
        self.payload = payload

    def __call__(self, url, headers=None, data=None, timeout=None):
        self.calls.append({"url": url, "headers": headers, "data": data})
        if self.payload is None:
            raise AssertionError("network call attempted")
        payload = self.payload

        class _Resp:
            status_code = 200

            def json(self):
                return payload
        return _Resp()


class EnvGuard:
    """Remove some env vars, set others, restore everything on exit."""
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


def run():
    fails = []

    def check(name, cond, got=None):
        if cond:
            print("  PASS: %s" % name)
        else:
            print("  FAIL: %s | got %r" % (name, got))
            fails.append(name)

    tmp = tempfile.mkdtemp(prefix="convergence_test_")
    orig_post = providers.requests.post
    try:
        print("=== missing key fails closed, per provider, no request, no file ===")
        for provider, p in sorted(providers.PROVIDERS.items()):
            out = os.path.join(tmp, "rows_%s.jsonl" % provider)
            arm = "B" if provider == "google" else "A"
            bomb = RecordingPost()
            providers.requests.post = bomb
            with EnvGuard(remove=[p["env"]]):
                try:
                    collect.run_collection([cfg_for(provider)], arm, out,
                                           k=1, items=[ITEMS[0]])
                    check("%s missing key raises CredentialError" % provider,
                          False, "no exception")
                except collect.CredentialError as exc:
                    check("%s missing key error names %s" % (provider, p["env"]),
                          p["env"] in str(exc), str(exc))
            check("%s issued no request" % provider, bomb.calls == [], len(bomb.calls))
            check("%s created no output file" % provider, not os.path.exists(out))

        print("=== all selected providers' keys are read before the first call ===")
        out = os.path.join(tmp, "rows_ordering.jsonl")
        bomb = RecordingPost()
        providers.requests.post = bomb
        with EnvGuard(remove=["ANTHROPIC_API_KEY"],
                      set_vars={"DEEPSEEK_API_KEY": TESTKEY}):
            try:
                collect.run_collection([cfg_for("anthropic"), cfg_for("deepseek")],
                                       "A", out, k=1, items=[ITEMS[0]])
                check("mixed selection with one missing key raises", False,
                      "no exception")
            except collect.CredentialError as exc:
                check("mixed selection fails on ANTHROPIC_API_KEY before any call",
                      "ANTHROPIC_API_KEY" in str(exc), str(exc))
        check("mixed selection issued no request at all", bomb.calls == [],
              len(bomb.calls))

        print("=== placeholder ids are rejected before the credential read ===")
        out = os.path.join(tmp, "rows_placeholder.jsonl")
        bomb = RecordingPost()
        providers.requests.post = bomb
        placeholder = dict(cfg_for("openai"), model="PIN_AT_LOCK-openai-small-tier")
        with EnvGuard(remove=["OPENAI_API_KEY"]):
            try:
                collect.run_collection([placeholder], "A", out, k=1,
                                       items=[ITEMS[0]])
                check("placeholder id raises ProviderConfigError", False,
                      "no exception")
            except ProviderConfigError as exc:
                check("placeholder id rejected naming it (validation, not "
                      "credentials)", "PIN_AT_LOCK-openai-small-tier" in str(exc),
                      str(exc))
        check("placeholder selection issued no request", bomb.calls == [],
              len(bomb.calls))

        print("=== rows carry the extended schema; key reaches headers only ===")
        with open(FIXTURE, encoding="utf-8") as f:
            payload = json.load(f)["payload"]
        out = os.path.join(tmp, "rows_schema.jsonl")
        fake = RecordingPost(payload=payload)
        providers.requests.post = fake
        with EnvGuard(set_vars={"ANTHROPIC_API_KEY": TESTKEY}):
            collect.run_collection([cfg_for("anthropic")], "A", out, k=2,
                                   items=[ITEMS[0]], run_id="test-run-id")
        check("two calls issued for k=2", len(fake.calls) == 2, len(fake.calls))
        check("key went to the request headers",
              fake.calls[0]["headers"].get("x-api-key") == TESTKEY)
        check("key not in the request body", TESTKEY not in fake.calls[0]["data"])
        with open(out, encoding="utf-8") as f:
            content = f.read()
        rows = [json.loads(line) for line in content.splitlines() if line]
        check("two rows on disk", len(rows) == 2, len(rows))
        check("no key material anywhere in the output file",
              TESTKEY not in content)
        r = rows[0]
        expected_fields = {
            "run_id": "test-run-id", "phase": "baseline",
            "model": "anthropic-model-under-test",
            "item_id": ITEMS[0]["id"], "item_cell": ITEMS[0]["cell"],
            "sample_index": 0, "parsed": "B", "raw_text": "ANSWER: B",
            "provider": "anthropic",
            "model_id_exact": "anthropic-model-under-test",
            "host": None, "arm": "A", "reasoning_requested": "off",
            "reasoning_detected": False, "temperature_sent": None,
        }
        for field, want in sorted(expected_fields.items()):
            check("row field %s" % field, r.get(field) == want, r.get(field))
        check("row has a timestamp", bool(r.get("ts")))
        check("sample indices are 0 and 1",
              sorted(x["sample_index"] for x in rows) == [0, 1])

        print("=== top-up: completed slots are never re-collected ===")
        fake2 = RecordingPost(payload=payload)
        providers.requests.post = fake2
        with EnvGuard(set_vars={"ANTHROPIC_API_KEY": TESTKEY}):
            collect.run_collection([cfg_for("anthropic")], "A", out, k=2,
                                   items=[ITEMS[0]])
        check("rerun over a complete file issues no calls",
              fake2.calls == [], len(fake2.calls))
        with open(out, encoding="utf-8") as f:
            check("rerun appends no rows",
                  len(f.read().splitlines()) == 2)

        print("=== CLI fails closed with the variable named on stderr ===")
        out = os.path.join(tmp, "rows_cli.jsonl")
        env = {k: v for k, v in os.environ.items() if k not in ALL_ENV_VARS}
        proc = subprocess.run(
            [sys.executable, os.path.join(REPO, "convergence", "collect.py"),
             "--arm", "A", "--models", "claude-haiku-4-5-20251001",
             "--out", out],
            capture_output=True, text=True, env=env, cwd=REPO, timeout=60)
        check("CLI exits 1", proc.returncode == 1, proc.returncode)
        check("CLI stderr names ANTHROPIC_API_KEY",
              "ANTHROPIC_API_KEY" in proc.stderr, proc.stderr[-300:])
        check("CLI created no output file", not os.path.exists(out))
    finally:
        providers.requests.post = orig_post
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    print("FAILURES: %d %s" % (len(fails), fails if fails else "- ALL PASS"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(run())


def test_credentials():  # pytest entry point
    assert run() == 0
