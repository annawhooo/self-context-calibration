# Repository visibility: public again during INTERCEPT review

Date: 2026-10-27. Status: DRAFT until merged; the merge adopts the
decision. Recorded under probe/REPORTING_COMMITMENT.md so the change
to the artifact link sits beside the submission record. Companions:
paper/intercept/SUBMISSION_FORM.md, whose item 3 and "Submitted
2026-10-01" section the present note supersedes on visibility only;
and paper/intercept/review/VERIFICATION_2026-09-28.md, where the
searchability question was first raised.

## The decision

The operator set the repository annawhooo/self-context-calibration
back to public on 2026-10-27, and the repository stays public through
INTERCEPT review. The paper is unchanged. The submitted PDF names no
author and no company, and the call for papers states no other
anonymity rule.

## What the record shows

On 2026-09-28 the verification pass left "the searchability of the
title and section names in the public repository" to the operator
(VERIFICATION_2026-09-28.md). SUBMISSION_FORM.md item 3 gave two
options: an anonymized mirror, or setting the real repository private
until the 2026-10-31 notification. Commit fa9b986 on 2026-09-29
applied the second option as the blind-review fallback, and the
"Submitted 2026-10-01" section records the repository as private
until the 2026-10-31 notification. The record does not hold the time
of the switch to private.

Item 3 presented the two options as the ways to protect the blind
review. A third option, leaving the repository public, was not
listed, although the call never required more than an anonymous
paper. The two-option framing came from the drafting session, not
from the call.

## Checks run on 2026-10-27

- `gh repo view annawhooo/self-context-calibration --json
  visibility,isPrivate` returned PRIVATE in a session turn that began
  at 18:40 EDT, and PUBLIC in a session turn that began at 18:48 EDT,
  after the operator made the change.
- The call for papers at aarm.dev/intercept/call-for-papers, fetched
  the same evening, states: "Review is blind. No author or company
  name anywhere — not the title, the sections, or the paper itself."
  The page states no rule on preprints, arXiv, or public code and
  artifact repositories, and lists code and artifacts only as a
  strength reviewers reward.
- The same page now gives a submission close of December 31, 2026,
  blind review in January 2027, and decisions "By late January 2027."
  The call fetched on 2026-09-28 gave a close of October 1, 2026 and
  notification by October 31. Whether Paper #19, submitted on
  2026-10-01, keeps the October 31 notification is unverified.

## What the change exposes

The paper's title, the abstract's opening sentence, section names,
figure basenames, and item ids appear verbatim in the public
repository under the operator's handle (SUBMISSION_FORM.md item 3). A
reviewer who searches the title can identify the author. If decisions
arrive in late January 2027, the exposure runs through late January
instead of ending on October 31. The operator accepts that exposure in
exchange for a working public link in other submissions and
correspondence.

## What this note does not do

The note changes no part of the submitted paper, the submission form
fields, the monitor, the verdict log, or any pin. The original
SUBMISSION_FORM.md stands unedited.
