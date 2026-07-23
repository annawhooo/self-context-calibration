"""
Adapter request-shaping test for convergence/providers.py, against the
recorded fixture in fixtures/expected_requests.json. No network anywhere.

Pins, for each provider and each arm:
  1. build_request produces exactly the fixture's url, headers, and body:
     the pinned reasoning setting (anthropic: thinking omitted on A, passed on
     B; openai: reasoning_effort none on A, omitted on B; deepseek: the V4
     thinking toggle; zai: enable_thinking, never thinking {type disabled});
     and the pinned temperature handling (1.0 sent for deepseek/zai/google,
     omitted for anthropic/openai), with temperature_sent reported to match.
  2. The zai body never carries a "thinking" key on either arm (that form is
     reported to be silently ignored, which would corrupt Arm A).
  3. The API key appears only in headers, never in the serialized body.
  4. google on Arm A raises ProviderConfigError (reasoning cannot be
     disabled; Arm B only), and an unknown provider or arm raises too.

Run: python convergence/tests/test_request_shaping.py   (plain asserts,
exit 1 on failure; also collectable by pytest).
"""
import os
import sys
import json

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "harness"))

from convergence.providers import build_request, ProviderConfigError  # noqa: E402

FIXTURE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "fixtures", "expected_requests.json")

KEY = "TESTKEY-not-a-real-credential"
PROMPT = "FIXTURE PROMPT: which option is highest risk?"

# Model configs under test: one per provider, ids fake by design (real ids are
# lock-day configuration in convergence/models.json, never code).
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


def run():
    fails = []

    def check(name, cond, got=None):
        if cond:
            print("  PASS: %s" % name)
        else:
            print("  FAIL: %s | got %r" % (name, got))
            fails.append(name)

    with open(FIXTURE_PATH, encoding="utf-8") as f:
        expected = json.load(f)

    print("=== request bodies match the recorded fixture ===")
    for case in CASES:
        provider, arm = case.rsplit("_", 1)
        exp = expected[case]
        url, headers, body, temperature_sent = build_request(
            CFGS[provider], arm, PROMPT, KEY)
        check("%s url" % case, url == exp["url"], url)
        check("%s headers" % case, headers == exp["headers"], headers)
        check("%s body" % case, body == exp["body"], body)
        check("%s temperature_sent" % case,
              temperature_sent == exp["temperature_sent"], temperature_sent)

    print("=== zai never sends the ignored thinking form ===")
    for arm in ("A", "B"):
        _u, _h, body, _t = build_request(CFGS["zai"], arm, PROMPT, KEY)
        check("zai arm %s body has no 'thinking' key" % arm,
              "thinking" not in body, sorted(body))

    print("=== key stays out of every body ===")
    for case in CASES:
        provider, arm = case.rsplit("_", 1)
        _u, _h, body, _t = build_request(CFGS[provider], arm, PROMPT, KEY)
        check("%s serialized body carries no key material" % case,
              KEY not in json.dumps(body))

    print("=== rejections ===")
    try:
        build_request(CFGS["google"], "A", PROMPT, KEY)
        check("google arm A raises ProviderConfigError", False, "no exception")
    except ProviderConfigError as exc:
        check("google arm A raises ProviderConfigError naming the rule",
              "Arm B" in str(exc), str(exc))
    try:
        build_request({"model": "x", "provider": "not-a-provider",
                       "temperature_mode": "omit"}, "A", PROMPT, KEY)
        check("unknown provider raises ProviderConfigError", False, "no exception")
    except ProviderConfigError:
        check("unknown provider raises ProviderConfigError", True)
    try:
        build_request(CFGS["zai"], "C", PROMPT, KEY)
        check("unknown arm raises ProviderConfigError", False, "no exception")
    except ProviderConfigError:
        check("unknown arm raises ProviderConfigError", True)
    try:
        build_request({"model": "anthropic-model-under-test",
                       "provider": "anthropic", "temperature_mode": "omit"},
                      "B", PROMPT, KEY)
        check("anthropic arm B without thinking_on raises", False, "no exception")
    except ProviderConfigError as exc:
        check("anthropic arm B without thinking_on raises naming the field",
              "thinking_on" in str(exc), str(exc))

    print()
    print("FAILURES: %d %s" % (len(fails), fails if fails else "- ALL PASS"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(run())


def test_request_shaping():  # pytest entry point
    assert run() == 0
