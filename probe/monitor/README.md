# Drift monitor: operations and scheduling

The monitor itself is probe/monitor/monitor.py (see its docstring for the
method). This file documents how it is operated on Windows. There is no
scheduler code in the monitor; cadence comes from a Windows scheduled
task. All commands below are cmd.exe, run from the repo root:

    cd /d C:\Users\Anna\PycharmProjects\self-context-calibration

Python is not on PATH on this machine; the pinned interpreter is:

    C:\Users\Anna\AppData\Local\Programs\Python\Python311\python.exe

## One-time setup

1. Credentials. The monitor reads one environment variable per provider
   (ANTHROPIC_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY, DEEPSEEK_API_KEY
   for the current roster) and fails closed, issuing zero requests, if any
   is missing. The scheduled task runs under your user account, so the
   variables must be **user-level** environment variables (set via
   `setx NAME "value"` or System Properties), not shell-session exports:
   a schtasks task does not inherit an interactive shell's session
   variables. This verification step exists because scheduled-task
   environments have burned us before.

2. Verify the environment the task will actually see. Required once
   before the task is trusted, from a fresh cmd.exe window (fresh, so it
   holds the same user-level variables the task will resolve):

       C:\Users\Anna\AppData\Local\Programs\Python\Python311\python.exe probe\monitor\monitor.py check-env

   Every key prints SET or MISSING (never values); nonzero exit on any
   missing. Do not create the task until this exits 0.

3. Baselines. Operator-run, never scheduled (two same-day bank runs per
   model, roughly 1,360+ calls per model):

       C:\Users\Anna\AppData\Local\Programs\Python\Python311\python.exe probe\monitor\monitor.py baseline --all

   Baselines land in probe\monitor\baselines\<model>.json and are
   committed: a baseline is a qualification record.

## The daily task

Create (one line; runs under your user account by default, which is what
makes the user-level environment variables resolve; working directory is
forced to the repo root by `cd /d`):

    schtasks /Create /TN "scc-drift-monitor" /SC DAILY /ST 09:00 /TR "cmd /c cd /d C:\Users\Anna\PycharmProjects\self-context-calibration && C:\Users\Anna\AppData\Local\Programs\Python\Python311\python.exe probe\monitor\monitor.py probe >> probe\monitor\rows\probe_task.log 2>&1"

Inspect, run once by hand, and remove:

    schtasks /Query /TN "scc-drift-monitor" /V /FO LIST
    schtasks /Run /TN "scc-drift-monitor"
    schtasks /Delete /TN "scc-drift-monitor" /F

Notes:
- Without /RU the task runs as the creating user with an interactive
  token, i.e. only while you are logged on. That is the intended mode
  here: it is what resolves the user-level environment variables. If you
  later switch to a stored-credential task (`/RU <user> /RP`), re-run
  check-env afterwards; the resolved environment can differ.
- Roughly 3,400 calls per day across the five roster models at K=10. No
  budget enforcement in code; each verdict line records calls made, so
  spend is auditable from the log.

## The preflight task (06:00, alert-only)

check-env verifies variables are set; the August outages showed the
real failure modes pass that test (a set key with exhausted credits,
http 429, Aug 14-16; a set-but-revoked key, http 401, Aug 19-20).
probe\monitor\preflight.py makes one minimal real request per roster
provider through the production request builder and emails on any
failure, three hours before the probe. It never touches monitor.py,
the bands, or any committed record.

    schtasks /Create /TN "scc-drift-preflight" /SC DAILY /ST 06:00 /TR "cmd /c cd /d C:\Users\Anna\PycharmProjects\self-context-calibration && C:\Users\Anna\AppData\Local\Programs\Python\Python311\python.exe probe\monitor\preflight.py --fresh-env >> probe\monitor\rows\preflight_task.log 2>&1"

One-time alert setup (user-level variables, like the API keys):
SCC_ALERT_EMAIL (the address, used as both from and to) and
SCC_ALERT_SMTP_PASS (a Gmail app password, not the account password).
Unset, the preflight still runs and logs; it just cannot email.
Manual check from any shell, stale or fresh:

    C:\Users\Anna\AppData\Local\Programs\Python\Python311\python.exe probe\monitor\preflight.py --fresh-env --no-email

--fresh-env overlays HKCU user environment before checking, so a
window opened before a setx still tells the truth. That flag exists
because key rotation without re-verification is exactly how Aug 19
happened.

## The push task (11:30, verdicts out)

The probe appends verdict lines locally; committing and pushing them
was a manual, batched step, and the published record lagged origin by
days (the Aug 22 non-fast-forward rejection: two days of lines local,
a PR merged remotely in between). probe\scripts\push_verdicts.py is
the scheduled push: it stages exactly verdicts.jsonl and
derived\daily_counts.jsonl and only when each diff is append-only,
commits with a factual tally message, rebases local commits onto
origin/main, and pushes with retries. It refuses to run off main and
never forces; anything else in the tree is never touched. Method,
guards, and exit codes are in its docstring.

    schtasks /Create /TN "scc-drift-push" /SC DAILY /ST 11:30 /TR "cmd /c cd /d C:\Users\Anna\PycharmProjects\self-context-calibration && C:\Users\Anna\AppData\Local\Programs\Python\Python311\python.exe probe\scripts\push_verdicts.py --export >> probe\monitor\rows\push_task.log 2>&1"

11:30 leaves close to an hour after the slowest observed probe finish
(10:39 local, Aug 17). A day whose probe overruns simply pushes the
next day: the script is a no-op when there is nothing new, and it
picks up any commit a failed push left behind.

One-time verification, in order:

1. Credentials. The task pushes over HTTPS with whatever Git
   Credential Manager has stored; in a non-interactive task GCM can
   only reuse, never prompt. Push once by hand from an interactive
   cmd first so the stored credential exists and is current.
2. Run the script by hand once from the repo root:

       C:\Users\Anna\AppData\Local\Programs\Python\Python311\python.exe probe\scripts\push_verdicts.py --export

   Expect either "nothing to push" or a real commit and push; verify
   on origin either way.
3. Create the task, `schtasks /Run /TN "scc-drift-push"` once, and
   check both push_task.log and origin before trusting it.

Notes:
- Automated commit messages are factual tallies ("Verdicts 2026-08-21
  to 2026-08-22: 4 CLEAN, ..."). Narrative milestone commits ("Days 17
  and 18: ...") stay a by-hand act, and the two coexist: whatever was
  already committed by hand, the script just pushes.
- --export regenerates derived\daily_counts.jsonl from rows\ before
  staging (deterministic; export_daily_counts.py). Because the export
  rebuilds the whole file, pruning rows\ would make the regenerated
  file drop published history; the append-only guard catches exactly
  that, leaves the file unstaged with a warning in the log, and the
  verdicts still push alone.

## Where output lands

- probe\monitor\verdicts.jsonl - one verdict line per model per day,
  appended, **committed**: the longitudinal record is the point. Exit
  codes: 0 all CLEAN/TRANSIENT, 1 any EVENT/UNSTABLE/ECHO_CHANGE,
  2 any ERROR.
- probe\monitor\rows\ - raw rows for baselines, daily probes, and
  disambiguation reruns, plus probe_task.log (the task's captured
  stderr report). Gitignored: rows embed full model replies.
- probe\monitor\baselines\<model>.json - committed qualification
  records, written by the baseline command only. Re-baselining after an
  EVENT is recommended by the monitor but never automatic; it is an
  operator decision, made visible in git history because the baseline
  file changes.
