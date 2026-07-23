"""
Verification-mode test for convergence/collect.py verify_reasoning. No
network: requests.post is replaced with a scripted fake.

The pre-registration makes reasoning-off a void condition requiring positive
verification, so the verdict aggregation is load-bearing. Pins:
  1. All-off responses give verified_off.
  2. Any response with reasoning content gives reasoning_present (the void),
     even when other responses are clean or undetectable.
  3. No reasoning content but any undetectable response gives undetectable,
     never verified_off: an undetectable state cannot satisfy a void
     condition that requires positive verification.
  4. Only Arm A models are verified; a google-style B-only entry is not
     called; a selection with no Arm A model is an error.
  5. Verification rows land durably with phase verify_reasoning, n rows per
     model.

Run: python convergence/tests/test_verify_reasoning.py   (plain asserts,
exit 1 on failure; also collectable by pytest).
"""
import os
import sys
import json
import shutil
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "harness"))

from convergence import collect, providers  # noqa: E402
from convergence.providers import ProviderConfigError  # noqa: E402
from items.items import ITEMS  # noqa: E402

FIXDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "fixtures", "responses")


def payload(name):
    with open(os.path.join(FIXDIR, name), encoding="utf-8") as f:
        return json.load(f)["payload"]


def cfg(provider, arms=("A", "B")):
    c = {"model": provider + "-model-under-test", "provider": provider,
         "arms": list(arms), "host": None, "temperature_mode": "send"}
    if provider == "anthropic":
        c["temperature_mode"] = "omit"
        c["thinking_on"] = {"type": "enabled", "budget_tokens": 3000}
    return c


class ScriptedPost:
    """Returns queued payloads in order; fails loudly when exhausted."""
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


def run():
    fails = []

    def check(name, cond, got=None):
        if cond:
            print("  PASS: %s" % name)
        else:
            print("  FAIL: %s | got %r" % (name, got))
            fails.append(name)

    tmp = tempfile.mkdtemp(prefix="convergence_verify_test_")
    orig_post = providers.requests.post
    os.environ.setdefault("OPENAI_API_KEY", "TESTKEY-fake")
    try:
        off = payload("openai_off.json")
        on = payload("openai_reasoning.json")
        und = payload("openai_undetectable.json")

        cases = [
            ("all off gives verified_off", [off, off, off], "verified_off"),
            ("any reasoning gives reasoning_present", [off, on, und],
             "reasoning_present"),
            ("no reasoning but undetectable gives undetectable, not success",
             [off, und, off], "undetectable"),
        ]
        print("=== verdict aggregation ===")
        for name, script, want in cases:
            out = os.path.join(tmp, "verify.jsonl")
            if os.path.exists(out):
                os.remove(out)
            providers.requests.post = ScriptedPost(script)
            verdicts = collect.verify_reasoning(
                [cfg("openai")], out_path=out, n=3, items=[ITEMS[0]],
                run_id="verify-test")
            check(name, verdicts == {"openai-model-under-test": want}, verdicts)

        print("=== rows land durably with phase verify_reasoning ===")
        with open(out, encoding="utf-8") as f:
            rows = [json.loads(line) for line in f if line.strip()]
        check("3 rows for n=3", len(rows) == 3, len(rows))
        check("all rows carry phase verify_reasoning",
              all(r["phase"] == "verify_reasoning" for r in rows),
              [r["phase"] for r in rows])
        check("all rows are Arm A reasoning off",
              all(r["arm"] == "A" and r["reasoning_requested"] == "off"
                  for r in rows))

        print("=== only Arm A models are verified ===")
        out = os.path.join(tmp, "verify_b_only.jsonl")
        providers.requests.post = ScriptedPost([off, off, off])
        verdicts = collect.verify_reasoning(
            [cfg("openai"), cfg("google", arms=("B",))],
            out_path=out, n=3, items=[ITEMS[0]], run_id="verify-test")
        check("google B-only entry is not verified and not called",
              sorted(verdicts) == ["openai-model-under-test"], verdicts)
        try:
            collect.verify_reasoning([cfg("google", arms=("B",))],
                                     out_path=out, n=3, items=[ITEMS[0]])
            check("no Arm A model raises", False, "no exception")
        except ProviderConfigError:
            check("no Arm A model raises ProviderConfigError", True)
    finally:
        providers.requests.post = orig_post
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    print("FAILURES: %d %s" % (len(fails), fails if fails else "- ALL PASS"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(run())


def test_verify_reasoning():  # pytest entry point
    assert run() == 0
