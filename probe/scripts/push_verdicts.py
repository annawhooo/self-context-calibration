"""Commit and push the monitor's committable outputs, on a schedule.

The daily probe appends verdict lines to probe/monitor/verdicts.jsonl
(committed; the longitudinal record is the point), but committing and
pushing has been a manual step, batched by hand, and the batches have
lagged origin by days (the non-fast-forward rejection of 2026-08-22 was
this class: two days of lines local, a PR merged remotely in between).
This script is the scheduled push. It stages exactly the two committable
monitor outputs, commits them with a factual tally message, rebases any
local commits onto the remote, and pushes. Nothing else is ever staged
or committed, no matter how dirty the tree.

What it will and will not do:
  - Stages only probe/monitor/verdicts.jsonl and
    probe/monitor/derived/daily_counts.jsonl, each only when its diff is
    append-only. Both files are append-only records by design, and an
    automated task must never be the thing that rewrites one: a diff
    with any deleted line is warned about and left unstaged. This guard
    is what makes --export safe: the export rebuilds daily_counts.jsonl
    from the gitignored rows/, so if rows are ever pruned the
    regenerated file would silently drop published history; here that
    surfaces as a refused non-append-only diff, and the verdicts still
    push alone.
  - --export regenerates daily_counts.jsonl first via
    probe/scripts/export_daily_counts.py (deterministic; its docstring).
    An export failure is logged and does not block the verdict push.
  - Commit messages are built from the staged added lines: date range
    and verdict tally, marked automated in the body. Narrative milestone
    commits ("Days 17 and 18: ...") remain a by-hand act; this only
    keeps the record from lagging. Whatever is already committed by
    hand, the script skips past and just pushes.
  - Refuses to run anywhere but main, mid-rebase, mid-merge, or when
    someone else's work is already staged (exit 2, nothing touched).
  - Never forces. Behind the remote: fetch, rebase local commits on
    top (--autostash, so an unrelated dirty file — including a rewrite
    this script itself refused to stage — cannot block the rebase),
    push. A rebase that stops on conflict is aborted, the commit stays
    local, and the exit is nonzero so the task log carries it.
  - The fetch/rebase/push round retries up to four times (2/4/8/16 s),
    refetching between attempts, so a transient network failure or a
    push race is absorbed. A previously committed but unpushed record
    (a failed push yesterday) is picked up and pushed by the same path.

Exit codes: 0 pushed or nothing to push; 1 rebase/push failure;
2 precondition failure. Run from anywhere; the repo root is found from
the script's own path:

  python probe/scripts/push_verdicts.py --export

Scheduling is documented in probe/monitor/README.md (the 11:30 task);
no scheduler code lives here.
"""
import os
import sys
import json
import time
import argparse
import subprocess
import collections

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, os.pardir, os.pardir))
VERDICTS = "probe/monitor/verdicts.jsonl"
COUNTS = "probe/monitor/derived/daily_counts.jsonl"
PUSHABLE = (VERDICTS, COUNTS)
BACKOFFS = (2, 4, 8, 16)
VERDICT_ORDER = ("CLEAN", "TRANSIENT", "EVENT", "UNSTABLE",
                 "ECHO_CHANGE", "ERROR")


def die(code, message):
    print("push_verdicts: %s" % message, file=sys.stderr)
    sys.exit(code)


def git(*args, ok_to_fail=False):
    proc = subprocess.run(("git",) + args, cwd=REPO,
                          capture_output=True, text=True)
    if proc.returncode != 0 and not ok_to_fail:
        raise RuntimeError("git %s failed (%d): %s" % (
            " ".join(args), proc.returncode,
            (proc.stderr or proc.stdout).strip()))
    return proc


def parse_numstat(output):
    """(added, deleted) from one-path `git diff --numstat` output.

    Empty output (no diff) is (0, 0); a binary marker "-" reads as
    (-1, -1) so callers treat it as not append-only.
    """
    line = output.strip()
    if not line:
        return 0, 0
    added, deleted, _ = line.split("\t", 2)
    if added == "-" or deleted == "-":
        return -1, -1
    return int(added), int(deleted)


