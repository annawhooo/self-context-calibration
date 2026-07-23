"""
Adapter response-parsing test for convergence/providers.py, against the
recorded example payloads in fixtures/responses/*.json. No network anywhere.

Pins, per fixture: parse_response extracts the answer text, the reasoning
presence signal, and the exact model id the provider reports. The three
reasoning_present values are load-bearing:
  true   reasoning content appeared (thinking block, reasoning tokens above
         zero, reasoning_content, or thoughts token count),
  false  a positive off signal (no thinking block, reasoning_tokens 0, no or
         empty reasoning_content, usageMetadata without a thoughts count),
  null   the response exposes no reasoning-presence surface. Reported as
         undetectable, never as success, because the pre-registration's void
         condition requires positive verification.

Also pins that the extracted text parses through the imported
parse_baseline_answer (the study's parse rule) to the expected option.

Run: python convergence/tests/test_response_parsing.py   (plain asserts,
exit 1 on failure; also collectable by pytest).
"""
import os
import sys
import json
import glob

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "harness"))

from convergence.providers import parse_response  # noqa: E402
from confab_harness_faithful import parse_baseline_answer  # noqa: E402

FIXTURE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "fixtures", "responses")


def run():
    fails = []

    def check(name, cond, got=None):
        if cond:
            print("  PASS: %s" % name)
        else:
            print("  FAIL: %s | got %r" % (name, got))
            fails.append(name)

    paths = sorted(glob.glob(os.path.join(FIXTURE_DIR, "*.json")))
    check("fixture set is present (13 recorded payloads)", len(paths) == 13,
          len(paths))

    print("=== recorded payloads parse to the expected fields ===")
    for path in paths:
        name = os.path.splitext(os.path.basename(path))[0]
        with open(path, encoding="utf-8") as f:
            fx = json.load(f)
        got = parse_response(fx["provider"], fx["payload"])
        exp = fx["expect"]
        check("%s text" % name, got["text"] == exp["text"], got["text"])
        check("%s reasoning_present" % name,
              got["reasoning_present"] == exp["reasoning_present"]
              and isinstance(got["reasoning_present"], (bool, type(None))),
              got["reasoning_present"])
        check("%s model_id_exact" % name,
              got["model_id_exact"] == exp["model_id_exact"],
              got["model_id_exact"])
        expected_option = exp["text"].split("ANSWER: ")[-1]
        check("%s text parses via imported parse rule" % name,
              parse_baseline_answer(got["text"]) == expected_option,
              parse_baseline_answer(got["text"]))

    print("=== structurally empty responses degrade to empty text, not a crash ===")
    for provider, payload in [("anthropic", {"content": []}),
                              ("openai", {"choices": []}),
                              ("google", {"candidates": []})]:
        got = parse_response(provider, payload)
        check("%s empty payload gives empty text" % provider,
              got["text"] == "", got["text"])
        check("%s empty payload parses to None (unparsed sample)" % provider,
              parse_baseline_answer(got["text"]) is None)

    print()
    print("FAILURES: %d %s" % (len(fails), fails if fails else "- ALL PASS"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(run())


def test_response_parsing():  # pytest entry point
    assert run() == 0
