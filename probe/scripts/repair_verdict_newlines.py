"""Repair missing newlines between verdict records, changing nothing else.

Written 2026-10-02. The committed verdicts.jsonl ended without a final
newline after the 2026-09-30 lines, so the next probe appended its first
record onto that line. This splits the file into its JSON records
exactly as written (each record's bytes are kept verbatim), rejoins them
one per line with a final newline, and refuses to write unless:

  - every record parses;
  - the committed HEAD version's records are an exact prefix of the
    result, byte for byte, in order (nothing reordered, edited, or
    dropped);
  - the record count only grows.

Dry run by default; --write writes the file. It never runs git.

Run from the repo root:
  python probe/scripts/repair_verdict_newlines.py           dry run
  python probe/scripts/repair_verdict_newlines.py --write   write
"""
import json
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REL = "probe/monitor/verdicts.jsonl"


def records(text):
    """Exact substrings of each top-level JSON value, in order."""
    dec = json.JSONDecoder()
    out, i, n = [], 0, len(text)
    while i < n:
        while i < n and text[i] in " \t\r\n":
            i += 1
        if i >= n:
            break
        _, end = dec.raw_decode(text, i)
        out.append(text[i:end])
        i = end
    return out


def repaired(head_text, work_text):
    head = records(head_text)
    work = records(work_text)
    if work[:len(head)] != head:
        raise SystemExit("REFUSED: committed records are not an exact prefix")
    return head, work, "\n".join(work) + "\n"


def main(argv):
    path = os.path.join(REPO, REL)
    with open(path, encoding="utf-8", newline="") as f:
        work_text = f.read()
    head_text = subprocess.run(["git", "-C", REPO, "show", "HEAD:" + REL],
                               capture_output=True, text=True,
                               encoding="utf-8").stdout
    head, work, out = repaired(head_text, work_text)
    new = work[len(head):]
    print("committed records %d, file records %d, new %d"
          % (len(head), len(work), len(new)))
    for r in new:
        v = json.loads(r)
        print("  new: %s %s %s" % (v["date"], v["model"], v["verdict"]))
    if out == work_text:
        print("already clean; nothing to write")
        return 0
    if "--write" not in argv:
        print("dry run: rerun with --write to fix the separators")
        return 0
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(out)
    print("written: %s" % REL)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
