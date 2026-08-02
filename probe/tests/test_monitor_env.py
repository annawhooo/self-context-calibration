"""
check-env and roster tests for the monitor, run against the shipped
probe/monitor/roster.json. No network anywhere: check-env issues zero
requests by design, and the roster-refusal path fails before the
credential read.

Pins:
  1. The shipped roster is the handoff's five models, one pinned arm each,
     and validates under the monitor's rules (gemini-3.1-pro-preview is
     absent; gemini-3.6-flash carries the B-only google pin).
  2. check-env prints SET or MISSING per required variable (one line per
     distinct provider variable), never a value, and exits nonzero on any
     missing variable, zero when all are set.
  3. An unknown model id is refused, naming the id and the roster ids,
     before any credential is read and with zero requests issued; exit 2
     through the CLI.
  4. baseline requires exactly one of --model / --all.

Run: python probe/tests/test_monitor_env.py   (plain asserts, exit 1 on
failure; also collectable by pytest).
"""
import io
import os
import sys
import contextlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from monitor_testkit import (  # noqa: E402
    TESTKEY, EnvGuard, ScriptedPost, monitor, providers,
)

ROSTER_ENVS = ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GOOGLE_API_KEY",
               "DEEPSEEK_API_KEY"]
ROSTER_IDS = ["claude-haiku-4-5-20251001", "claude-sonnet-4-6",
              "gpt-5.6-terra", "gemini-3.6-flash", "deepseek-v4-flash"]


def run():
    fails = []

    def check(name, cond, got=None):
        if cond:
            print("  PASS: %s" % name)
        else:
            print("  FAIL: %s | got %r" % (name, got))
            fails.append(name)

    print("=== the shipped roster is the handoff roster ===")
    roster = monitor.load_roster(monitor.ROSTER_PATH)
    check("five models, the handoff ids, in order",
          [m["model"] for m in roster] == ROSTER_IDS,
          [m["model"] for m in roster])
    for m in roster:
        try:
            monitor.validate_monitor_model(m)
            check("roster entry %s validates" % m["model"], True)
        except Exception as exc:  # noqa: BLE001 - test reports any failure
            check("roster entry %s validates" % m["model"], False, str(exc))
    arms = {m["model"]: m["arms"] for m in roster}
    check("gemini-3.6-flash carries the google B-only pin",
          arms["gemini-3.6-flash"] == ["B"], arms["gemini-3.6-flash"])
    check("all non-google entries run Arm A",
          all(v == ["A"] for k, v in arms.items()
              if k != "gemini-3.6-flash"), arms)
    check("gemini-3.1-pro-preview excluded (680-call bank vs 250/day cap)",
          "gemini-3.1-pro-preview" not in arms)

    print("=== check-env: SET/MISSING per key, no values, fail-closed ===")
    set_all = {env: TESTKEY for env in ROSTER_ENVS}
    out = io.StringIO()
    with EnvGuard(set_vars=set_all):
        with contextlib.redirect_stdout(out):
            code = monitor.run_check_env(roster)
    text = out.getvalue()
    check("all keys set -> exit 0", code == 0, code)
    check("one line per distinct provider variable",
          sorted(line.split()[0] for line in text.strip().splitlines())
          == sorted(ROSTER_ENVS), text)
    check("all report SET", text.count(" SET") == len(ROSTER_ENVS), text)
    check("values never printed", TESTKEY not in text)

    for env in ROSTER_ENVS:
        vars_minus_one = dict(set_all)
        del vars_minus_one[env]
        out = io.StringIO()
        with EnvGuard(remove=[env], set_vars=vars_minus_one):
            with contextlib.redirect_stdout(out):
                code = monitor.run_check_env(roster)
        text = out.getvalue()
        check("missing %s -> nonzero exit, named MISSING" % env,
              code != 0 and "%s MISSING" % env in text, (code, text))

    print("=== unknown model ids are refused, zero requests ===")
    bomb = ScriptedPost({})
    orig = providers.requests.post
    providers.requests.post = bomb
    err = io.StringIO()
    try:
        with EnvGuard(remove=ROSTER_ENVS):
            with contextlib.redirect_stderr(err):
                code = monitor.main(["baseline", "--model",
                                     "not-a-roster-model"])
    finally:
        providers.requests.post = orig
    text = err.getvalue()
    check("unknown id exits 2", code == 2, code)
    check("refusal names the unknown id", "not-a-roster-model" in text, text)
    check("refusal lists the roster ids", "gpt-5.6-terra" in text, text)
    check("zero requests issued", bomb.calls == [], len(bomb.calls))

    print("=== baseline requires exactly one of --model / --all ===")
    for argv in (["baseline"],
                 ["baseline", "--model", "gpt-5.6-terra", "--all"]):
        err = io.StringIO()
        try:
            with contextlib.redirect_stderr(err):
                monitor.main(argv)
            check("%r rejected" % (argv,), False, "no exit")
        except SystemExit as exc:
            check("%r rejected" % (argv,), exc.code == 2, exc.code)

    print()
    print("FAILURES: %d %s" % (len(fails), fails if fails else "- ALL PASS"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(run())


def test_monitor_env():  # pytest entry point
    assert run() == 0
