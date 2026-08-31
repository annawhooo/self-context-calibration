"""
Pins for the counting semantics in
probe/scripts/step_change_watch.py, the mechanical check for the
rules pinned in STEP_CHANGE_DECISION_RULES_2026-08-31.md. Offline;
synthetic records only.

Pins:
  1. A modal tie is never HOME, whatever the TVD.
  2. A modal mismatch is never HOME, even distributionally at
     baseline.
  3. A modal-matching day at the band is HOME (<= semantics; the
     breach rule is strict >).
  4. Days before count_from never enter the table.
  5. A date gap in the observed sequence (missing day) does not
     reset the count; consecutiveness is over observed days.
  6. A HOME day resets the count to zero and terminates nothing.
  7. fired is True exactly on the day the count reaches the
     threshold, not after.
  8. null_context is a probability pair with p_home <= p_modal,
     and a fully concentrated baseline gives (1.0, 1.0).

Run: python probe/tests/test_step_change_watch.py   (plain asserts,
exit 1 on failure; also collectable by pytest).
"""
import os
import sys
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.normpath(os.path.join(
    HERE, os.pardir, "scripts", "step_change_watch.py"))
spec = importlib.util.spec_from_file_location("step_change_watch",
                                              SCRIPT)
watch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(watch)

REC = {"baseline_counts": {"A": 6, "C": 12, "D": 2},
       "band": {"p99": 0.40}}


def test_home_definition():
    # tie for modal is not home (pin 1)
    assert not watch.is_home({"A": 5, "C": 5}, REC)
    # modal mismatch is not home even near baseline shape (pin 2)
    assert not watch.is_home({"A": 7, "C": 3}, REC)
    # modal match at the band is home under <= (pin 3)
    assert watch.is_home({"C": 10}, REC)
    # and the plain at-baseline day is home
    assert watch.is_home({"A": 3, "C": 6, "D": 1}, REC)


def test_counting():
    away = {"A": 7, "C": 3}
    tie = {"A": 5, "C": 5}
    home = {"A": 3, "C": 6, "D": 1}
    days = [
        ("2026-08-31", away),   # before count_from (pin 4)
        ("2026-09-01", away),
        ("2026-09-02", home),   # reset (pin 6)
        ("2026-09-03", away),
        ("2026-09-05", away),   # 09-04 missing: no reset (pin 5)
        ("2026-09-06", tie),    # ties count as away (pin 1)
        ("2026-09-07", away),
    ]
    table = watch.evaluate(days, REC, 3, "2026-09-01")
    assert [r[0] for r in table] == [
        "2026-09-01", "2026-09-02", "2026-09-03",
        "2026-09-05", "2026-09-06", "2026-09-07"]
    assert [r[5] for r in table] == [1, 0, 1, 2, 3, 4]
    # fired exactly at the threshold, never again (pin 7)
    assert [r[6] for r in table] == [
        False, False, False, False, True, False]


def test_null_context():
    p_modal, p_home = watch.null_context(REC)
    assert 0.0 < p_home <= p_modal < 1.0
    concentrated = {"baseline_counts": {"D": 20},
                    "band": {"p99": 0.45}}
    p_modal, p_home = watch.null_context(concentrated)
    assert abs(p_modal - 1.0) < 1e-12
    assert abs(p_home - 1.0) < 1e-12


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("ok   %s" % name)
            except AssertionError as exc:
                failures += 1
                print("FAIL %s: %s" % (name, exc))
    sys.exit(1 if failures else 0)
