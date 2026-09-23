# Registration attestation for the 2026-09-14 disclosure pin

Date: 2026-09-21. Status: DRAFT until merged to main; the merge
is the operator's adoption of the extensions marked as such
below. Precedent for recording registration position after the
fact: STEP_CHANGE_DECISION_RULE_2026-08-16.md ("Registration
status, stated plainly"). Companions:
STEP_CHANGE_DECISION_RULE_2026-09-14.md (the pin in question),
PIN_COLLISION_2026-09-21.md (the verification that raised this),
RULINGS_2026-09-21.md (Ruling 4, the tally convention this note
leans on), and REPORTING_COMMITMENT.md.

## The question

STEP_CHANGE_DECISION_RULE_2026-09-14.md carries the validity
condition "merged before any post-2026-09-14 probe data is read
by operator or assistant; otherwise it is void and gets
redrafted with a later start date." Its note and RULES entry
were committed 2026-09-14T17:50:08Z (c157b1f), before any
post-pin probe ran; the text never changed afterward. The merge
that adopted it (PR #19, merge commit 63cd03a) landed
2026-09-18T13:17:23Z (git committer time; the GitHub API reports
one second later). By then the 2026-09-15, 09-16, and 09-17
verdicts commits were on origin/main, and the 2026-09-18 probe
had been running for 17 minutes (13:00 UTC start; its verdicts
reached origin at 16:30 UTC, after the merge). The condition
therefore turns on reading, not existence: data read before a
pin never counts toward it, and data merely on disk leaves the
rule blind to it. This is the 08-16 situation, with one
difference stated at the end.

## The attestation

Layers, stated separately so each can be weighed:

1. The operator attests, in the 2026-09-21 session: she read no
   2026-09-15, 09-16, or 09-17 verdict data before the #19
   merge.
2. Extension, drafted by the assistant and adopted by this
   merge: layer 1 extends to post-2026-09-14 probe data of any
   form read before the merge, including: verdict lines,
   derived daily counts, row files, scheduled-task logs
   (probe_task.log carries the daily per-model verdict reports,
   with per-item detail for any breached item), and
   analysis-script output. A step_change_watch.py or
   return_watch.py run in the window would have printed
   post-pin rows for the threads then in RULES; the extension
   covers such runs too.
3. The present assistant session first read post-2026-09-14
   verdict content on 2026-09-20, after the merge. Checkable in
   the session transcript, which is not committed; stated here
   so it is on the record.
4. Other sessions, and the direction of the discipline. The
   operator reports that the discipline ran from assistant to
   operator, not the reverse: a Claude Code session (undated in
   her account) instructed her not to read anything yet, on
   preregistration-integrity grounds. Extension,
   adopted by this merge: so far as she directed or can
   determine, no session she ran between the pin commit and the
   merge read the monitor record.

The 09-18 sliver is narrower than it looks. The governed item's
own 09-18 observation did not exist at merge time:
gpt-5.6-terra's probe run began 13:22:49Z, five and a half
minutes after the merge, per the run_ids in its verdict line.
Only the haiku (13:00:01Z) and sonnet (13:08:27Z) partial rows
existed pre-merge, and layer 2 covers them.

Commit-subject exposure is handled separately, because no layer
above can honestly cover it: the 09-15 through 09-17 tally
subjects were visible on the repository while the operator
merged #19, and she is not asked to attest that she never saw
them. Under Ruling 4 they are metadata and the pin stands. For
a reader who rejects Ruling 4, the honest statement is a bound,
not a denial: the visible subjects determine the governed item
HOME on 09-15 and 09-16 and bound its away count at one on
09-17 (the arithmetic is in the ruling), so candidacy at
threshold three was unreachable on pre-merge information. The
residual channel is selective adoption, the option not to merge
had the subjects looked bad, never outcome knowledge.

None of the layers can be proven from the record alone. They
are recorded so the rule's evidential weight can be judged
honestly. One difference from the precedent, stated so the
freeze write-up does not equate two grades: the 08-16
attestation was contemporaneous with adoption, committed to
main the same day (dcdd15c). This one is retrospective,
recorded 2026-09-21 about conduct on 2026-09-15 to 18, in a
repo whose verify-never-recall rule exists because
memory-sourced claims have been wrong. Weight it below the
08-16 statement accordingly. Grades: the 08-31 pins are clean
by construction; this pin is blind by attestation; the 09-20
pin is clean by construction against its own condition
(PIN_COLLISION_2026-09-21.md).

## Consequence

The 2026-09-14 pin stands. eq_disclosure_timing counting from
2026-09-15 continues under the committed watch; no count state
is asserted here. Against a reader who treats day-level commit
tallies as probe data, the pin's defense is Ruling 4 first and
the exposure bound above failing that. If the operator cannot
adopt the extensions in layers 2 and 4, this note is not
merged, the pin is void under its own condition, and the rule
is redrafted counting from the first probe after the redraft's
merge.
