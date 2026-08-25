"""Diff the draft's keyed FREEZE tags against the number manifest.

The verifier half of the numbers policy. Every regenerable number in
paper/INTERCEPT_DRAFT.md sits inside a keyed tag:

    [FREEZE <key>: <rendered value>]

freeze_numbers.py computes the manifest (out/freeze_numbers.json);
this script parses the draft, compares each keyed tag's content to
the manifest render for that key, and reports:

    OK        tag matches the manifest render exactly
    STALE     tag differs (the draft carries an older record's value)
    NO-KEY    the tag names a key the manifest does not have
    MANUAL    an unkeyed [FREEZE ...] tag; a human placeholder, listed
              so none is forgotten at the freeze

Exit status is 1 while any STALE or NO-KEY remains, so the freeze-day
loop is: rerun freeze_numbers.py, rerun this until clean. --apply
rewrites every keyed tag's content to the manifest render in place;
prose around the tags is never touched, so a swap that changes
sentence logic (a zero that became nonzero, a claim that inverted)
still needs the human pass the STALE listing points at. Provenance
rides along: applying a raw-rows or no-script value prints a warning,
because those renders are last published values, not regenerated
ones.

  python paper/figures/check_draft_numbers.py [--apply]
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, os.pardir, os.pardir))
DRAFT = os.path.join(REPO, "paper", "INTERCEPT_DRAFT.md")
MANIFEST = os.path.join(HERE, "out", "freeze_numbers.json")

TAG = re.compile(r"\[FREEZE(?:\s+(?P<key>[a-z0-9-]+))?"
                 r"(?::\s*(?P<content>[^\]]*?))?\s*\]")


def normalize(s):
    return " ".join((s or "").split())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="rewrite keyed tag contents from the "
                         "manifest")
    args = ap.parse_args()

    with open(MANIFEST, encoding="utf-8") as fh:
        doc = json.load(fh)
    entries = doc["entries"]
    with open(DRAFT, encoding="utf-8") as fh:
        text = fh.read()

    stale, no_key, manual, ok = [], [], [], []
    used = set()

    def replacement(m):
        key, content = m.group("key"), normalize(m.group("content"))
        line = text.count("\n", 0, m.start()) + 1
        if key is None:
            manual.append((line, content))
            return m.group(0)
        if key not in entries:
            no_key.append((line, key))
            return m.group(0)
        used.add(key)
        want = entries[key]["render"]
        prov = entries[key]["provenance"]
        if normalize(content) == normalize(want):
            ok.append((line, key))
            return m.group(0)
        stale.append((line, key, content, want, prov))
        if args.apply:
            if prov in ("raw-rows", "no-script"):
                print("WARNING applying %s value for %s (line %d): "
                      "not regenerated from the record"
                      % (prov, key, line))
            return "[FREEZE %s: %s]" % (key, want)
        return m.group(0)

    new_text = TAG.sub(replacement, text)

    print("draft: %s" % os.path.relpath(DRAFT, REPO))
    print("manifest: data through %s (%d probe days)"
          % (doc["data_through"], doc["probe_days"]))
    print()
    for line, key in ok:
        print("  OK     line %-4d %s" % (line, key))
    for line, key, content, want, prov in stale:
        print("  STALE  line %-4d %-28s draft %r" % (line, key,
                                                     content))
        print("                    %-28s manifest %r%s"
              % ("", want,
                 "  [%s]" % prov if prov != "record" else ""))
    for line, key in no_key:
        print("  NO-KEY line %-4d %s is not in the manifest"
              % (line, key))
    for line, content in manual:
        print("  MANUAL line %-4d [FREEZE%s]"
              % (line, ": " + content if content else ""))
    unused = sorted(set(entries) - used)
    if unused:
        print()
        print("manifest keys the draft never references: %s"
              % ", ".join(unused))
    print()
    print("%d ok, %d stale, %d unknown key, %d manual placeholders"
          % (len(ok), len(stale), len(no_key), len(manual)))

    if args.apply and new_text != text:
        with open(DRAFT, "w", encoding="utf-8") as fh:
            fh.write(new_text)
        print("applied %d manifest renders to the draft"
              % len(stale))
    if stale and not args.apply or no_key:
        sys.exit(1)


if __name__ == "__main__":
    main()
