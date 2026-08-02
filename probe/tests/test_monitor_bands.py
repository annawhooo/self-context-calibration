"""
Smoothed band computation for the monitor, checked against hand-computed
values. No network anywhere in this file (pure arithmetic under test).

Pins:
  1. Per-item TVD over the four options, each side normalized by its own
     parsed count, hand-checked values.
  2. smooth=0 on a degenerate baseline gives zero-width bands (every
     simulated draw reproduces the baseline exactly): the naive plug-in.
  3. Laplace smooth=1 on a degenerate K=10 baseline {A:10}: the smoothed
     probabilities are (11/14, 1/14, 1/14, 1/14) and TVD to baseline
     reduces to (10 - nA)/10 with nA ~ Binomial(10, 11/14). Exact CDF,
     hand-computed: P(TVD <= 0.3) = 0.8526, P(TVD <= 0.4) = 0.9568,
     P(TVD <= 0.5) = 0.9909. Hence p95 = 0.4 and p99 = 0.5; the 10,000-draw
     simulation must land exactly there (margins are 7e-3 and 9e-4 above
     the targets, far outside simulation error at the pinned seeds).
  4. The pooled {A:20} baseline sharpens the band: P(TVD <= 0.4) = 0.9955,
     so p99 tightens from 0.5 to 0.4.
  5. Determinism: identical seed, identical bands; the seed derivation is
     the recorded seed_rule (base:model:item plus purpose suffix).
  6. An empty distribution (zero parsed samples) raises MonitorError, the
     parse-collapse path, rather than dividing by zero.

Run: python probe/tests/test_monitor_bands.py   (plain asserts, exit 1 on
failure; also collectable by pytest).
"""
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from monitor_testkit import monitor  # noqa: E402


def run():
    fails = []

    def check(name, cond, got=None):
        if cond:
            print("  PASS: %s" % name)
        else:
            print("  FAIL: %s | got %r" % (name, got))
            fails.append(name)

    print("=== TVD, hand-checked ===")
    check("identical distributions -> 0",
          monitor.tvd(Counter({"A": 10}), Counter({"A": 10}), 10, 10) == 0.0)
    check("disjoint distributions -> 1",
          monitor.tvd(Counter({"A": 10}), Counter({"B": 10}), 10, 10) == 1.0)
    got = monitor.tvd(Counter({"A": 6, "B": 4}), Counter({"A": 4, "B": 6}),
                      10, 10)
    check("6/4 vs 4/6 -> 0.2", abs(got - 0.2) < 1e-12, got)
    got = monitor.tvd(Counter({"A": 10}), Counter({"A": 5, "B": 5}), 10, 10)
    check("10A vs 5A5B -> 0.5", abs(got - 0.5) < 1e-12, got)
    check("normalization: {A:5} vs {A:10} at n=5,10 -> 0",
          monitor.observed_tvd(Counter({"A": 5}), Counter({"A": 10})) == 0.0)

    print("=== smooth=0 recovers the naive plug-in ===")
    got = monitor.smoothed_bands(Counter({"A": 10}), "any-seed", smooth=0)
    check("degenerate baseline, smooth=0 -> (0, 0)", got == (0.0, 0.0), got)

    print("=== smooth=1 degenerate baseline vs exact binomial ===")
    p95, p99 = monitor.smoothed_bands(Counter({"A": 10}), "hand-check")
    check("{A:10} p95 == 0.4 (exact P(TVD<=0.4)=0.9568)",
          abs(p95 - 0.4) < 1e-12, p95)
    check("{A:10} p99 == 0.5 (exact P(TVD<=0.5)=0.9909)",
          abs(p99 - 0.5) < 1e-12, p99)
    p95, p99 = monitor.smoothed_bands(
        Counter({"A": 10}), monitor.item_seed("m-x", "it1"))
    check("same values at a recorded item seed", (p95, p99) == (0.4, 0.5),
          (p95, p99))

    print("=== pooled baseline sharpens the band ===")
    p95, p99 = monitor.smoothed_bands(Counter({"A": 20}), "hand-check-2")
    check("{A:20} p99 == 0.4 (exact P(TVD<=0.4)=0.9955)",
          abs(p99 - 0.4) < 1e-12, p99)
    check("p95 <= p99", p95 <= p99, (p95, p99))

    print("=== determinism and seed derivation ===")
    a = monitor.smoothed_bands(Counter({"A": 6, "B": 4}), "det-seed")
    b = monitor.smoothed_bands(Counter({"A": 6, "B": 4}), "det-seed")
    check("identical seed -> identical bands", a == b, (a, b))
    check("item_seed derivation",
          monitor.item_seed("m", "i") == "20260802:m:i"
          and monitor.item_seed("m", "i", "band") == "20260802:m:i:band",
          (monitor.item_seed("m", "i"), monitor.item_seed("m", "i", "band")))

    print("=== empty distribution fails as parse collapse ===")
    try:
        monitor.smoothed_bands(Counter(), "z")
        check("empty distribution raises MonitorError", False, "no exception")
    except monitor.MonitorError:
        check("empty distribution raises MonitorError", True)

    print()
    print("FAILURES: %d %s" % (len(fails), fails if fails else "- ALL PASS"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(run())


def test_monitor_bands():  # pytest entry point
    assert run() == 0
