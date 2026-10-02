"""
Pure-function pins for the deepseek side-channel watch
(probe/scripts/deepseek_watch.py). No network and no git.

Pins:
  1. The branch guard admits only "deepseek-watch"; main and every other
     name are refused, so the watch can never run in the monitor's tree.
  2. summarize counts A..D per item, counts unparsed separately, tallies
     echoes per distinct id, and carries no reply text.
  3. The watch never writes under probe/monitor/: its paths all sit in
     probe/deepseek_watch/.

Run: python probe/tests/test_deepseek_watch.py   (plain asserts, exit 1
on failure; also collectable by pytest).
"""
import os
import sys
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, os.pardir, "scripts", "deepseek_watch.py")
spec = importlib.util.spec_from_file_location("deepseek_watch", SCRIPT)
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)


def test_branch_guard():
    assert w.branch_ok("deepseek-watch")
    for b in ("main", "claude/fervent-lovelace-q741su", "HEAD", ""):
        assert not w.branch_ok(b)


def test_summarize():
    rows = [
        {"item_id": "x", "parsed": "A", "model_id_exact": "deepseek-flash",
         "raw_text": "secret reply"},
        {"item_id": "x", "parsed": "A", "model_id_exact": "deepseek-flash"},
        {"item_id": "x", "parsed": None, "model_id_exact": "deepseek-flash"},
        {"item_id": "y", "parsed": "D", "model_id_exact": "deepseek-v4-flash"},
    ]
    s = w.summarize(rows, "2026-10-03")
    assert s["items"]["x"] == {"A": 2, "B": 0, "C": 0, "D": 0}
    assert s["items"]["y"] == {"A": 0, "B": 0, "C": 0, "D": 1}
    assert s["unparsed"] == 1
    assert s["calls"] == 4
    assert s["echo"] == {"deepseek-flash": 3, "deepseek-v4-flash": 1}
    assert "secret reply" not in repr(s)
    assert s["requested"] == "deepseek-v4-flash" and s["k"] == 10


def test_paths_outside_monitor():
    monitor = os.path.normpath(os.path.join(w.REPO, "probe", "monitor"))
    for p in (w.WATCH_DIR, w.ROWS_DIR, w.COUNTS_PATH):
        assert not os.path.normpath(p).startswith(monitor + os.sep)


if __name__ == "__main__":
    failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("ok   " + name)
            except AssertionError as exc:
                failed += 1
                print("FAIL " + name + " " + repr(exc))
    sys.exit(1 if failed else 0)
