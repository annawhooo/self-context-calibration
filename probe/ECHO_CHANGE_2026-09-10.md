# First ECHO_CHANGE: the deepseek arm's echoed id changed

Date: 2026-09-10. Status: DRAFT until merged to main; the merge
adopts the reporting only. The arm disposition it opens is a
separate operator decision, stated below and not taken here.
Companions: STEP_CHANGE_DECISION_RULE_2026-09-07.md (the dlp
counter this event suspends), CORRECTIONS_2026-09-06.md (the dlp
thread history), and REPORTING_COMMITMENT.md.

## What fired

On the first call of the 2026-09-10 deepseek run (item
vendor_access, probe run id 2026-09-10T15:02:47Z), the API
response echoed the model id "deepseek-flash" against the pinned
reference "deepseek-v4-flash". The echo tripwire halted
collection for the model at one call. No distributions were
sampled under the ambiguous identity, nothing entered the derived
counts, and the day's verdict line records the divergent echo
verbatim. This is the first use of the ECHO_CHANGE verdict in the
record, and it behaved exactly as designed.

## What it means, and what it does not

- The identity covariate moved. Every prior row of the monitor
  record, on all five models, echoed its pinned id exactly; this
  is the first day the string itself changed.
- There is no attribution beyond the string. A rename, an alias
  migration, rerouted serving, or an upstream truncation are
  indistinguishable from outside the API. The record says
  changed; it does not say why, and it does not say what is
  serving now.
- The timing is recorded, not interpreted. The same arm's
  eq_alert_dlp_email_v2 thread had breached on nine days since
  Aug 17, five of them held EVENTs, every excursion D-ward, with
  the thread's deepest readings in the four days immediately
  before the id change. A reader will form the obvious
  hypothesis; this note records only the sequence.

## Effect on the live instruments

- The dlp step-change counter stands at 2 of 5 and is suspended.
  ECHO_CHANGE days produce no probe rows, so under the pinned
  missing-day semantics they are neither home nor away and do not
  reset. The count resumes only if probe days resume under the
  pinned identity. If the pinned echo never returns, the counter
  never resolves, and the freeze reports it as suspended by the
  id change.
- The arm's behavioral record ends at 2026-09-09 unless probes
  resume under the pinned id. Every prior verdict stands
  unchanged.
- No other arm is affected.

## The open operator decision

Three dispositions, none taken in this note:

1. Ride to the freeze. Leave the arm halted; the daily runs keep
   attempting and recording ECHO_CHANGE days; the behavioral
   record ends at Sep 9 with the id change as its terminal event.
   No new code, no new baselines. This is the default state and
   requires no action.
2. Re-pin under the new echo. A new arm on "deepseek-flash" with
   a fresh n=20 baseline and new bands per the original
   qualification procedure, reported as a NEW arm, never as
   continuous with the old one. Sixteen days before the freeze
   bounds what it could say.
3. Vendor-side check first, operator only (this session holds no
   API credentials): whether deepseek-v4-flash is still served,
   whether deepseek-flash is a published alias, and whether the
   vendor posted any notice. The findings feed disposition 1 or
   2 and get recorded in the disposition note.

## Interaction with the paper

Section 3.4's claim is detection without attribution: behavior
moved while every outside-visible covariate held constant. This
event is the claim's complement and its strongest single
exhibit: the first covariate that moved in the whole record is
the identity string itself, and the instrument's response was to
stop measuring rather than mix identities. It is also the first
exercise of the ECHO_CHANGE arm of the verdict grammar (section
2), which had been dormant since design. The freeze report
carries the event, the suspended counter, and whichever
disposition the operator records.
