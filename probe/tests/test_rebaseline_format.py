"""
Pins for the dual-reference re-baseline format and its two readers.
No network: the qualification runs are not exercised here (they go
through the monitor machinery pinned by the monitor tests); what is
pinned is the pure record transform (rebaseline_item.supersede_item),
the date-aware reference selector (paper/figures/figdata.baseline_for)
and the pre-registered return criterion (return_watch.is_return).

Pins:
  1. supersede_item moves the old item record intact into the
     superseded list with valid_from = the file's qualification date
     and valid_through = the run date, installs the new record's
     monitor-visible keys, appends to earlier superseded entries
     rather than replacing them, grows the file-level rebaselines
     list, and never mutates its input.
  2. baseline_for honors the pinned boundary convention: a date
     inside the superseded window (its valid_through day included)
     resolves to the old reference; the day after resolves to the
     active one; a record with no supersession returns itself.
  3. is_return is the pre-registered criterion exactly: within the
     superseded band AND modal match. The away vector fails on
     modal, an at-band non-modal day fails, a modal tie fails.

Run: python probe/tests/test_rebaseline_format.py   (plain asserts,
exit 1 on failure; also collectable by pytest).
"""
import os
import sys
import copy
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))


def load(name, *parts):
    path = os.path.join(REPO, *parts)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


sys.path.insert(0, os.path.join(REPO, "paper", "figures"))
import figdata  # noqa: E402
rebaseline = load("rebaseline_item", "probe", "scripts",
                  "rebaseline_item.py")
return_watch = load("return_watch", "probe", "scripts",
                    "return_watch.py")

OLD = {"class": "alarm",
       "baseline_counts": {"A": 2, "B": 1, "D": 17}, "n": 20,
       "band": {"seed": "s:band", "p95": 0.4, "p99": 0.45},
       "runs": {"run1": {"D": 9, "A": 1}, "run2": {"D": 8, "A": 1,
                                                   "B": 1}},
       "qualification": {"third_run": None}}
NEW = {"class": "alarm",
       "baseline_counts": {"B": 13, "D": 7}, "n": 20,
       "band": {"seed": "s:rebl-band:2026-08-23", "p95": 0.4,
                "p99": 0.45},
       "runs": {"run1": {"B": 6, "D": 4}, "run2": {"B": 7, "D": 3}},
       "qualification": {"third_run": None}}
BASE = {"model": "m", "date": "2026-08-02", "items": {"it": OLD}}


def test_supersede():
    before = copy.deepcopy(BASE)
    out = rebaseline.supersede_item(BASE, "it", NEW, "2026-08-23")
    assert BASE == before                                    # pure
    rec = out["items"]["it"]
    assert rec["baseline_counts"] == {"B": 13, "D": 7}
    assert rec["band"]["p99"] == 0.45
    assert rec["valid_from"] == "2026-08-23"
    old = rec["superseded"][0]
    assert old["baseline_counts"] == OLD["baseline_counts"]
    assert old["valid_from"] == "2026-08-02"
    assert old["valid_through"] == "2026-08-23"
    assert out["rebaselines"][0]["item"] == "it"
    # a second supersession appends, never replaces
    newer = dict(NEW, baseline_counts={"A": 20})
    out2 = rebaseline.supersede_item(out, "it", newer, "2026-09-10")
    olds = out2["items"]["it"]["superseded"]
    assert len(olds) == 2
    assert olds[0]["valid_through"] == "2026-08-23"
    assert olds[1]["valid_from"] == "2026-08-23"
    assert olds[1]["valid_through"] == "2026-09-10"


def test_baseline_for():
    out = rebaseline.supersede_item(BASE, "it", NEW, "2026-08-23")
    rec = out["items"]["it"]
    assert figdata.baseline_for(rec, "2026-08-02") is rec["superseded"][0]
    assert figdata.baseline_for(rec, "2026-08-23") is rec["superseded"][0]
    assert figdata.baseline_for(rec, "2026-08-24") is rec
    assert figdata.baseline_for(OLD, "2026-08-10") is OLD
    assert figdata.ref_key(rec, "2026-08-23") == "2026-08-02"
    assert figdata.ref_key(rec, "2026-08-24") == "2026-08-23"


def test_is_return():
    out = rebaseline.supersede_item(BASE, "it", NEW, "2026-08-23")
    old = out["items"]["it"]["superseded"][0]
    assert return_watch.is_return({"D": 8, "A": 2}, old)      # home
    assert not return_watch.is_return({"B": 6, "D": 4}, old)  # away
    # near-miss inside band arithmetic but wrong modal is no return
    assert not return_watch.is_return({"B": 5, "D": 5}, old)  # tie
    assert not return_watch.is_return({"B": 10}, old)


def main():
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print("ok %s" % name)
    print("all rebaseline format pins hold")


if __name__ == "__main__":
    main()
