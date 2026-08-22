"""
Pure-function pins for the scheduled push (probe/scripts/push_verdicts.py).
No git and no network anywhere in this file: the git orchestration is
exercised by hand per probe/monitor/README.md; what is pinned here is the
two decisions the script makes on its own.

Pins:
  1. parse_numstat: empty diff is (0, 0); an append-only diff reads back
     its counts; the binary marker "-" reads as (-1, -1), which callers
     treat as not append-only.
  2. summarize subject grammar: single date has no range; multi-date is
     "min to max"; verdict tally follows the fixed grammar order (CLEAN,
     TRANSIENT, EVENT, UNSTABLE, ECHO_CHANGE, ERROR), not count or
     alphabetical order, so subjects are comparable across days.
  3. Unparsable staged lines are counted and named in the subject, never
     silently dropped: the commit message must not claim less than was
     pushed.
  4. No parsable lines at all (counts-only refresh, or a hand-committed
     backlog) falls back to the fixed subject "Monitor record push".
  5. The body always marks the commit automated; the daily-counts
     sentence appears exactly when counts_refreshed is set.

Run: python probe/tests/test_push_verdicts.py   (plain asserts, exit 1 on
failure; also collectable by pytest).
"""
import os
import sys
import json
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.normpath(os.path.join(
    HERE, os.pardir, "scripts", "push_verdicts.py"))
spec = importlib.util.spec_from_file_location("push_verdicts", SCRIPT)
push_verdicts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(push_verdicts)

parse_numstat = push_verdicts.parse_numstat
summarize = push_verdicts.summarize


def vline(date, verdict):
    return json.dumps({"date": date, "verdict": verdict})


def test_parse_numstat():
    assert parse_numstat("") == (0, 0)
    assert parse_numstat("\n") == (0, 0)
    assert parse_numstat("10\t0\tprobe/monitor/verdicts.jsonl\n") == (10, 0)
    assert parse_numstat("3\t2\tprobe/monitor/verdicts.jsonl\n") == (3, 2)
    assert parse_numstat("-\t-\tsome.bin\n") == (-1, -1)


def test_summarize_single_day():
    msg = summarize([vline("2026-08-21", "CLEAN")] * 4
                    + [vline("2026-08-21", "EVENT")], False)
    subject, blank, body = msg.split("\n", 2)
    assert subject == "Verdicts 2026-08-21: 4 CLEAN, 1 EVENT"
    assert blank == ""
    assert "Automated push" in body
    assert "daily counts" not in body


def test_summarize_range_and_order():
    lines = [vline("2026-08-22", "ERROR"),
             vline("2026-08-21", "EVENT"),
             vline("2026-08-21", "EVENT"),
             vline("2026-08-22", "CLEAN"),
             vline("2026-08-21", "TRANSIENT")]
    msg = summarize(lines, True)
    subject = msg.splitlines()[0]
    # grammar order, not count order and not alphabetical
    assert subject == ("Verdicts 2026-08-21 to 2026-08-22: "
                       "1 CLEAN, 1 TRANSIENT, 2 EVENT, 1 ERROR")
    assert "daily counts refreshed" in msg.splitlines()[-1].lower()


def test_summarize_counts_unparsable():
    lines = [vline("2026-08-21", "CLEAN"), "not json at all",
             json.dumps({"date": "2026-08-21"})]  # missing verdict
    subject = summarize(lines, False).splitlines()[0]
    assert subject == "Verdicts 2026-08-21: 1 CLEAN, 2 unparsable"


def test_summarize_no_verdict_lines():
    msg = summarize([], True)
    assert msg.splitlines()[0] == "Monitor record push"
    assert "Automated push" in msg


def main():
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print("ok %s" % name)
    print("all push_verdicts pins hold")


if __name__ == "__main__":
    main()
