"""Single-item re-baseline with the original qualification semantics.

Operator-run, never scheduled. Implements the dual-reference
re-baseline of probe/REBASELINE_DECISION_2026-08-23.md for one item
of one roster model: the item's current reference is preserved
intact inside the item record (a "superseded" entry with validity
dates, invisible to monitor.py, which reads only baseline_counts and
band), and a freshly qualified reference to the item's current state
becomes the alarm reference. The monitor itself is untouched: this
is a data change to the committed baseline file, made through the
monitor's own imported machinery so the new reference is
structurally identical to every other slot's.

Qualification, mirroring monitor.py baseline (DRIFT_EVENT_2026-07-31
design consequence 1), scoped to one item: two same-day K=10 runs
through run_bank (the production collect path, echo tripwire armed
with the existing baseline's recorded echo), parse-collapse checks,
run-pair TVD against run1's smoothed p99 band, pooled n=20 counts,
and a band from the pooled counts. No third-run logic: a failed
run-pair gate aborts with a report and writes nothing; a state
unstable across two same-day runs is not a state to re-baseline
onto, and the operator escalates by hand. Seeds follow the recorded
seed rule with new purpose suffixes ("rebl:<date>" for run1 bands,
"rebl-band:<date>" for the pooled band) so the new reference's
bands can never collide with, or silently reuse, the originals.

Two additional gates, the sanity-gate pattern of the declined K=30
procedure: the new pooled reference must sit outside the OLD
reference's p99 band (re-baselining onto a state indistinct from
the old one voids the premise), and the old record must not already
carry a superseded entry for the same date (double-run protection).

Validity convention, pinned: the superseded reference's
valid_through is the run date, and the new reference governs from
the day after. Run this AFTER the day's probe, so the boundary day's
verdict was scored against the reference actually in force when it
ran. The analysis-side selector (paper/figures/figdata.baseline_for)
implements the same convention.

Cost: 2 x K calls (20 at K=10). Rows land in probe/monitor/rows/
(gitignored). The rewritten baseline file is the committable record;
inspect the diff before committing, per the decision note.

  python probe/scripts/rebaseline_item.py \
      --model claude-haiku-4-5-20251001 --item eq_alert_spend_anomaly_v2
"""
import os
import sys
import json
import argparse

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "harness"))
sys.path.insert(0, os.path.join(REPO, "probe", "monitor"))

import monitor as mon  # noqa: E402

DECISION = "probe/REBASELINE_DECISION_2026-08-23.md"
CANDIDACY = "probe/STEP_CHANGE_CANDIDACY_2026-08-23.md"


def supersede_item(baseline, iid, new_rec, date):
    """Return the baseline dict with item iid's reference superseded.

    Pure transform, no I/O: the old item record moves intact into the
    new record's superseded list (appending to any earlier entries),
    stamped with its validity window; the new record becomes the
    monitor-visible reference from the day after. The file-level
    rebaselines list gains one entry for discoverability.
    """
    old = dict(baseline["items"][iid])
    prior = old.pop("superseded", [])
    old["valid_from"] = old.get("valid_from", baseline["date"])
    old["valid_through"] = date
    new_rec = dict(new_rec)
    new_rec["valid_from"] = date
    new_rec["superseded"] = prior + [old]
    new_rec["rebaseline"] = {"date": date, "decision": DECISION,
                             "candidacy": CANDIDACY,
                             "supersedes_valid_from": old["valid_from"]}
    out = dict(baseline)
    out["items"] = dict(baseline["items"])
    out["items"][iid] = new_rec
    out["rebaselines"] = list(baseline.get("rebaselines", [])) + [
        {"item": iid, "date": date, "decision": DECISION}]
    return out


