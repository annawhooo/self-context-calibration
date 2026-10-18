# Registration attestation for the 2026-10-18 wait rule

Date: 2026-10-18. Status: DRAFT until merged to main; the merge is the
operator's adoption of the extension marked as such below. Precedent:
REGISTRATION_ATTESTATION_2026-09-21.md. Companions:
STEP_CHANGE_DECISION_RULE_2026-10-18.md (the pin in question),
RULINGS_2026-09-21.md (Ruling 4, the tally convention), and
REPORTING_COMMITMENT.md.

## The question

STEP_CHANGE_DECISION_RULE_2026-10-18.md is valid only if merged before
any 2026-10-17 or later probe data is read by operator or assistant.
The 2026-10-17 verdicts commit (01e6e92) reached origin/main at
2026-10-17T12:30:06-04:00, and the 2026-10-18 probe runs before this
note can be merged. As in the precedent, the condition turns on
reading, not existence. This note records what was and was not read,
and how each statement can be checked.

## The attestation

Layers, stated separately so each can be weighed:

1. The operator attests, in the 2026-10-18 session: she reads the
   monitor record only through Claude sessions and does not open the
   record files otherwise. She has read no 2026-10-17 or later probe
   data.
2. Extension, drafted by the assistant and adopted by this merge:
   layer 1 covers probe data in any form, including verdict lines,
   derived daily counts, row files, scheduled-task logs, analysis
   script output, and the repository's pages on GitHub.
3. Transcript scan, run on 2026-10-18 in the drafting session. A
   script read every local Claude Code transcript modified since
   2026-10-16 (68 files across all of the operator's projects) and
   listed each tool call at or after 2026-10-17T16:30:00Z whose input
   names a record file, a watch script, a git log or show, or a pull
   request. The script printed tool inputs only, never the tool outputs.
   One session matched: the drafting session itself, with 8 calls.
   Each of the 8 is a git log printing commit hashes and timestamps
   only, a read of daily counts filtered to dates through 2026-10-15,
   or a file write. The only other repository session active since
   2026-10-16 ended at 2026-10-16T16:16:45Z, before the 2026-10-17
   data existed.
4. The working tree. The drafting session's branch was cut from
   origin/main at 5373dae, which predates 01e6e92; 01e6e92 is not an
   ancestor of the branch head. The branch's verdicts.jsonl and
   daily_counts.jsonl hold zero lines dated 2026-10-17. The 2026-10-17
   data reached the local object store through git fetch and was never
   checked out or printed.
5. What the drafting session did see. On 2026-10-16 a git log printed
   the opening characters of the 2026-10-16 commit subject: "Verdicts
   2026-10-16: 2 CLE". On 2026-10-18 a git log printed the hash and
   timestamp of 01e6e92 and no subject. Under Ruling 4 a commit tally
   is metadata, and 2026-10-16 counts toward nothing in the pin.

## Limits, stated so the grade is honest

The scan covers local Claude Code transcripts only. The scan cannot see
cloud sessions, claude.ai chats, GitHub web views, or email
notifications, and layer 1 alone covers those. Windows last-access
timestamps are disabled on the operator's machine (fsutil reports
DisableLastAccess = 2), so file metadata cannot corroborate any layer.
A Claude Code session opened in this repository receives recent commit
subjects, which carry verdict tallies, in its starting context; a
session opened before this merge would see the 2026-10-17 and
2026-10-18 tallies, which Ruling 4 treats as metadata.

Grade: contemporaneous, written before the merge it supports, with
layers 3 and 4 checkable by command. That is stronger than the
retrospective 2026-09-21 attestation and weaker than a pin that is
clean by construction.

## Consequence

If this note and the wait rule merge together, the wait rule stands
and counts from 2026-10-17. If the operator cannot adopt the extension
in layer 2, neither note is merged, the wait rule is void under its own
condition, and the rule is redrafted counting from the first probe
after the redraft's merge.
