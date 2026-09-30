"""Mechanical prose checklist for any draft written for the operator.

Prints, for one draft file: every pronoun or demonstrative with the
nearest noun before it (the reader resolves each); every elided object
("none", "neither", "either", "both", "the rest", "so are", "did");
every bare "held" or "moved" or "stands" or "fired"; every run of three
sentences of twelve words or fewer; every sentence-initial contraction;
every em dash; sentence length statistics; and, when --paper is given,
every number in the draft that does not appear in the paper. It never
edits. A draft is shown to the operator only after this report has run
and each finding has been resolved or named as deliberate.

  python paper/scripts/prose_check.py DRAFT.txt [--paper paper/intercept/main.tex]
"""
import argparse
import re
import sys

PRON = r"\b(it|its|this|that|these|those|they|them|their|which|one|ones)\b"
ELIDE = r"\b(none|neither|either|both|the rest|so are|so is|did|does)\b"
BARE = r"\b(held|moved|stands|stood|fired)\b(?!\s+(constant|still|at|on|to|from|as|in|for|by|toward|the|a|an|its|their|no|every|off|out|up|past|within|against|behind|under|because|and|but|or|so))"
CONTR = r"^(It's|I'm|I'd|I've|That's|There's|Isn't|Can't|Don't|Won't|Doesn't|Didn't)\b"


def sentences(t):
    t = re.sub(r"\s+", " ", t)
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z\"'(])", t) if s.strip()]


def nearest_noun(before):
    words = re.findall(r"[A-Za-z][A-Za-z\-]+", before)
    stop = {"the", "a", "an", "and", "of", "in", "on", "to", "from", "with", "by",
            "for", "at", "is", "was", "are", "were", "be", "not", "no", "that", "it",
            "its", "this", "as", "or", "but", "so", "which", "one", "every", "all"}
    for w in reversed(words):
        if w.lower() not in stop and not w.endswith("ly"):
            return w
    return "?"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("draft")
    ap.add_argument("--paper")
    a = ap.parse_args()
    t = open(a.draft, encoding="utf-8").read()
    body = re.sub(r"^\s*[-*]\s+", "", t, flags=re.M)
    sents = sentences(body)
    findings = 0

    print("== pronouns and demonstratives (resolve each) ==")
    for i, s in enumerate(sents):
        for m in re.finditer(PRON, s, flags=re.I):
            ctx = (sents[i - 1] + " " if i else "") + s[:m.start()]
            print(f"  s{i+1:02d} '{m.group(0)}' <- nearest noun '{nearest_noun(ctx)}' | {s[:70]}")
            findings += 1

    print("== elided objects ==")
    for i, s in enumerate(sents):
        for m in re.finditer(ELIDE, s, flags=re.I):
            print(f"  s{i+1:02d} '{m.group(0)}' | {s[:80]}"); findings += 1

    print("== bare verbs (held/moved/stands/fired without complement) ==")
    for i, s in enumerate(sents):
        for m in re.finditer(BARE, s, flags=re.I):
            print(f"  s{i+1:02d} '{m.group(0)}' | {s[:80]}"); findings += 1

    print("== staccato runs (3 sentences <= 12 words) ==")
    lens = [len(s.split()) for s in sents]
    for i in range(len(lens) - 2):
        if all(l <= 12 for l in lens[i:i + 3]):
            print(f"  s{i+1:02d}-{i+3:02d} ({lens[i]},{lens[i+1]},{lens[i+2]}) | {' '.join(sents[i:i+3])[:120]}"); findings += 1

    print("== sentence-initial contractions ==")
    for i, s in enumerate(sents):
        if re.match(CONTR, s):
            print(f"  s{i+1:02d} | {s[:80]}"); findings += 1

    print("== em dashes ==")
    for i, s in enumerate(sents):
        if "—" in s or "---" in s:
            print(f"  s{i+1:02d} | {s[:80]}"); findings += 1

    if a.paper:
        paper = open(a.paper, encoding="utf-8").read()
        print("== numbers in draft not in paper ==")
        for n in sorted(set(re.findall(r"\d[\d,\.]*", body))):
            if n not in paper:
                print(f"  {n}"); findings += 1

    words = sum(lens)
    print(f"== stats == sentences {len(sents)}, words {words}, mean {words/len(sents):.1f}, "
          f"max {max(lens)}, findings {findings}")


if __name__ == "__main__":
    main()
