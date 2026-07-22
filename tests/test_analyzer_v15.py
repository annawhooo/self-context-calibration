"""
Fixture for the analyzer v1.5 reconciliation (docs/claude_code_handoff_analyzer_v15.md),
running the real analyzer against the real files:

  1. Stratum assertion: sizes 53/15 (haiku), 60/8 (sonnet), 65/3 (opus) from the
     zero-miss rule under the pinned read rule.
  2. Dry-run reproduction on the July faithful data with the needle_source
     sensitivity basis (existing-tier rows only): haiku derivable-bank mixture
     c=0.82, r=0.05, s=0.00, a=0.00 at two decimals; sonnet and opus CT=1.00 and
     deny_false=1.00 on their July legs; opus equipoise deny_true 2 of 5. These
     are the recorded dry-run reads (PRE_REGISTRATION_FAITHFUL.md, Dry-run
     disclosure) on the same row basis they were computed from: the per-model
     July legs, restricted to the legacy item_cell the dry run read, which the
     test reconstructs by filtering rows of the real results file (legacy
     plumbing; no synthetic rows).
  3. Full-read numbers (recovered rows included) are printed, not asserted; the
     research chat hand-verifies them at re-verification.
  4. Generalized path spot-run: byte-identical output (modulo the path header
     line and line endings) to tests/golden_generalized_output.txt, captured
     from the pre-reconciliation analyzer on the same generalized results file.

The real results and baseline JSONLs are gitignored and live in the main
checkout's results/ directory; the test resolves them by walking up from the
repo root, so it works from a worktree as well.

Run: python tests/test_analyzer_v15.py   (plain asserts, exit 1 on failure;
also collectable by pytest).
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANALYZER = os.path.join(REPO, "analysis", "analyze.py")

FAITHFUL = "confab_results_faithful.jsonl"
BASELINE = "confab_baseline_faithful.jsonl"
GENERALIZED = "confab_results_generalized.jsonl"
GOLDEN_GENERALIZED = os.path.join(REPO, "tests", "golden_generalized_output.txt")

# July pilot legs (run_id prefixes; the dry-run disclosure basis).
LEGS = {
    "haiku": ("claude-haiku-4-5-20251001", "2026-07-04T16:02:19"),
    "sonnet": ("claude-sonnet-4-6", "2026-07-04T16:59:24"),
    "opus": ("claude-opus-4-7", "2026-07-05T14:49:49"),
}

PINNED_STRATA = {
    "claude-haiku-4-5-20251001": (53, 15),
    "claude-sonnet-4-6": (60, 8),
    "claude-opus-4-7": (65, 3),
}


def resolve_results_dir():
    """results/*.jsonl is gitignored; find the directory holding the real files,
    starting at the repo root and walking up (covers running from a worktree)."""
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


def load_rows(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def run_analyzer(args):
    proc = subprocess.run([sys.executable, ANALYZER] + args,
                          capture_output=True, text=True, cwd=REPO)
    return proc.returncode, proc.stdout, proc.stderr


def section(text, start_tag, end_tags):
    """Slice of text from the line containing start_tag up to the first
    following line containing any end_tag (or the end of text)."""
    i = text.find(start_tag)
    if i < 0:
        return ""
    rest = text[i:]
    end = len(rest)
    for tag in end_tags:
        j = rest.find(tag, len(start_tag))
        if j >= 0:
            end = min(end, j)
    return rest[:end]


def write_basis(rows, path):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


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
    generalized_path = os.path.join(results_dir, GENERALIZED)
    for p in (faithful_path, baseline_path, generalized_path):
        assert os.path.exists(p), "missing real file: %s" % p

    all_rows = load_rows(faithful_path)
    tmp = tempfile.mkdtemp(prefix="analyzer_v15_fixture_")
    try:
        # --- 1 + 3: full-leg runs on the real file (strata assert; full-read print).
        full_outputs = {}
        for name, (model, rid_prefix) in LEGS.items():
            rids = sorted({r["run_id"] for r in all_rows
                           if r["run_id"].startswith(rid_prefix)})
            check("%s leg run_id resolves uniquely" % name, len(rids) == 1, rids)
            if len(rids) != 1:
                continue
            code, out, err = run_analyzer(
                [faithful_path, "--family", "faithful", "--run-id", rids[0],
                 "--baseline-from", baseline_path])
            check("%s full-leg analyzer exit 0" % name, code == 0,
                  (code, err.strip()[-300:]))
            full_outputs[name] = out

        print("=== 1. stratum assertion (zero-miss rule, pinned read rule) ===")
        out = full_outputs.get("haiku", "")
        strata_sec = section(out, "STRATA (zero-miss", ["\n\n"])
        for model, (n_anchor, n_ident) in PINNED_STRATA.items():
            pat = r"%s\s+anchor (\d+) \| identifying (\d+)" % re.escape(model)
            m = re.search(pat, strata_sec)
            got = (int(m.group(1)), int(m.group(2))) if m else strata_sec[:200]
            check("strata %s == %d/%d" % (model, n_anchor, n_ident),
                  m is not None and got == (n_anchor, n_ident), got)

        # --- 2. dry-run reproduction on the dry-run row basis (existing-tier rows only).
        print("=== 2. dry-run reproduction (needle_source sensitivity basis) ===")
        basis_outputs = {}
        for name, (model, rid_prefix) in LEGS.items():
            for cell in (("derivable", "equipoise") if name == "opus" else ("derivable",)):
                basis = [r for r in all_rows
                         if r["run_id"].startswith(rid_prefix)
                         and (r.get("item_cell") or "derivable") == cell]
                bpath = os.path.join(tmp, "%s_%s.jsonl" % (name, cell))
                write_basis(basis, bpath)
                code, out, err = run_analyzer(
                    [bpath, "--family", "faithful",
                     "--baseline-from", baseline_path])
                check("%s %s basis analyzer exit 0" % (name, cell), code == 0,
                      (code, err.strip()[-300:]))
                basis_outputs[(name, cell)] = out

        def ns_section(out):
            return section(out, "SENSITIVITY needle_source (existing-tier rows only)",
                           ["SENSITIVITY near-anchor"])

        # haiku derivable-bank mixture c=0.82, r=0.05, s=0.00, a=0.00.
        sec = ns_section(basis_outputs.get(("haiku", "derivable"), ""))
        m = re.search(r"claude-haiku-4-5-20251001\s+r=(\d+\.\d\d) s=(\d+\.\d\d) "
                      r"a=(\d+\.\d\d) c=(\d+\.\d\d)", sec)
        got = m.groups() if m else sec[:200]
        check("haiku derivable-bank mixture r=0.05 s=0.00 a=0.00 c=0.82",
              m is not None and got == ("0.05", "0.00", "0.00", "0.82"), got)

        # sonnet and opus CT=1.00 and deny_false=1.00 on their July legs.
        for name, model in (("sonnet", "claude-sonnet-4-6"),
                            ("opus", "claude-opus-4-7")):
            sec = ns_section(basis_outputs.get((name, "derivable"), ""))
            m = re.search(r"%s\s+CT \d+/\d+=(\d+\.\d\d) \| CF \d+/\d+=\d+\.\d\d \| "
                          r"DT \d+/\d+=\d+\.\d\d \| DF \d+/\d+=(\d+\.\d\d)"
                          % re.escape(model), sec)
            got = m.groups() if m else sec[:200]
            check("%s derivable CT=1.00" % name,
                  m is not None and m.group(1) == "1.00", got)
            check("%s derivable deny_false=1.00" % name,
                  m is not None and m.group(2) == "1.00", got)

        # opus equipoise deny_true 2 of 5.
        sec = ns_section(basis_outputs.get(("opus", "equipoise"), ""))
        m = re.search(r"claude-opus-4-7\s+CT \d+/\d+=\d+\.\d\d \| CF \d+/\d+=\d+\.\d\d"
                      r" \| DT (\d+)/(\d+)=\d+\.\d\d", sec)
        got = m.groups() if m else sec[:200]
        check("opus equipoise deny_true 2 of 5",
              m is not None and got == ("2", "5"), got)

        # --- 3. full-read numbers: printed for hand-verification, not asserted.
        print("=== 3. full-read mixtures (recovered rows included; hand-verify) ===")
        for name in LEGS:
            out = full_outputs.get(name, "")
            mix = section(out, "MIXTURE (residual read)", ["MIXTURE by stratum"])
            print("--- %s full-read ---" % name)
            for line in mix.splitlines():
                print("  |", line)

        # --- 4. generalized path spot-run, unchanged in output.
        print("=== 4. generalized path unchanged ===")
        code, out, err = run_analyzer([generalized_path])
        check("generalized analyzer exit 0", code == 0, (code, err.strip()[-300:]))
        with open(GOLDEN_GENERALIZED, encoding="utf-8") as f:
            golden = f.read().splitlines()
        # Drop the "Analysis of <path>" header line; it embeds the invocation path.
        lines = out.splitlines()[1:]
        check("generalized output matches pre-change golden", lines == golden,
              "first diff: %r" % next(
                  (a_b for a_b in zip(lines + ["<end>"], golden + ["<end>"])
                   if a_b[0] != a_b[1]), None))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    print("FAILURES: %d %s" % (len(fails), fails if fails else "- ALL PASS"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(run())


def test_analyzer_v15():  # pytest entry point
    assert run() == 0
