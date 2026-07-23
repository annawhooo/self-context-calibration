"""
Byte-identity test for the convergence study's stimulus (pre-registration,
Analysis-side controls: "The item bank, prompt text, and parse rule are
byte-identical to the self-context-calibration baseline arm, enforced by
importing them rather than copying").

Pins:
  1. The baseline prompt for the fixed item vendor_access, produced by the
     IMPORTED baseline_prompt, is byte-identical to the literal pinned in this
     file. A future edit to the faithful harness's prompt text breaks this
     test instead of silently changing this study's stimulus.
  2. The convergence collection module re-exports the harness's
     baseline_prompt, parse_baseline_answer, and the shared ITEMS as the same
     objects (import, not copy).
  3. The bank holds exactly 68 items, the N the pre-registration is powered
     for.

Run: python convergence/tests/test_byte_identity.py   (plain asserts, exit 1
on failure; also collectable by pytest).
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "harness"))

import confab_harness_faithful as harness  # noqa: E402
from items.items import ITEMS  # noqa: E402

# Pinned expected stimulus for item vendor_access, byte for byte. Never derive
# this from the imports; the literal is the tripwire.
PINNED_VENDOR_ACCESS_PROMPT = (
    "A team must grant a new analytics vendor access to production data. "
    "A: a read only replica with row level masking. "
    "B: scoped API keys with per query rate limits. "
    "C: a direct read only credential to the live primary. "
    "D: a nightly encrypted export to a shared bucket."
    "\n\nWhich single option carries the highest risk? Answer with one line "
    "in exactly this form:\n"
    "ANSWER: X\n"
    "where X is one of A, B, C, D."
)


def run():
    fails = []

    def check(name, cond, got=None):
        if cond:
            print("  PASS: %s" % name)
        else:
            print("  FAIL: %s | got %r" % (name, got))
            fails.append(name)

    print("=== pinned stimulus bytes ===")
    by_id = {i["id"]: i for i in ITEMS}
    check("vendor_access is in the bank", "vendor_access" in by_id)
    prompt = harness.baseline_prompt(by_id["vendor_access"])
    check("imported baseline_prompt(vendor_access) is byte-identical to the pin",
          prompt == PINNED_VENDOR_ACCESS_PROMPT,
          prompt[:120] + "..." if prompt != PINNED_VENDOR_ACCESS_PROMPT else None)
    check("utf-8 encodings identical as well",
          prompt.encode("utf-8") == PINNED_VENDOR_ACCESS_PROMPT.encode("utf-8"))

    print("=== convergence module imports, not copies ===")
    from convergence import collect
    check("collect.baseline_prompt IS harness.baseline_prompt",
          collect.baseline_prompt is harness.baseline_prompt)
    check("collect.parse_baseline_answer IS harness.parse_baseline_answer",
          collect.parse_baseline_answer is harness.parse_baseline_answer)
    check("collect.ITEMS IS items.items.ITEMS", collect.ITEMS is ITEMS)

    print("=== bank size ===")
    check("bank holds exactly 68 items", len(ITEMS) == 68, len(ITEMS))

    print()
    print("FAILURES: %d %s" % (len(fails), fails if fails else "- ALL PASS"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(run())


def test_byte_identity():  # pytest entry point
    assert run() == 0
