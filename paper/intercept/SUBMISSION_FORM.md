# INTERCEPT submission form: the three short sections

Drafted 2026-09-28 against the CFP as fetched the same day
(aarm.dev/intercept/call-for-papers: submissions close October 1,
2026; notification by October 31; IEEE conference format via the
Overleaf template, PDF under 4 MB; review is blind, no author or
company name anywhere in the paper; tracks Builders, Breakers,
Defenders; the form asks for core topics, key takeaways, and why
it matters and who it is for, plus a talk format). Track:
Defenders. Nothing below names the author, an employer, or the
repository.

## Operator decisions still open (decide before filling the form)

1. Talk format. The CFP lists a 25 minute case study, a 40 minute
   deep dive, an 8 minute lightning talk, and a live demo. Not
   chosen yet. The paper reads as a case study.
2. Vendor and model names. The CFP as fetched reads: "Strip your
   identity. Review is blind. No author or company name anywhere,
   not the title, the sections, or the paper itself. A paper that
   names an author or company will be deleted." Read literally
   that covers the vendors whose APIs are the subject of
   measurement: the model ids in the body, "Claude" in section
   3.5, "ChatGPT" in a cited title, the two corporate authors and
   vendor URLs in the reference list, and the arm labels drawn
   into the figures. The paper keeps them because the finding is
   about pinned ids. If the organizers say otherwise, the fallback
   is: arm labels (arm 1 to arm 5) in prose and in figdata.SHORT
   with the figures regenerated; the two posts cited by title and
   date only, no corporate author or URL; the chen entry by arXiv
   id only. Ask the organizers before Oct 1.
3. Artifact link and searchability. Reviewers score "code,
   artifacts, or working demonstrations" and cannot check anything
   from a withheld link. The exposure is also wider than the link:
   the paper's title, the abstract's opening sentence, section
   names, figure basenames and labels, and item ids are verbatim
   in the public repository under the author's handle, so a
   reviewer who searches the title de-anonymizes the paper. The
   options are an anonymized mirror (fresh account, scrubbed
   history, day-job names removed per the public-write gate) with
   its link in the paper, or setting the real repository private
   until the 2026-10-31 notification.

## Core topics

Continuous behavioral monitoring of production LLM APIs as a
runtime security control. Exact recurrence of prior answer
distributions on pinned model ids: reversible, day-scale, and on
one thread week-scale. Boundary-item instrumentation: a stratified
judgment bank of designed-equipoise and decisive items, and an
11,057 slot-day zero-breach null on the decisive class. False-alarm
calibration by exact enumeration rather than band percentiles, and
the measured failure of square-root-K scaling on between-day
variance. The detection versus attribution ceiling of customer-side
monitoring, demonstrated when the one covariate that moved was the
model identity string itself.

## Key takeaways

A snapshot evaluation certifies the day it ran, not the period it
is cited for. Judgment calls drift while clear-cut behavior stays
frozen: all 75 breach entries in 56 days landed on contested items,
none on decisive ones. The drift is not a slow slide; it is
discrete states revisited exactly, with dwell from one day to
weeks, so change detectors that require multi-day persistence
discard it by construction. Per-call determinism is not temporal
stability; the models that answer most consistently within a day
were the ones that flipped between days. Pin by the identity the
API echoes, not by the request string: a pinned id can be silently
aliased with no request failing. A calibrated monitor bills about
20 USD per month, and its own honest-failure list (a wrong
false-alarm estimate, a declined upgrade that data later vindicated,
floating-point verdict edges, a baseline that may itself be the
anomaly, and 21 model-days lost to credit, credentials, vendor
availability, and network) is the part most teams will need.

## Why it matters and who it is for

Teams operating agents on frontier APIs inside controlled
processes: security operations, compliance, and ICFR-adjacent
automation, where a control validated last quarter is presumed
valid today and no signal reports the expiration. Vendors of
runtime-security tooling who need a cheap, reproducible observable
for model stability. Anyone writing model-stability language into
contracts: the paper says what a customer can measure
(distribution stability on a pinned bank, dated and reproducible)
and what no customer can (the cause), and argues for specifying
the former. The full instrument, the 56-day append-only record,
the pre-registered decision rules, and every dated correction are
public; the link is supplied on acceptance.

## Decisions taken 2026-09-29

Recorded by the operator in session; each closes the matching item
under "Operator decisions still open" above, which stands as
written.

1. Talk format: 25 minute case study.
2. Vendor and model names: the fallback is applied, without asking
   the organizers. In main.tex the five arms are arm 1 to arm 5 in
   roster order (paper/figures/figdata.py MODELS); the echoed
   identity strings of 2026-09-10 are described, not quoted; the
   two web posts are cited by title and date only, and the chen
   entry by arXiv id only (refs.bib). Figures F1, F2, and F4 are
   regenerated with PAPER_BLIND=1 PAPER_DATA_THROUGH=2026-09-26,
   which writes arm-labeled PDFs to paper/intercept/figures/ and
   leaves paper/figures/out/ untouched. F3 prints no model label
   and is unchanged. The markdown master (paper/INTERCEPT_DRAFT.md)
   keeps the model names; it is the research record, not the
   submission.
3. Artifact link and searchability: the repository is set private
   until the 2026-10-31 notification. No mirror. The link is
   supplied on acceptance, as the last section above already says.

## Submitted 2026-10-01

Submitted by the operator at aarm.dev as Paper #19, status
PENDING REVIEW, locked for review. Track Defenders, 25 minute case
study, the three sections above pasted as written, PDF compiled
from main.tex at commit 2909e27 (blind scrub in session: no
identity string, empty metadata, 0.39 MB, 9 pages). The WCARS
named variant was emailed to the program chair on 2026-09-30 from
commit 957bf27 and the submission confirmed on 2026-10-01. The
repository is private until the 2026-10-31 notification.
