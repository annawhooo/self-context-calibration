Handoff: continuous drift monitor over the probing harness

Context. probe/ARCHITECTURE.md defines the active-probing layer;
probe/NOISE_FLOOR.md and probe/DRIFT_EVENT_2026-07-31.md characterize
the instrument and its first caught event. This handoff builds the
scheduled monitor on top of the existing convergence collection
machinery. Reuse collect_row, build_request, post_with_retries, the
PROVIDERS table, ITEMS, and the parse path verbatim; the monitor must
not duplicate request shaping. Nothing outside probe/ and
convergence/tests fixtures may change, except one import shim if
needed. models.json is not modified; the monitor carries its own
roster file.

Roster. probe/monitor/roster.json, five models, Arm A, K=10:
claude-haiku-4-5-20251001, claude-sonnet-4-6, gpt-5.6-terra,
gemini-3.6-flash, deepseek-v4-flash. Temperature and reasoning-off
handling exactly as the convergence roster pins them for these ids.
gemini-3.1-pro-preview is excluded: its 250-per-day cap cannot hold a
680-call bank.

Baseline protocol. Command: monitor.py baseline --model <id> (or
--all). Two same-day runs of the bank. Per item: Laplace-smoothed
multinomial simulation (10,000 draws, seed recorded) from run1's
distribution gives p95 and p99 TVD bands; the run-pair observed TVD
is checked against p99. Items inside the band qualify for the alarm
set with run1+run2 pooled as the baseline distribution. Items outside
trigger a same-day third run for those items only, K=10:
- third matches run2, not run1: a drift event straddled calibration;
  baseline is the post-event state (run2+run3), event logged.
- third matches run1: transient; pooled baseline, item qualified.
- matches neither: item classed sentinel, monitored, never a sole
  alarm trigger.
Baselines are written to probe/monitor/baselines/<model>.json
(distributions, bands, item classes, seeds, dates) and are committed
files: a baseline is a qualification record.

Daily probe. Command: monitor.py probe (all roster models, once
daily). One K=10 bank run per model, rows appended under
probe/monitor/rows/ (gitignored). Per item: TVD against baseline,
compared to that item's p99 band. Echo tripwire as in collection: an
id change halts that model's probe and is its own verdict.

Auto-disambiguation. Any alarm-set item over its band fires an
immediate same-day rerun of the breached items only, K=10:
- rerun matches the probe, not the baseline: verdict EVENT, items
  and distances named, re-baseline recommended (never automatic).
- rerun matches the baseline: verdict TRANSIENT, logged, no alarm.
- matches neither: verdict UNSTABLE, item flagged for sentinel
  review.
Sentinel items are reported descriptively in every verdict but never
fire disambiguation.

Verdict log. One line per model per day appended to
probe/monitor/verdicts.jsonl (a committed file; the longitudinal
record is the point). Fields: date, model, model_id_echo, verdict
(CLEAN, EVENT, TRANSIENT, UNSTABLE, ECHO_CHANGE, ERROR), breached
items with observed vs band, sentinel summary, calls made, run ids.
Exit codes: 0 all CLEAN or TRANSIENT; 1 any EVENT, UNSTABLE, or
ECHO_CHANGE; 2 ERROR (credentials, network exhaustion, parse
collapse). stderr carries the human-readable report.

Credentials and environment. Fail-closed exactly as collection:
every required env var read before the first call, a missing one
names itself and issues zero requests. Add monitor.py check-env:
prints SET or MISSING per required key, never values, exit nonzero
on any missing. This exists because scheduled-task environments have
burned us before; the scheduler docs below require running it once.

Scheduling. No scheduler code. Document in probe/monitor/README.md:
a schtasks command creating a daily task under the user's account
(so user env vars resolve), working directory the repo root, plus
the one-time check-env verification and where output lands. Windows
paths throughout; cmd.exe, not PowerShell, in examples.

Costs. Roughly 3,400 calls per day across the five models at K=10.
No budget enforcement in code, but the verdict line records calls
made so spend is auditable from the log.

Tests. No-network fixture tests in the existing style, in
probe/tests/, discovered by pytest from the repo root: smoothed band
computation against hand-computed values; two-run qualification on
fixtures for all three third-run outcomes; alarm firing and
disambiguation on all three rerun outcomes; sentinel never sole
trigger; echo-change verdict; check-env fail-closed naming; verdict
schema and exit codes; roster refusing unknown model ids. The
existing 13 test files pass unmodified.

Deviations. Exhaustive per the standing contract: departures and
additions both, flag semantics included. The probe handoff's
undisclosed flag additions and the analysis handoff's undisclosed
real-data run are the precedents to not repeat: running anything
against live APIs is out of scope for this handoff and belongs to
the operator.
