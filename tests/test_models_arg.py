"""
Test for the --models CLI argument on the faithful harness.

Pins, at parse level with no API calls anywhere:
  1. resolve_models(None) falls back to the MODELS constant unchanged.
  2. A valid comma-separated list resolves to exactly those model ids, in the
     order given (both orders tested).
  3. Every resolved id is a THINKING_CONFIG key.
  4. An unknown id raises ValueError naming it, before any network call.
  5. An empty --models value raises ValueError (fail closed).
  6. CLI wiring, via subprocess with ANTHROPIC_API_KEY stripped from the
     environment so no call can ever be made:
     - an unknown id exits 2 at argument validation (before the API key gate,
       therefore before any API call);
     - a valid list exits 1 at the API key gate (parsing accepted, run stopped
       with no network);
     - the absent flag also exits 1 at the API key gate (default path intact).

Run: python tests/test_models_arg.py   (plain asserts, exit 1 on failure;
also collectable by pytest).
"""
import os
import sys
import subprocess

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "harness"))

from confab_harness_faithful import (  # noqa: E402
    MODELS, THINKING_CONFIG, resolve_models,
)

HARNESS = os.path.join(REPO, "harness", "confab_harness_faithful.py")
SONNET = "claude-sonnet-4-6"
OPUS = "claude-opus-4-7"


def run_cli(extra_args):
    """Run the harness CLI with ANTHROPIC_API_KEY stripped, so the run can
    never reach the network. Returns (exit_code, stderr_text)."""
    env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
    proc = subprocess.run(
        [sys.executable, HARNESS] + extra_args,
        capture_output=True, text=True, env=env, cwd=REPO, timeout=60,
    )
    return proc.returncode, proc.stderr


def run():
    fails = []

    def check(name, cond, got=None):
        if cond:
            print("  PASS: %s" % name)
        else:
            print("  FAIL: %s | got %r" % (name, got))
            fails.append(name)

    print("=== resolve_models: fallback, order, validation ===")
    got = resolve_models(None)
    check("absent flag falls back to MODELS", got == list(MODELS), got)

    got = resolve_models(SONNET + "," + OPUS)
    check("valid list resolves in the order given", got == [SONNET, OPUS], got)

    got = resolve_models(OPUS + "," + SONNET)
    check("reversed list preserves its order", got == [OPUS, SONNET], got)

    check("every resolved id is a THINKING_CONFIG key",
          all(m in THINKING_CONFIG for m in resolve_models(SONNET + "," + OPUS)))

    try:
        resolve_models(SONNET + ",not-a-model")
        check("unknown id raises ValueError", False, "no exception")
    except ValueError as exc:
        check("unknown id raises ValueError naming it", "not-a-model" in str(exc),
              str(exc))

    try:
        resolve_models("")
        check("empty value raises ValueError", False, "no exception")
    except ValueError:
        check("empty value raises ValueError", True)

    print("=== CLI wiring, no API key in the environment ===")
    code, err = run_cli(["--models", "not-a-model"])
    check("unknown id exits 2 before the API key gate", code == 2, (code, err[-200:]))
    check("unknown id error names the bad id, not argparse rejection",
          "not-a-model" in err and "unrecognized arguments" not in err,
          err[-200:])

    code, err = run_cli(["--models", SONNET + "," + OPUS])
    check("valid list passes parsing and exits 1 at the API key gate",
          code == 1 and "ANTHROPIC_API_KEY" in err, (code, err[-200:]))

    code, err = run_cli([])
    check("absent flag exits 1 at the API key gate (default path intact)",
          code == 1 and "ANTHROPIC_API_KEY" in err, (code, err[-200:]))

    print()
    print("FAILURES: %d %s" % (len(fails), fails if fails else "- ALL PASS"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(run())


def test_models_arg():  # pytest entry point
    assert run() == 0
