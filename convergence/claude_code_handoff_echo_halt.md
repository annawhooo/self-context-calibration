Handoff: enforce the echo-change halt rule in the collection runner

Context. The pre-registration (Roster, preview-id mitigations) commits
to a tripwire: the model id echoed in each response is recorded per
row, and if the echoed id changes mid-collection, collection halts for
that model and completed rows form their own cell. The runner records
model_id_exact per row but does not act on it; the rule is currently
enforced by post-hoc checks only. gemini-3.1-pro-preview collection is
now split across daily quota windows, which is the live case the rule
exists for. models.json and the pre-registration are locked under
prereg-lock-convergence-2026-07-24. Nothing outside convergence/ may
change.

Behavior. During collection runs only (not --verify-reasoning, not
--probe-sampling), the runner maintains a reference echo id per model
and halts on divergence.

Reference. Before the first call for a model, read the existing --out
file. If prior rows for that model carry exactly one distinct
model_id_exact, that is the reference; this makes the rule span
resumed runs, which is the scenario in production now. If prior rows
carry more than one distinct echo, refuse to start collection for
that model and exit nonzero naming the ids found: the data is already
split and needs human partitioning before more rows land. If no prior
rows exist, the first response of this run sets the reference.

Halt. When a response echoes an id different from the reference: write
that row exactly as normal, durable append, so the divergent response
remains evidence, then immediately stop issuing calls for that model,
print a report naming the model, the reference id, the divergent id,
and the row counts on each side, continue with any remaining models in
the run, and exit nonzero at the end. Analysis partitions rows by
model_id_exact, so the written divergent row lands in its own cell per
the pre-registered rule, not in the reference cell.

Missing echo. A response with no parseable model id echo does not
trigger the halt, absence is not change, but it is counted and
reported per model at the end of the run, and it never sets or
updates the reference.

No flag. The check is always on for collection. It enforces a
pre-registered control, so it is not optional behavior.

Tests. No-network fixture tests in the existing style, added to
convergence/tests/: reference taken from a prior-rows fixture file;
refuse-to-start on a pre-split fixture naming both ids; mid-run halt
writes the divergent row then stops that model and continues others;
missing echo counted, not halted, reference unchanged; exit codes for
clean, halted, and refuse-to-start runs; resume-spanning reference,
prior file plus new run. Existing 11 test files pass unmodified.

Deviations. Any departure from this spec is listed in the handoff
report, and so is any addition beyond it, flag semantics included; the
probe handoff's undisclosed flag-exclusion choice is the precedent to
not repeat.
