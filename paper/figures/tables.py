"""T1 and T2 for the INTERCEPT paper, emitted as markdown.

T1 (structure vs null) shells out to the committed analysis of
record, probe/scripts/recurrence_structure_null.py, and formats its
labeled output lines into the paper table; nothing is recomputed
here, so T1 can never disagree with the script the paper cites. T2
(instrument summary) is assembled from the committed baseline files
and instrument constants. Both land in out/ next to the figures.

  python paper/figures/tables.py
"""
import os
import re
import subprocess
import sys
import collections

import figdata as fd

NULL_SCRIPT = os.path.join(fd.REPO, "probe", "scripts",
                           "recurrence_structure_null.py")
FREEZE_SCRIPT = os.path.join(fd.HERE, "freeze_numbers.py")


def freeze_output():
    proc = subprocess.run((sys.executable, FREEZE_SCRIPT), cwd=fd.REPO,
                          capture_output=True, text=True, check=True)
    return proc.stdout


def conditional_direction(text):
    """(obs, expected, tail) for the >=3 and >=5 thread sets from the
    conditional direction block of freeze_numbers.py."""
    out = {}
    for line in text.splitlines():
        m = re.match(r"\s*threads >=(\d): (\d+), unidirectional (\d+), "
                     r"E\[unidirectional\] ([\d.]+), P\(>= \d+\) = (\S+)",
                     line)
        if m:
            out[m.group(1)] = (m.group(3), m.group(2), m.group(4),
                               m.group(5))
    return out
EFB_SCRIPT = os.path.join(fd.REPO, "probe", "scripts",
                          "expected_false_breaches.py")


def expected_false_breaches():
    """(smoothed, empirical) per-day expectations from the committed
    enumeration script, read off its labeled lines."""
    proc = subprocess.run((sys.executable, EFB_SCRIPT), cwd=fd.REPO,
                          capture_output=True, text=True, check=True)
    vals = {}
    for line in proc.stdout.splitlines():
        for key in ("smoothed", "empirical"):
            if line.strip().startswith("truth = %s" % key):
                vals[key] = line.split("baseline")[1].split()[0]
    return vals["smoothed"], vals["empirical"]


def null_output():
    cmd = [sys.executable, NULL_SCRIPT]
    if fd.DATA_THROUGH != "9999-12-31":
        cmd += ["--end", fd.DATA_THROUGH]
    proc = subprocess.run(cmd, cwd=fd.REPO,
                          capture_output=True, text=True, check=True)
    return proc.stdout


def grab(text, label):
    """Value column of the labeled line, whitespace-collapsed."""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(label):
            return " ".join(stripped[len(label):].split())
    raise KeyError(label)