def summarize(added_lines, counts_refreshed):
    """Commit message for a set of staged verdict lines.

    added_lines are the raw appended verdicts.jsonl lines. Subject is
    the date range plus a verdict tally in the fixed grammar order;
    unparsable lines are counted as such rather than hidden. The body
    marks the commit automated.
    """
    dates, tally, unparsed = set(), collections.Counter(), 0
    for line in added_lines:
        try:
            row = json.loads(line)
            dates.add(row["date"])
            tally[row["verdict"]] += 1
        except (ValueError, KeyError, TypeError):
            unparsed += 1
    if not dates:
        subject = "Monitor record push"
    else:
        span = min(dates) if len(dates) == 1 else "%s to %s" % (
            min(dates), max(dates))
        order = {v: i for i, v in enumerate(VERDICT_ORDER)}
        parts = ["%d %s" % (tally[v], v) for v in sorted(
            tally, key=lambda v: (order.get(v, len(order)), v))]
        if unparsed:
            parts.append("%d unparsable" % unparsed)
        subject = "Verdicts %s: %s" % (span, ", ".join(parts))
    body = "Automated push (probe/scripts/push_verdicts.py)."
    if counts_refreshed:
        body += " Derived daily counts refreshed in the same commit."
    return subject + "\n\n" + body


def preconditions():
    branch = git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    if branch != "main":
        die(2, "on branch %r, not main; refusing to push" % branch)
    gitdir = git("rev-parse", "--git-dir").stdout.strip()
    gitdir = os.path.normpath(os.path.join(REPO, gitdir))
    for marker in ("rebase-merge", "rebase-apply", "MERGE_HEAD"):
        if os.path.exists(os.path.join(gitdir, marker)):
            die(2, "a rebase or merge is in progress; resolve it by hand")
    staged = git("diff", "--cached", "--name-only").stdout.split()
    strays = [p for p in staged if p not in PUSHABLE]
    if strays:
        die(2, "index already holds staged work outside the monitor "
               "record (%s); refusing to commit it" % ", ".join(strays))


def run_export():
    exporter = os.path.join(HERE, "export_daily_counts.py")
    proc = subprocess.run((sys.executable, exporter), cwd=REPO,
                          capture_output=True, text=True)
    if proc.returncode != 0:
        print("WARNING: daily-counts export failed (%d): %s" % (
            proc.returncode, (proc.stderr or proc.stdout).strip()))
    elif proc.stdout.strip():
        print(proc.stdout.strip())


def stage(path):
    added, deleted = parse_numstat(
        git("diff", "--numstat", "--", path).stdout)
    if (added, deleted) == (0, 0):
        return False
    if deleted != 0 or added < 0:
        print("WARNING: %s diff is not append-only (+%s/-%s); "
              "left unstaged" % (path, added, deleted))
        return False
    git("add", "--", path)
    return True


def commit_if_staged():
    if git("diff", "--cached", "--quiet", ok_to_fail=True).returncode == 0:
        return
    diff = git("diff", "--cached", "-U0", "--", VERDICTS).stdout
    added_lines = [l[1:] for l in diff.splitlines()
                   if l.startswith("+") and not l.startswith("+++")]
    counts_staged = bool(
        git("diff", "--cached", "--name-only", "--", COUNTS).stdout.strip())
    message = summarize(added_lines, counts_staged)
    git("commit", "-m", message)
    print("committed: %s" % message.splitlines()[0])


def push():
    for attempt, backoff in enumerate(BACKOFFS + (None,)):
        try:
            git("fetch", "origin", "main")
            behind = int(git("rev-list", "--count",
                             "main..origin/main").stdout.strip())
            if behind:
                proc = git("rebase", "--autostash", "origin/main",
                           ok_to_fail=True)
                if proc.returncode != 0:
                    git("rebase", "--abort", ok_to_fail=True)
                    die(1, "rebase onto origin/main stopped (%s); commit "
                           "kept local, resolve by hand" %
                           (proc.stderr or proc.stdout).strip())
            ahead = int(git("rev-list", "--count",
                            "origin/main..main").stdout.strip())
            if not ahead:
                print("nothing to push; origin/main already current")
                return
            git("push", "origin", "main")
            print("pushed %d commit%s to origin/main" % (
                ahead, "" if ahead == 1 else "s"))
            return
        except RuntimeError as err:
            if backoff is None:
                die(1, "push failed after %d attempts: %s" % (
                    attempt + 1, err))
            print("WARNING: %s; retrying in %ds" % (err, backoff))
            time.sleep(backoff)


def main():
    parser = argparse.ArgumentParser(
        description="Commit and push the monitor's committable outputs.")
    parser.add_argument("--export", action="store_true",
                        help="regenerate derived/daily_counts.jsonl from "
                             "rows/ before staging")
    args = parser.parse_args()
    preconditions()
    if args.export:
        run_export()
    for path in PUSHABLE:
        stage(path)
    commit_if_staged()
    push()


if __name__ == "__main__":
    main()