def qualify(m, item, api_key, rows_dir, date, old_rec,
            reference_echo=None):
    """Two same-day single-item runs; returns the new item record or
    raises MonitorError with the failed gate named. reference_echo
    (the baseline file's recorded model_id_echo) arms the tripwire
    from the first request: a served-id change halts before any
    reference is written."""
    mid = m["model"]
    iid = item["id"]
    arm = m["arms"][0]
    os.makedirs(rows_dir, exist_ok=True)
    rows_path = os.path.join(
        rows_dir, "rebaseline_{}_{}_{}.jsonl".format(mid, iid, date))
    run_ids = {}
    with open(rows_path, "a", encoding="utf-8") as fh:
        run_ids["run1"] = mon.now_iso()
        run1 = mon.run_bank(m, arm, [item], mon.K_SAMPLES, api_key,
                            run_ids["run1"], fh, "rebaseline_run1",
                            reference_echo=reference_echo)
        if run1["echo_change"]:
            raise mon.EchoChange(run1["echo_change"])
        mon.check_parse_collapse(run1, [item], mid, "run1")
        run_ids["run2"] = mon.now_iso()
        run2 = mon.run_bank(m, arm, [item], mon.K_SAMPLES, api_key,
                            run_ids["run2"], fh, "rebaseline_run2",
                            reference_echo=run1["reference"])
        if run2["echo_change"]:
            raise mon.EchoChange(run2["echo_change"])
        mon.check_parse_collapse(run2, [item], mid, "run2")

    c1, c2 = run1["counts"][iid], run2["counts"][iid]
    seed1 = mon.item_seed(mid, iid, "rebl:%s" % date)
    p95_1, p99_1 = mon.smoothed_bands(c1, seed1)
    obs = mon.observed_tvd(c1, c2)
    if obs > p99_1:
        raise mon.MonitorError(
            "run-pair gate failed: TVD(run1, run2) = %.3f above run1 "
            "p99 %.3f; the state is not stable across same-day runs "
            "and nothing was written" % (obs, p99_1))

    pooled = dict(c1)
    for o, n in c2.items():
        pooled[o] = pooled.get(o, 0) + n
    old_base = old_rec["baseline_counts"]
    dist_old = mon.observed_tvd(pooled, old_base)
    if dist_old <= old_rec["band"]["p99"]:
        raise mon.MonitorError(
            "distinctness gate failed: new pooled reference sits %.3f "
            "from the old reference, inside its p99 band %.3f; the "
            "premise of a re-baseline is a distinct state, nothing "
            "was written" % (dist_old, old_rec["band"]["p99"]))

    band_seed = mon.item_seed(mid, iid, "rebl-band:%s" % date)
    p95, p99 = mon.smoothed_bands(pooled, band_seed)
    return {
        "class": "alarm",
        "runs": {"run1": dict(c1), "run2": dict(c2)},
        "unparsed": {"run1": run1["unparsed"].get(iid, 0),
                     "run2": run2["unparsed"].get(iid, 0)},
        "qualification": {"seed": seed1, "p95": p95_1, "p99": p99_1,
                          "observed_run_pair_tvd": obs,
                          "third_run": None},
        "baseline_counts": pooled,
        "n": sum(pooled.values()),
        "band": {"seed": band_seed, "p95": p95, "p99": p99},
        "run_ids": run_ids,
        "model_id_echo": run1["reference"],
        "rows": os.path.relpath(rows_path, REPO).replace(os.sep, "/"),
        "distance_from_superseded": dist_old,
    }


def main():
    ap = argparse.ArgumentParser(
        description="Re-baseline one item onto its current state, "
                    "preserving the old reference (see docstring).")
    ap.add_argument("--model", required=True)
    ap.add_argument("--item", required=True)
    args = ap.parse_args()

    roster = mon.load_roster(mon.ROSTER_PATH)
    models = mon.select_models(roster, args.model)
    m = models[0]
    mon.validate_monitor_model(m)
    item = next((i for i in mon.ITEMS if i["id"] == args.item), None)
    if item is None:
        raise SystemExit("unknown item id: %s" % args.item)
    keys = mon.read_keys(models)

    path = mon.baseline_path(m["model"])
    with open(path, encoding="utf-8") as f:
        baseline = json.load(f)
    old_rec = baseline["items"].get(args.item)
    if old_rec is None:
        raise SystemExit("item %s not in baseline file" % args.item)
    date = mon.local_date()
    if any(s.get("valid_through") == date
           for s in old_rec.get("superseded", [])):
        raise SystemExit(
            "a superseded entry for %s already exists; refusing a "
            "same-day double run" % date)

    new_rec = qualify(m, item, keys[m["provider"]], mon.ROWS_DIR, date,
                      old_rec,
                      reference_echo=baseline.get("model_id_echo"))
    updated = supersede_item(baseline, args.item, new_rec, date)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(updated, f, indent=2)
        f.write("\n")

    print("re-baselined %s / %s effective %s (probes from the next "
          "day score against the new reference)" % (
              m["model"], args.item, date))
    print("  new reference %s  n=%d  band p99 %.2f" % (
        new_rec["baseline_counts"], new_rec["n"],
        new_rec["band"]["p99"]))
    print("  distance from superseded reference %.3f (its band %.2f)"
          % (new_rec["distance_from_superseded"],
             old_rec["band"]["p99"]))
    print("  superseded reference preserved; return watch: "
          "python probe/scripts/return_watch.py")
    print("  inspect the diff of %s, then commit per %s" % (
        os.path.relpath(path, REPO), DECISION))


if __name__ == "__main__":
    main()
