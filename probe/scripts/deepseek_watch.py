"""Daily side-channel observation of the renamed deepseek identity.

Pinned by probe/DECISIONS_2026-10-02.md. The monitor's deepseek arm has
been halted by its echo tripwire since 2026-09-10 (the pinned id
deepseek-v4-flash answers under deepseek-flash) and stays halted. This
script observes what a customer pinned to deepseek-v4-flash now
receives, without touching the monitor or its record:

  - Same request path as the monitor: convergence.collect.run_collection
    (which calls the collect_row the monitor imports), the monitor's own
    roster entry for deepseek-v4-flash, arm A, K=10, the 68-item bank.
  - Separate everything else. Rows go to probe/deepseek_watch/rows/
    (gitignored, they embed replies); one counts-only line per day is
    appended to probe/deepseek_watch/daily_counts.jsonl. Nothing under
    probe/monitor/ is read for decisions or written, ever.
  - Runs only in a clone checked out on the branch deepseek-watch, never
    in the monitor's working tree on main, and pushes only that branch.
    It never rebases, merges, or force-pushes; a failed push leaves the
    commit local and the next day's push carries both.

Watch data never enters verdicts.jsonl, daily_counts.jsonl under
probe/monitor/, any null, any band, or any paper number. Its only use is
the descriptive comparison pinned in the decision note.

Run (from the watch clone's root):
  python probe/scripts/deepseek_watch.py            collect, summarize, push
  python probe/scripts/deepseek_watch.py --no-git   collect and summarize only
"""
import argparse
import datetime
import json
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "harness"))

WATCH_BRANCH = "deepseek-watch"
MODEL_ID = "deepseek-v4-flash"
ARM = "A"
K = 10
ROSTER_PATH = os.path.join(REPO, "probe", "monitor", "roster.json")
WATCH_DIR = os.path.join(REPO, "probe", "deepseek_watch")
ROWS_DIR = os.path.join(WATCH_DIR, "rows")
COUNTS_PATH = os.path.join(WATCH_DIR, "daily_counts.jsonl")
LABELS = ("A", "B", "C", "D")


def branch_ok(branch_name):
    """The watch runs only on its own branch."""
    return branch_name == WATCH_BRANCH


def summarize(rows, date, requested=MODEL_ID):
    """One counts-only line for a day's rows. Per item: answer counts over
    A..D, unparsed counted separately. Echoes tallied per distinct id. No
    reply text is carried."""
    items = {}
    echoes = {}
    unparsed = 0
    for r in rows:
        iid = r.get("item_id")
        if iid is None:
            continue
        cell = items.setdefault(iid, {lab: 0 for lab in LABELS})
        lab = r.get("parsed")
        if lab in LABELS:
            cell[lab] += 1
        else:
            unparsed += 1
        echo = r.get("model_id_exact")
        echoes[echo] = echoes.get(echo, 0) + 1
    return {
        "date": date,
        "requested": requested,
        "arm": ARM,
        "k": K,
        "calls": sum(echoes.values()),
        "unparsed": unparsed,
        "echo": dict(sorted(echoes.items(), key=lambda kv: str(kv[0]))),
        "items": dict(sorted(items.items())),
    }


def read_rows(path):
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except ValueError:
                continue  # torn final line from an aborted run
    return rows


def git(*args):
    return subprocess.run(["git", "-C", REPO] + list(args),
                          capture_output=True, text=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--no-git", action="store_true",
                    help="collect and summarize; skip the branch guard, "
                         "commit, and push")
    args = ap.parse_args(argv)

    if not args.no_git:
        b = git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
        if not branch_ok(b):
            sys.stderr.write("REFUSED: on branch {!r}; the watch runs only "
                             "on {!r} in its own clone.\n".format(b, WATCH_BRANCH))
            return 2

    from convergence.collect import (load_roster, select_models,
                                     run_collection)
    date = datetime.date.today().isoformat()
    os.makedirs(ROWS_DIR, exist_ok=True)
    rows_path = os.path.join(ROWS_DIR, "watch_{}.jsonl".format(date))
    models = select_models(load_roster(ROSTER_PATH), MODEL_ID)
    status = run_collection(models, ARM, rows_path, k=K)

    line = summarize(read_rows(rows_path), date)
    line["halted"] = bool(status.get("halted"))
    with open(COUNTS_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(line, sort_keys=True) + "\n")
    print("watch {}: {} calls, echo {}, unparsed {}".format(
        date, line["calls"], line["echo"], line["unparsed"]))

    if args.no_git:
        return 0
    git("add", COUNTS_PATH)
    c = git("commit", "-m", "Deepseek watch {}: {} calls".format(date, line["calls"]),
            "-m", "Automated by probe/scripts/deepseek_watch.py; counts only.")
    if c.returncode != 0:
        sys.stderr.write("commit: " + c.stdout + c.stderr)
    p = git("push", "origin", WATCH_BRANCH)
    if p.returncode != 0:
        sys.stderr.write("push failed, commit kept local: " + p.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
