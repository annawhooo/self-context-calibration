"""
Pins for the counting semantics in probe/scripts/wait_rule_count.py,
the mechanical check for STEP_CHANGE_DECISION_RULE_2026-10-18.md.
Offline; synthetic records only.

Pins:
  1. A modal tie is never HOME, whatever the TVD.
  2. TVD exactly 0.40 is HOME (<= semantics, exact arithmetic).
  3. Days before count_from never enter the table.
  4. A single HOME day between AWAY days adds nothing and resets
     nothing.
  5. Two consecutive observed HOME days reset the count to zero; a
     date gap between them does not break consecutiveness.
  6. The THRESHOLD event falls exactly on the day the count reaches
     the threshold, and no later day is returned.
  7. The reference is the earliest superseded entry once the item
     carries one.
  8. earliest() adds the remaining count in calendar days.

Run: python probe/tests/test_wait_rule_count.py   (plain asserts,
exit 1 on failure; also collectable by pytest).
"""
import os
import sys
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.normpath(os.path.join(
    HERE, os.pardir, "scripts", "wait_rule_count.py"))
spec = importlib.util.spec_from_file_location("wait_rule_count", SCRIPT)
wrc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wrc)

REF = {"baseline_counts": {"A": 20}}
HOME = {"A": 9, "B": 1}
AWAY = {"A": 2, "B": 8}


def test_home_definition():
    # tie for modal is not home (pin 1)
    assert not wrc.is_home({"A": 5, "B": 5}, REF)
    # exactly 0.40 is home under exact <= (pin 2)
    assert wrc.is_home({"A": 6, "B": 4}, REF)
    assert not wrc.is_home({"A": 5, "B": 4, "C": 1}, REF)


def test_counting():
    days = [
        ("2026-10-16", AWAY),   # before count_from (pin 3)
        ("2026-10-17", AWAY),
        ("2026-10-18", HOME),   # single home: no change (pin 4)
        ("2026-10-19", AWAY),
        ("2026-10-20", HOME),
        ("2026-10-22", HOME),   # 10-21 missing: still consecutive,
                                # reset (pin 5)
        ("2026-10-23", AWAY),
    ]
    table = wrc.evaluate(days, REF, 18, "2026-10-17")
    assert [r[0] for r in table] == [
        "2026-10-17", "2026-10-18", "2026-10-19", "2026-10-20",
        "2026-10-22", "2026-10-23"]
    assert [r[4] for r in table] == [1, 1, 2, 2, 0, 1]
    assert [r[5] for r in table] == ["", "", "", "", "RESET", ""]


def test_threshold():
    days = [("2026-10-%02d" % d, AWAY) for d in range(17, 23)]
    table = wrc.evaluate(days, REF, 3, "2026-10-17")
    # stops on the threshold day (pin 6)
    assert [r[4] for r in table] == [1, 2, 3]
    assert table[-1][5] == "THRESHOLD"


def test_reference():
    rec = {"baseline_counts": {"B": 20},
           "superseded": [{"baseline_counts": {"A": 18, "B": 2},
                           "valid_through": "2026-08-23"},
                          {"baseline_counts": {"A": 20},
                           "valid_through": "2026-08-01"}]}
    # earliest superseded entry (pin 7)
    assert wrc.reference(rec)["baseline_counts"] == {"A": 20}
    assert wrc.reference(REF) is REF


def test_earliest():
    # pin 8
    assert wrc.earliest("2026-10-27", 0) == "2026-11-14"
    assert wrc.earliest("2026-10-27", 17) == "2026-10-28"


if __name__ == "__main__":
    failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("ok   %s" % name)
            except AssertionError as e:
                failed += 1
                print("FAIL %s %s" % (name, e))
    sys.exit(1 if failed else 0)
