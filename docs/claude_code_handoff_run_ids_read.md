# Code handoff: analyzer --run-ids multi-run read (post-lock Deviation)

Context: the faithful real runs (2026-07-22, post prereg-lock) span four
run_ids by the recovery convention recorded in
docs/baseline_run_note_2026-07-19.md: Haiku one run, Sonnet one run, Opus
derivable from an aborted run plus equipoise from a top-up. The analyzer's
existing single-run guard (main(): multiple run_ids present and no --run-id
given -> exit 2) is a correct safety rail against accidental pooling, but it
cannot express a deliberate, documented multi-run read. This adds an explicit
allow-list so the human affirms exactly which runs to read. This is a
post-lock change: it is recorded as a Deviation in PRE_REGISTRATION_FAITHFUL.md.
It changes NO computation, threshold, stratum rule, or output number.

## Scope

1. Add a CLI argument --run-ids (plural): a comma-separated allow-list of
   run_id prefixes. Mutually exclusive with --run-id (error if both given).
2. Guard behavior with --run-ids present:
   - Load rows, then keep only rows whose run_id starts with one of the
     listed prefixes; drop the rest before any analysis.
   - After filtering, if any run_id remains that is not matched by some
     prefix, that is impossible by construction; assert the filtered set's
     run_ids are all covered and error otherwise.
   - The multiple-run_ids-present-and-no-run-id guard does NOT fire when
     --run-ids is given, because the human has explicitly affirmed the set.
   - Prefix match (startswith), same convention the recovery read uses, so a
     19-char timestamp prefix selects the full run_id.
3. --run-id (singular) behavior is unchanged. Absent both flags with multiple
   run_ids present: unchanged (still exit 2).
4. No other change. Do not touch any threshold, the mixture, the strata, the
   read rule table, the bootstrap, or the faithful/generalized analysis
   bodies. The pinned constants stay byte-identical.

## Note on the Opus dual-run read

Two orphan equipoise query rows exist under the aborted Opus run
2026-07-22T23:09:47 (two probes fired before the credit-balance abort). The
read rule reads Opus equipoise from the top-up 2026-07-22T23:39:51 only.
--run-ids by prefix alone would readmit those two orphans. Handle this the
way the read rule states, per-model-cell, NOT by a blanket run_id filter:
add an optional --faithful-realrun-read flag (or equivalent documented
mechanism) that applies the exact recorded read rule
(Opus derivable <- aborted run, Opus equipoise <- top-up, Haiku and Sonnet
<- their single runs), OR accept a small per-(model,cell)->run_id mapping.
Implement whichever is cleaner; the hard requirement is that the analyzed
Opus set is 80 derivable query rows from the aborted run and 80 equipoise
query rows from the top-up, zero orphans, and that the mechanism is explicit
and testable rather than a hand-filtered input file. State in your report
which mechanism you chose.

## Test (TDD, extend tests/)

test_run_ids_read.py, running the real analyzer against the real files:
1. --run-id and --run-ids together: error.
2. --run-ids with the four faithful real-run prefixes plus the read-rule
   mechanism yields exactly 80+80 Opus query rows (0 orphans), 160 Haiku,
   160 Sonnet; the multi-run guard does not fire.
3. A --run-ids list that omits a present run_id filters those rows out (row
   count drops), never pools them.
4. Existing suite green; the single-run and no-flag guard paths unchanged
   (assert exit 2 still fires on multiple runs with neither flag).

## Hard constraints

- No pinned constant, threshold, equation, or output number changes.
- The single-run guard and the no-flag exit-2 path stay intact.
- No em dashes.

## Report back

Which read mechanism you chose; the row counts per model and the Opus
per-cell/run split; test results per assertion; suite status; confirmation
that no pinned value moved (diff touches only main()/argparse and the new
test).
