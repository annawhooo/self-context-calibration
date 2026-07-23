"""
Fixture for the analyzer --run-ids multi-run read
(docs/claude_code_handoff_run_ids_read.md, post-lock Deviation), running the
real analyzer against the real files:

  1. --run-id and --run-ids together: error.
  2. --run-ids with the four faithful real-run prefixes plus
     --faithful-realrun-read yields exactly 80+80 Opus query rows (0 orphans,
     the two aborted-run equipoise rows dropped), 160 Haiku, 160 Sonnet; the
     multi-run guard does not fire.
  3. A --run-ids list that omits present run_ids filters those rows out,
     never pools them.
  4. Guard paths unchanged: neither flag with multiple runs still exits 2;
     --run-id (singular) still works alone.

Run: python tests/test_run_ids_read.py   (plain asserts, exit 1 on failure;
also collectable by pytest).
"""
import json
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANALYZER = os.path.join(REPO, "analysis", "analyze.py")

FAITHFUL = "confab_results_faithful.jsonl"
BASELINE = "confab_baseline_faithful.jsonl"

# The four faithful real-run run_id prefixes, recorded in
# docs/baseline_run_note_2026-07-19.md (Faithful real runs, post-lock).
REALRUN_PREFIXES = [
    "2026-07-22T17:32:38",  # Haiku, complete
    "2026-07-22T22:16:15",  # Sonnet, complete
    "2026-07-22T23:09:47",  # Opus derivable (aborted during equipoise)
    "2026-07-22T23:39:51",  # Opus equipoise top-up
]


def resolve_results_dir():
    d = REPO
    for _ in range(8):
        cand = os.path.join(d, "results")
        if os.path.exists(os.path.join(cand, FAITHFUL)):
            return cand
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    raise AssertionError(
        "real results files not found: no results/%s at or above %s" % (FAITHFUL, REPO))


def run_analyzer(args):
    proc = subprocess.run([sys.executable, ANALYZER] + args,
                          capture_output=True, text=True, cwd=REPO)
    return proc.returncode, proc.stdout, proc.stderr


def run():
    fails = []

    def check(name, cond, got=None):
        if cond:
            print("  PASS: %s" % name)
        else:
            print("  FAIL: %s | got %r" % (name, got))
            fails.append(name)

    results_dir = resolve_results_dir()
    faithful_path = os.path.join(results_dir, FAITHFUL)
    baseline_path = os.path.join(results_dir, BASELINE)

    # Resolve the full haiku real-run run_id for --run-id (exact-match) calls.
    haiku_full = None
    with open(faithful_path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rid = json.loads(line).get("run_id", "")
                if rid.startswith(REALRUN_PREFIXES[0]):
                    haiku_full = rid
                    break
    check("haiku real-run run_id present in the results file", haiku_full is not None)

    print("=== 1. --run-id and --run-ids together: error ===")
    code, out, err = run_analyzer(
        [faithful_path, "--family", "faithful", "--run-id", haiku_full or "x",
         "--run-ids", ",".join(REALRUN_PREFIXES)])
    check("both flags: nonzero exit", code != 0, code)
    check("both flags: mutual-exclusion error", "not allowed with" in err,
          err.strip()[-200:])

    print("=== 2. four-prefix read with the real-run read rule ===")
    code, out, err = run_analyzer(
        [faithful_path, "--family", "faithful",
         "--run-ids", ",".join(REALRUN_PREFIXES), "--faithful-realrun-read",
         "--baseline-from", baseline_path])
    check("realrun read: exit 0 (multi-run guard does not fire)", code == 0,
          (code, err.strip()[-300:]))
    expected_cells = [
        ("claude-haiku-4-5-20251001", "derivable", REALRUN_PREFIXES[0], 80, 0),
        ("claude-haiku-4-5-20251001", "equipoise", REALRUN_PREFIXES[0], 80, 0),
        ("claude-sonnet-4-6", "derivable", REALRUN_PREFIXES[1], 80, 0),
        ("claude-sonnet-4-6", "equipoise", REALRUN_PREFIXES[1], 80, 0),
        ("claude-opus-4-7", "derivable", REALRUN_PREFIXES[2], 80, 0),
        ("claude-opus-4-7", "equipoise", REALRUN_PREFIXES[3], 80, 2),
    ]
    for model, cell, prefix, kept, dropped in expected_cells:
        pat = (r"%s\s+%s\s+run %s \| query rows kept %d \| dropped %d"
               % (re.escape(model), cell, re.escape(prefix), kept, dropped))
        check("read map %s %s: run %s, kept %d, dropped %d"
              % (model, cell, prefix, kept, dropped),
              re.search(pat, out) is not None,
              "\n".join(l for l in out.splitlines() if model in l and "run " in l)[:300])
    for model in ("claude-haiku-4-5-20251001", "claude-sonnet-4-6", "claude-opus-4-7"):
        pat = r"%s\s+excluded recovered-tier rows: \d+ of 160 query rows" % re.escape(model)
        check("%s analyzed set is 160 query rows" % model,
              re.search(pat, out) is not None,
              "\n".join(l for l in out.splitlines() if "query rows" in l)[:300])

    print("=== 3. omitting present run_ids filters, never pools ===")
    code, out, err = run_analyzer(
        [faithful_path, "--family", "faithful", "--run-ids", REALRUN_PREFIXES[0]])
    check("single-prefix allow-list: exit 0", code == 0, (code, err.strip()[-200:]))
    models_line = next((l for l in out.splitlines() if l.startswith("Models:")), "")
    check("only haiku rows remain", models_line == "Models: claude-haiku-4-5-20251001",
          models_line)
    header = next((l for l in out.splitlines() if l.startswith("Family:")), "")
    check("header lists only the allowed run",
          REALRUN_PREFIXES[0] in header
          and not any(p in header for p in REALRUN_PREFIXES[1:]),
          header)

    print("=== 4. guard paths unchanged ===")
    code, out, err = run_analyzer([faithful_path, "--family", "faithful"])
    check("no flags with multiple runs: exit 2", code == 2, code)
    check("no flags: pooling refusal message", "Multiple run_ids present" in err,
          err.strip()[-200:])
    code, out, err = run_analyzer(
        [faithful_path, "--family", "faithful", "--run-id", haiku_full or "x"])
    check("--run-id (singular) alone: unchanged, exit 0", code == 0,
          (code, err.strip()[-300:]))

    print()
    print("FAILURES: %d %s" % (len(fails), fails if fails else "- ALL PASS"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(run())


def test_run_ids_read():  # pytest entry point
    assert run() == 0
