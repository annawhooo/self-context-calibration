# ECHO_CHANGE disposition: the pinned id is now a silent alias

Date: 2026-09-12. Status: DRAFT until merged to main; the merge
adopts the disposition. Companions: ECHO_CHANGE_2026-09-10.md
(the event and the three dispositions it opened),
STEP_CHANGE_DECISION_RULE_2026-09-07.md (the suspended counter),
and REPORTING_COMMITMENT.md.

## The vendor-side check

Operator-run on 2026-09-12 at about 16:11 UTC, from the
credentialed machine, against the monitor's own endpoint
(api.deepseek.com per convergence/providers.py). Three calls;
response bodies committed verbatim in
probe/vendor_evidence/2026-09-12/:

1. GET /models (models.json): the list carries deepseek-flash
   and deepseek-v4-pro. deepseek-v4-flash is absent.
2. POST /chat/completions requesting model deepseek-v4-flash
   (echo_v4flash.json): serves without error and echoes
   "model": "deepseek-flash".
3. The same call requesting deepseek-flash (echo_flash.json):
   echoes deepseek-flash. Both completions carry the identical
   system_fingerprint (aeb56401ca74e127821c4f9126dcb669) on
   adjacent calls, consistent with one serving stack behind both
   names.

One naming slip, recorded: the operator's local copies of these
files carry _2026-09-13 names from the suggested command
template. The response created timestamps (1789229501 and
1789229502) place the check at 2026-09-12; the committed copies
are named by the true date. A docs or changelog check was not
part of this evidence; a published vendor notice, if one is
later found, gets appended as a dated addendum.

## What this settles

The pinned id was not removed. It was silently aliased: a
request for deepseek-v4-flash succeeds and is answered under the
identity deepseek-flash. The v4-pro sibling keeps its name, so
this is a flash-tier rename or replacement, not a vendor-wide
versioning change. The record bounds the cutover: the pinned
echo answered normally through the 2026-09-09 run and diverged
at first contact on 2026-09-10 (probe run 15:02 UTC).

What it does not settle, and the line is kept: whether the
weights, configuration, or serving stack behind the flash tier
changed at the cutover, or only the name. The instrument
measures behavior and identity strings, not intent.

## What this buys the paper

A customer pinning by request id would never see this event:
calls to deepseek-v4-flash keep succeeding. Only the
response-side echo distinguishes the pinned model from whatever
now answers to its name, and the echo tripwire is what converted
a silent reroute into a detected, dated event with a one-day
detection bound. Section 5 gains the guidance in one line: pin
by served identity, not by request string, and record the echo
on every row. Section 3.4 gains its complement: the one
covariate that moved in the record is the identity itself, and
without the echo it would have moved invisibly.

## Disposition, adopted with this merge

Disposition 1 of ECHO_CHANGE_2026-09-10.md, ride to the freeze:

- The arm stays halted. Daily runs keep attempting and recording
  ECHO_CHANGE days; the behavioral record ends 2026-09-09.
- The dlp step-change counter stays suspended at 2 of 5 and is
  expected never to resolve; the freeze reports it as suspended
  by the id change.
- Re-pinning deepseek-flash as a NEW arm is deferred to the
  post-submission amendment window, where it is now well
  defined: the id is listed and serving. One question is flagged
  for that re-pin and deliberately left unanswered today:
  whether the V4-line reasoning-off toggle (thinking type
  disabled) still binds on the new id. The identity checks ran
  default configuration, and the reasoning content they show is
  what defaults would produce; the toggle was not exercised.

## What this does not do

No monitor, baseline, band, or roster change through the freeze.
The daily task keeps running all five arms. The dlp thread's
pre-change escalation stays recorded as sequence, not cause:
nine breach days and then a rename is what happened; why is not
observable from outside the API.
