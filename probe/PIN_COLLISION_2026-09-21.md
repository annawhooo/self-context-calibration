# Pin collision on the patch_timing rule: two drafts, one filename

Date: 2026-09-21. Status: DRAFT until merged to main; the merge
adopts this account and the dispositions recorded here. This is a
process note: it changes no rule, no baseline, and no verdict.
Companions: STEP_CHANGE_DECISION_RULE_2026-09-20.md (the adopted
pin), CORRECTIONS_2026-09-21.md (E6, surfaced by the verification
recorded here), REGISTRATION_ATTESTATION_2026-09-21.md (the 09-14
pin question, same verification), and REPORTING_COMMITMENT.md.

## What happened

Two Claude sessions drafted the same decision rule for the same
thread under the same filename, in different registration
positions, and both opened PRs. Timeline; times are git committer
times except the PR close, which is the GitHub API's:

- 2026-09-19: eq_patch_timing on gpt-5.6-terra holds an EVENT
  (probe 6/4/0/0, rerun identical; the verdict line is in the
  committed record).
- 2026-09-20 08:58:55 -0400: commit 2921e01 (PR #20) writes
  probe/STEP_CHANGE_DECISION_RULE_2026-09-20.md and the RULES
  entry (threshold 4, count_from 2026-09-21), before that day's
  09:00 probe.
- 2026-09-20 12:30:04 -0400: the scheduled push commits the
  day's verdicts (7c71fe3).
- 2026-09-20 13:47:58 -0400: commit 3b8faf5 (PR #21, a separate
  session, on branch claude/probe-run-numbers-8oki5d cut from
  7c71fe3) writes a second draft of the same note: same filename,
  same rule parameters, different prose, drafted after reading
  the 09-20 verdicts.
- 2026-09-21 08:36:00 -0400: the operator merges #20 (7ec3c95),
  24 minutes before the first countable probe at 13:00 UTC. No
  post-2026-09-20 probe data existed anywhere at the merge; the
  first post-pin probe began at 13:00 UTC, so the validity
  condition holds by construction, checkable from the run
  timestamps in the record.
- 2026-09-21 13:05:31Z: #21 is closed unmerged.

## Why #20 is the pin

The merge is the pin, and #20's merge satisfied its own validity
condition: adopted before any post-2026-09-20 probe data was read
by operator or assistant. #21 carried identical rule parameters
and a byte-identical step_change_watch.py hunk, so no decision
differed between the drafts; only prose did. Nothing in #21 is
needed by the record: its two facts absent from #20 (the 09-20
probe read 0/10/0/0; 47 observed days through 09-20) recompute
from the committed record, and its "41 consecutive days" home
dwell counts calendar days where the pinned convention counts
observed days (38 observed in 2026-08-09 to 2026-09-18;
2026-08-14 through 16 are absent from the record).

## Disposition of the second draft

Closed unmerged with a comment naming #20 as the pin. The draft
commit is preserved twice, at refs/pull/21/head and at the
annotated tag pr21-draft-3b8faf5. The source branch
claude/probe-run-numbers-8oki5d was then deleted: its tip's only
effect against main was to replace the adopted note, so any
future PR from it would re-carry an add/add conflict on that
file and invite a resolution that rewrites an original. Sessions
branch from origin/main. One name collision is recorded so a
future reader is not misled: the deleted branch re-created the
name PR #19 had merged from on 2026-09-18; #19's merged tip is
untouched and remains reachable at 63cd03a^2 (c157b1f).

## The verification pass

Before #21 was closed, a seven-agent read-only verification ran
over the worktree at 7ec3c95: independent fact-checks of both
drafts against the committed record using the committed watch
arithmetic, a methodology review against the repo's pinning and
correction rules, a merge simulation, and three adversarial
reviewers. Findings and where each one lives:

- One false sentence in the adopted note: E6 in
  CORRECTIONS_2026-09-21.md, with a dated notice on the original.
- The 2026-09-14 pin's registration position (merged 09-18,
  after post-pin data existed):
  REGISTRATION_ATTESTATION_2026-09-21.md.
- Wording in the drafts that the freeze write-up should not
  carry. From the #21 draft: "41 consecutive days" (38
  observed) and "Pinned the afternoon of 2026-09-20" (a draft
  is not a pin). From the adopted note: "roughly 20-minute
  gate" (9.0 minutes by the 09-19 run ids), "twelve plus three"
  (the 08-31 note rejected thirteen and beyond), and "a one-day
  open run" (the run closed HOME on 2026-09-20, before the
  pin).
- Pin dates in the freeze write-up come from git merge times,
  not note titles: the 09-14 note merged 2026-09-18T13:17:23Z,
  the 09-20 note merged 2026-09-21T12:36:00Z (git committer
  times; the GitHub API reports each one second later). The
  title convention "pinned <date>" names the draft date.

## What this does not change

No monitor, baseline, band, roster, or verdict change. The
append-only record was not touched at any point; the collision
lived entirely in drafts and one GitHub branch. The
eq_patch_timing count starts, as pinned, with the 2026-09-21
probe, which no one had read when this note was written.
