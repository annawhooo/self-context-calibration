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
- Wording, sentences, and decisions the operator chose in a session
  are not removed, reworded, or reverted by a later edit (a trim, a
  fluency pass, a rewrite) without telling her first, in the same
  message, before the change is made. Before proposing any edit to
  text she has already reviewed, diff the proposal against the
  record of her choices and list every one it would touch. Added
  2026-09-30 after a trim silently undid five approved abstract
  edits.
- Any prose drafted for the operator (paper text, dated notes,
  cover emails, abstracts, form answers) passes this checklist
  before it is shown to her, and the draft says what the checklist
  changed: no garden-path openers; no term of art before the
  reader has its definition; no elided object ("produced none");
  every verb carries its complement ("held constant"); a contrast
  takes its conjunction; one thought is one sentence, joined with
  "and", a colon, or "so", not chopped into staccato pieces; a
  negation may stand alone before its payoff; every claim scoped
  to the check actually run; the number the reader will ask about
  is in the sentence, with its unit; formal salutation on a first
  professional send; contractions kept mid-sentence, expanded at a
  sentence start. Added 2026-09-30 after the operator had to catch
  the same patterns in a cover email that she had already caught
  in the paper.
