# INTERCEPT submission form: the three short sections

Drafted 2026-09-28 against the CFP as fetched the same day
(aarm.dev/intercept/call-for-papers: submissions close October 1,
2026; notification by October 31; IEEE conference format via the
Overleaf template, PDF under 4 MB; review is blind, no author or
company name anywhere in the paper; tracks Builders, Breakers,
Defenders; the form asks for core topics, key takeaways, and why
it matters and who it is for). Track: Defenders. Nothing below
names the author, an employer, or the repository.

## Core topics

Continuous behavioral monitoring of production LLM APIs as a
runtime security control. Reversible day-scale regime oscillation
in served judgment behavior, with exact recurrence of prior answer
distributions on pinned model ids. Boundary-item instrumentation:
a stratified judgment bank of designed-equipoise and decisive
items, and an 11,057 slot-day zero-breach null on the decisive
class. False-alarm calibration by exact enumeration rather than
band percentiles, and the measured failure of square-root-K
scaling on between-day variance. The detection versus attribution
ceiling of customer-side monitoring, demonstrated when the one
covariate that moved was the model identity string itself.

## Key takeaways

A snapshot evaluation certifies the day it ran, not the period it
is cited for. Judgment calls drift while clear-cut behavior stays
frozen: all 75 breach entries in 56 days landed on contested items,
none on decisive ones. The drift is not a slow slide; it is
discrete states revisited exactly, with dwell from one day to
weeks, so change detectors that require multi-day persistence
discard it by construction. Per-call determinism is not temporal
stability; the most confident-looking vendors were the least
snapshot-auditable. Pin by the identity the API echoes, not by the
request string: a pinned id can be silently aliased with no request
failing. A calibrated monitor costs about 20 USD per month, and its
own honest-failure list (a wrong false-alarm estimate, a declined
upgrade that data later vindicated, floating-point verdict edges,
a baseline that may itself be the anomaly, and 21 model-days lost
to credit, credentials, vendor availability, and network) is the
part most teams will need.

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