def build_t1(text, cond):
    window = re.search(r"window (\S+)\.\.(\S+), (\d+) probe days", text)
    start, end, days = window.groups()
    probed = len({v["date"] for v in fd.load_verdicts()
                  if v["verdict"] != "ERROR"
                  and start <= v["date"] <= end})
    entries = int(grab(text, "breach entries").split()[0])
    exp_entries, p_count = re.match(
        r"([\d.]+)\s+P\(>= \d+\) = ([\d.e+-]+)",
        grab(text, "E[breach entries]")).groups()
    obs2, obs3, obs5 = re.match(
        r"(\d+) / (\d+) / (\d+)",
        grab(text, "slots >=2 / >=3 / >=5")).groups()
    exp2, exp3, exp5 = grab(text, "E[slots >=2 / >=3 / >=5]").split(" / ")
    p2 = grab(text, "P(#slots >=2 at least").split(")")[-1].strip()
    p3 = grab(text, "P(#slots >=3 at least").split(")")[-1].strip()
    p5 = grab(text, "P(#slots >=5 at least").split(")")[-1].strip()
    eq_share = grab(text, "eq_ share of breach mass")
    p_all_entries = grab(text, "P(all %d entries on eq_)" % entries)
    distinct = int(grab(text, "distinct breached slots"))
    p_all_distinct = grab(text, "P(all %d distinct on eq_)" % distinct)
    exp_distinct = grab(text, "E[distinct breached slots]")
    dir3 = grab(text, ">=3-threads unidirectional")
    dir5 = grab(text, ">=5-threads unidirectional")
    dir_tail3 = grab(text, "E[slots >=3 same dir]")
    dir_tail5 = grab(text, "P(any slot >=5 same dir)")

    lines = [
        "## T1: breach structure against the exact no-drift null",
        "",
        "Window %s to %s, %s calendar days (%d with a probe). Null:"
        % (start, end, days, probed),
        "exact enumeration under the smoothed baselines",
        "(recurrence_structure_null.py), charging every arm for all %s"
        % days,
        "days; the count row is deliberately weak and reported first.",
        "",
        "| quantity | observed | expected (null) | P(at least obs.) |",
        "| --- | --- | --- | --- |",
        "| breach entries | %d | %s | %s |" % (entries, exp_entries,
                                               p_count),
        "| distinct breached slots | %d | %s | |" % (distinct,
                                                     exp_distinct),
        "| slots with >=2 breaches | %s | %s | %s |" % (obs2, exp2, p2),
        "| slots with >=3 breaches | %s | %s | %s |" % (obs3, exp3, p3),
        "| slots with >=5 breaches | %s | %s | %s |" % (obs5, exp5, p5),
        "| equipoise share of entries | %d of %d | null mass %s | %s |"
        % (entries, entries, eq_share, p_all_entries),
        "| equipoise share, distinct slots | %d of %d | | %s |"
        % (distinct, distinct, p_all_distinct),
        "| unidirectional >=3-threads, joint with clustering | %s | %s | |"
        % (dir3, dir_tail3),
        "| unidirectional >=5-threads, joint with clustering | %s | %s | |"
        % (dir5, dir_tail5),
        "| unidirectional >=3-threads, given the %s threads | %s of %s | %s | %s |"
        % (cond["3"][1], cond["3"][0], cond["3"][1], cond["3"][2],
           cond["3"][3]),
        "| unidirectional >=5-threads, given the %s threads | %s of %s | %s | %s |"
        % (cond["5"][1], cond["5"][0], cond["5"][1], cond["5"][2],
           cond["5"][3]),
        "",
        "Slots within a model-day share a scaffold and are not",
        "independent; per-slot recurrence rows are computed across",
        "days, where the sharing argument does not apply.",
    ]
    return "\n".join(lines) + "\n"


def build_t2():
    verdicts = fd.load_verdicts()
    baselines = fd.load_baselines()
    slots = sum(len(items) for items in baselines.values())
    eq = sum(1 for items in baselines.values()
             for i in items if fd.is_equipoise(i))
    bands = collections.Counter(
        round(rec["band"]["p99"], 2)
        for items in baselines.values() for rec in items.values())
    band_str = ", ".join("%.2f x%d" % (b, n)
                         for b, n in sorted(bands.items()))
    efb = expected_false_breaches()
    days = len({v["date"] for v in verdicts})
    probed = len({v["date"] for v in verdicts if v["verdict"] != "ERROR"})
    calls = sum(v["calls"] or 0 for v in verdicts)
    lines = [
        "## T2: instrument summary",
        "",
        "| parameter | value |",
        "| --- | --- |",
        "| item bank | 68 forced-choice judgment items "
        "(45 decisive, 23 designed-equipoise) |",
        "| models | 5 production APIs, one pinned arm each |",
        "| alarm slots | %d (%d equipoise) |" % (slots, eq),
        "| cadence | scheduled daily, 13:00 UTC, K=10 samples per item |",
        "| baseline | frozen n=20 per slot (two pooled same-day K=10 "
        "runs, 2026-08-02); one slot re-baselined 2026-08-23, original "
        "preserved |",
        "| alarm bands (p99) | %s |" % band_str,
        "| breach test | per-item TVD vs baseline, strictly above "
        "band; same-day rerun disambiguates |",
        "| verdict grammar | CLEAN, EVENT, TRANSIENT, UNSTABLE, "
        "ECHO_CHANGE, ERROR |",
        "| expected false breaches | %s/day (smoothed truth), "
        "%s/day (empirical truth), exact enumeration |" % efb,
        "| record at freeze | %d calendar days (%d with a probe), %s calls |"
        % (days, probed, format(calls, ",")),
        "| operating cost | about 20 USD per month, vendor billing "
        "(the rows record calls, not tokens) |",
    ]
    return "\n".join(lines) + "\n"


def main():
    os.makedirs(fd.OUT, exist_ok=True)
    text = null_output()
    cond = conditional_direction(freeze_output())
    for name, content in (("t1_structure_vs_null.md", build_t1(text, cond)),
                          ("t2_instrument_summary.md", build_t2())):
        with open(os.path.join(fd.OUT, name), "w",
                  encoding="utf-8") as fh:
            fh.write(content)
        print("wrote", name)


if __name__ == "__main__":
    main()
