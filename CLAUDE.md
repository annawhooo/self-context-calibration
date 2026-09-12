# Operating rules for this repository

This repo is a live research record: a daily drift monitor over
five LLM APIs (probe/), the completed calibration and convergence
studies (convergence/, docs/), and an in-progress paper (paper/).
The rules below are not style preferences; they are the
methodology, and when a rule conflicts with convenience the rule
wins. The operator is Anna Hix. Her merge to main is the act of
adoption for every decision.

## Verify, never recall

- Any statement about the status of a PR, branch, merge, or prior
  decision must come from a fresh fetch or API call in the same
  turn it is made. If it cannot be verified right now, label it
  unverified. Working memory is not a source; this rule exists
  because memory-sourced claims have been wrong in this project
  (probe/CORRECTIONS_2026-09-06.md, E4).
- Any number in a note, report, or paper section must be computed
  by a committed script or by a script run shown in the session,
  never estimated or recalled. Paper numbers additionally require
  a committed script behind them (the numbers policy in
  paper/INTERCEPT_DRAFT.md).

## The record is append-only and pre-registered

- probe/monitor/verdicts.jsonl and
  probe/monitor/derived/daily_counts.jsonl are append-only. Never
  rewrite, reorder, or prune them.
- The monitor code is byte-constant through the 2026-09-26 data
  freeze. No change to verdicts, bands, baselines, K, seeds, or
  the alarm set without a dated decision note merged by the
  operator.
- Decision rules are pinned BEFORE their deciding data, and data
  read before a pin never counts toward that rule. Dated notes are
  DRAFT until merged to main; the merge is the pin. Some pins
  carry validity conditions (merge before post-date data is read),
  so check open PRs for pending pins before decoding new probe
  days.
- Analysis-side scripts (probe/scripts/step_change_watch.py,
  probe/scripts/return_watch.py) print; they never decide.
  Decisions live in dated notes.

## Corrections

Originals stand unedited. A factual error in a committed note
gets a dated notice header on the original pointing to the
correction, plus an entry in a dated CORRECTIONS file citing the
log evidence. Follow probe/CORRECTIONS_2026-08-30.md and
probe/CORRECTIONS_2026-09-06.md.

## Conventions

- Dated notes: 76-character wrap, no em dashes, dated filenames,
  companion notes listed in the header, recorded per
  probe/REPORTING_COMMITMENT.md.
- Run every file in probe/tests/ and confirm green before pushing
  any change under probe/scripts/ or probe/monitor/.
- Claude sessions never merge PRs in this repo unless the operator
  explicitly asks in the session, and never force-push.
