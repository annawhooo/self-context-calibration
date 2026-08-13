# Code handoff: monitor probe K upgrade, 10 to 30

Context: the scc-drift-monitor scheduled task runs
probe/monitor/monitor.py probe daily at 09:00 ET over a five-model
roster (haiku 4.5, sonnet 4.6, gpt-5.6-terra, gemini-3.6-flash,
deepseek-v4-flash) against committed Aug 2 baselines. Decision
(chat, 2026-08-06): raise probe K from 10 to 30. Rationale: at
K=10 the smoothed simulation bands sit flat near TVD 0.4 and a
breach needs 4 of 10 samples to change category; at K=30 bands
narrow to roughly 0.267 to 0.30, single-day power on an f=0.3
mass shift rises from about 0.15 to 0.60-0.72, null false-alarm
rate stays near zero, and spend rises from about $20 to $60 per
month (approved). No re-baseline: bands recompute offline from
the committed baseline_counts, preserving the Aug 2 reference
that the current oscillation record depends on.

Sequencing is the hard part. The constant bump and the band
recompute must land together, in one commit, before the next
scheduled run at 09:00 ET on 2026-08-07. A K=30 probe against
k=10 bands silently loses sensitivity; a K=10 probe against k=30
bands inflates false alarms. If the work cannot land before the
run, land nothing and let tomorrow run at K=10.

## Scope

1. In probe/monitor/monitor.py set K_SAMPLES = 30. Grep the file
   and probe/monitor/README.md for any other literal 10 that
   means K (docstring says "K=10" in the probe and baseline
   command descriptions; update those mentions to K=30). SIMS,
   SMOOTH, SEED_BASE, seed_rule stay untouched.
2. New script probe/scripts/recompute_bands.py taking --k (int,
   required). For each file in probe/monitor/baselines/*.json,
   for each item record: recompute
   (p95, p99) = smoothed_bands(baseline_counts,
                               rec["band"]["seed"], k=args.k)
   using the stored band seed verbatim, and overwrite only
   rec["band"]["p95"] and rec["band"]["p99"]. Add
   rec["band"]["k"] = args.k so the file is self-describing.
   Write with json.dump(indent=2) plus a trailing newline,
   matching baseline_one's format.
3. The top-level "k": 10 in each baseline file describes the
   Aug 2 qualification runs and STAYS 10. The qualification
   block per item (bands, TVDs, third-run records) is the
   frozen Aug 2 record and must not be recomputed or touched.
   Same for runs, unparsed, events, counts, run_ids, and every
   other field.

4. Run the recompute with --k 30. Verify determinism: run it a
   second time and confirm the files are byte-identical to the
   first pass.
5. Sanity gates on the recomputed bands, all five files:
   every new p99 <= its old p99; every new p99 in [0.20, 0.35];
   every band dict now carries "k": 30. If any gate fails, stop
   and report; do not adjust anything.
6. Run the existing test suites (probe/tests and tests). Zero
   regressions. If a test pins band values or K=10 behavior,
   report it; do not edit a test to pass without flagging.
7. One commit: monitor.py, README.md if touched, the new
   script, and the five recomputed baseline files. Use the
   _commit_msg.txt + _do_commit.bat helper pattern from cmd,
   stage the listed files explicitly by path, verify with
   git status --porcelain=v1 and git log --oneline, delete the
   helpers after.

## Hard constraints

- probe/monitor/verdicts.jsonl currently has uncommitted lines
  (days 3 through 6). Out of scope. Do not stage it. Stage
  files by explicit path, never git add -A or git add .
- Frozen dated records stay frozen: NOISE_FLOOR.md, the
  DRIFT_EVENT files, CELL_CONCENTRATION_2026-08-06.md. The
  CELL_CONCENTRATION note says "at K=10"; that is correct for
  its window and must not be edited.
- k=30 exact. sims=10000, smooth=1.0, stored seeds verbatim.
  No tuning, no new constants beyond the --k argument.
- No em dashes anywhere. 76-character wrap in Markdown and
  docstrings.
- Show every file edit for review before applying it.
- If anything in this brief conflicts with what the repo
  actually contains, stop and report rather than adapt.

## Expected band shift for orientation (not a gate)

Chat-side analysis with ad hoc seeds, so per-item values will
differ slightly under the stored seeds:

    baseline shape        k=10       k=30
    unanimous 20-0        0.400      0.267
    mixed (12/8 etc.)     0.40-0.45  0.267-0.30

The [0.20, 0.35] gate in scope item 5 is the binding check.

## Report back

Constant and docstring locations changed; per-model summary of
band changes (item count, old and new p99 ranges); determinism
check result; sanity gate results; test suite status; the
commit hash; confirmation the commit landed before 09:00 ET
2026-08-07 or that nothing was landed; any deviation considered
(should be none).
