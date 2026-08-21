# Research and Open Source Summary, March through August 2026

Anna Hix. Compiled 2026-08-21 as source material for resume and bio updates.
Every claim below traces to a public repo, a commit, a DOI, or a merged PR.
Nothing here is aspirational. Where a submission is pending, it says pending.

## The arc in one paragraph

Since March I have run one research program with three strands: security
architecture for autonomous AI agents, the fidelity of agent reasoning to agent
output, and empirical measurement of served-model behavior. The program is not a
pile of disconnected repos. Each artifact feeds the next: building a credential
vault (Coffer) exposed a detection gap; the gap produced a paper and an open
catalog (Biomimetic Gap Analysis, Defense Catalog); the paper's design
principles became running detection code (Motion Detector, mcp-detect); the
detection work needed audit infrastructure (mcp-tap) and upstream fixes to an
agent firewall (Pipelock); and the question of whether the model under an agent
can be trusted at all became a pre-registered measurement program
(self-context-calibration) with a live drift monitor and a conference submission
in preparation.

## Projects

### Coffer MCP: credential vault for LLM agents
`github.com/annawhooo/coffer-mcp` | Python | March 2026 to present | 95 commits, v0.1.0

The problem: a credential pasted to an AI assistant lives in context, history,
and logs. Coffer stores credentials AES-256-GCM encrypted on the user's machine
and exposes MCP tools that let the agent use a credential without ever seeing
it. The agent gets the response; the secret goes vault-to-target.

- MCP tool surface: alias listing, authenticated HTTP, credential testing,
  website login with session caching, OAuth2, command execution.
- Security posture: fail-closed URL allowlists (default deny), credential
  expiry, HMAC tamper-evident audit log, a credential_guard that rejects
  secret-shaped values arriving in tool parameters, secure-memory handling,
  rate limiting.
- Engineering discipline: 417 test functions, CI, a mutation-testing
  configuration, a written threat model, and a security policy.

### Biomimetic Gap Analysis: the paper
`github.com/annawhooo/biomimetic-gap-analysis` | April 2026 | with Shaun Milligan
DOI 10.5281/zenodo.19411502 (v2); 10.5281/zenodo.19393455 (v1)

Immune systems are the largest dataset of solved adversarial detection problems
on earth. The paper decomposes immune mechanisms across six biological kingdoms
into abstract structural patterns and maps them against how we secure AI agents
today. Three versions shipped in April (v1, v2, v2.1).

- 36 cross-domain mappings, 35 risk-prioritized design principles, 19
  biologically derived attack scenarios with paired mitigations, 8 immune
  failure modes with safeguards, 170 references.
- Feasibility assessment against MCP and LangChain: 14 of 19 attack scenarios
  (74%) graded trivially or feasibly exploitable using documented framework
  behaviors.
- Compliance mappings to NIST CSF 2.0, OWASP LLM Top 10 (2025), and MITRE
  ATT&CK, including scenarios that extend beyond current ATT&CK coverage.

### Biomimetic Defense Catalog: the long-term project
`github.com/annawhooo/biomimetic-defense-catalog` | launched April 2026

The paper is the proof of concept; the catalog is the durable artifact. It is a
structured, community-maintained knowledge base in the shape of MITRE ATT&CK,
one markdown file per mechanism, organized into detection, response, evasion,
learning, regulation, and architectural classes. 36 Tier 1 entries at launch,
with a three-tier review process and contribution paths designed for both
immunologists and security researchers.

### The Motion Detector Framework
`github.com/annawhooo/motion-detector-framework` | April 2026

Behavioral diagnostics for AI agent misbehavior in enterprise identity
infrastructure. The unifying principle: lack of plausible upstream reason. Six
diagnostic criteria; the sixth, Guardrail Delegation, is the novel one. A
transparent, well-intentioned agent that recruits a human to perform an action
its own controls prevent produces the same behavioral signature as social
engineering. That leads to the Transparency Paradox: performative transparency
functions as a persuasion mechanism, not a safety mechanism.

This is not only a paper. The 13 detection rules are implemented and were
validated against 48 real audit events from Coffer's telemetry, where they
found 4 real implementation bugs that I then fixed. Detect, diagnose, fix,
verify, on my own tool.

### Divergence Series: four papers on reasoning-generation fidelity
`github.com/annawhooo/divergence-series` | April 2026 to present, ~41,000 words

Empirical and architectural research on whether an agent's output faithfully
reflects its reasoning.

- **Honesty Decay**: evidence that reasoning-generation divergence is
  progressive, not stochastic; a probabilistic sunk-cost mechanism makes
  correction more expensive each turn.
- **The Audit Gap** (~30,000 words, 350+ references): six structural
  constraints that make agent self-correction a mechanical impossibility, not
  a missing feature; the incremental attention drift attack, which achieves
  prompt injection through persistence and time alone; a Three-Tier Audit
  Stack architecture.
- **Divergence Taxonomy**: an 8-type classification of thinking-to-text
  divergence with detection methods per type.
- **Semantic Drift Measurement Methodology**: a quantitative pipeline using
  bi-encoder fidelity scoring, cross-encoder verification, and LLM-as-judge
  escalation. The agent cannot influence its own score.

Behind the papers sits a maintained registry of 80 external works (arXiv,
industry, standards) with per-item provenance tags, citation status, and
adversarial verification sweeps. The August sweep verified 90 primary sources
with zero misattributions. When another team independently coined "audit gap"
for a different interval, I handled it as concurrent coinage with a
differentiation paragraph, not a priority claim.

### mcp-tap: audit infrastructure for stdio MCP servers
`github.com/annawhooo/mcp-tap` | April to May 2026 | Python, stdlib only

MCP gateways capture traffic for HTTP-transport servers. Most community MCP
servers run on stdio, where there is no network traffic to intercept. mcp-tap
covers the transport nobody else covers: a transparent wrapper between client
and server that logs all JSON-RPC traffic to tamper-evident, HMAC-chained
JSONL. The server does not know it is there; the agent does not know it is
there. Four sensitivity modes (full, redact, hash, metadata) for production
data handling.

It ships with mcp-detect, a transport-agnostic detection engine: 15 rules,
ten derived from the biomimetic catalog (BIO-001 through BIO-009 families,
honeytoken access, structural mutation, and kin) and five conventional
controls, operating on traffic from mcp-tap, the Bifrost gateway, or SIEM
ingestion. The experiment behind it is a factorial detection study with
honeytokens, a five-state outcome taxonomy, and a pre-registered strict
binarization for the Cochran's Q and McNemar primary analyses. The strict
specification was registered before any real-data output was viewed.

### Upstream contributions

**Pipelock** (`luckyPipewrench/pipelock`), an open-source AI agent firewall for
verifiable egress control, Go. In June I landed six merged PRs: a capture
feature adding the JSON-RPC id to CaptureRequest so requests and responses join
in receipts (#708), and a Windows test-portability series (#710, #711, #766,
#767, #768) fixing golden-file line endings, Unix-only test assumptions, and a
TempDir teardown flake. Follow-up branches (Winsock close-code parity, portable
forced-failure injection for certgen tests) are submitted on my fork.

**AARM/CSA Specification** (runtime security spec for AI-driven actions). In
May I submitted a registry PR listing mcp-tap in the spec's builders registry
under the Aligned tier.

### self-context-calibration: the measurement program
`github.com/annawhooo/self-context-calibration` | July 2026 to present

The question: when an agent's own prior commitment is silently removed from
context, does the model say "I can't know that," or does it confidently
fabricate an answer? This is a standard method, abstention under unanswerable
context, pointed at a novel target: the agent's own dropped commitment.

Three studies share one instrument, a 68-item forced-choice security-judgment
bank (45 derivable, 23 designed-equipoise) that I authored and baselined with
2,850 rows across three models.

- **v1.5 faithful study**: pre-registration locked and tagged before the first
  real run (2026-07-22). The headline is a strong per-model contrast under
  absence: one model abstains in 65 to 100% of anchor cells; the other two
  abstain at 0 to 11% and confidently assert or deny content they can no
  longer see, at rates up to 94% with control questions passing at 100%. The
  committed read lives in the repo; the numbers are regenerable from the
  pre-registered analyzer.
- **Convergence study**: the cross-vendor arm. Ten models across five
  providers (Anthropic, OpenAI, Google, DeepSeek, Z.ai), 18 model-arm cells at
  exactly 680 rows each, 12,240 rows total, collection completed 2026-07-28
  under its own pre-registration. The analysis is deterministic and
  sha256-matched across three independent executions. The collection runner
  enforces an echo tripwire that halts on any sign of preview-id contamination.
- **Drift monitor**: live since 2026-08-02. Daily K=10 probes of the full bank
  against five served APIs, per-item total-variation distance against frozen
  baselines with simulation-calibrated p99 thresholds, a same-day
  disambiguation rerun on breach, and a six-state verdict grammar. The false
  positive budget is not hand-waved: an exact-enumeration null puts expected
  false breaches at 1.64 per day against 0.05 observed. The monitor has
  already documented multiple drift events behind unchanged model ids,
  including recurring, reversible day-scale regime flips in judgment behavior,
  and it runs for about 20 USD a month.
- **Publication**: a Defenders-track submission on the drift monitor is in
  preparation for INTERCEPT, the AARM runtime-security venue (San Francisco,
  February 2027; submissions close 2026-10-01).

## Research practice worth naming

The methodology is a deliberate differentiator, and it is all public history.

- Three pre-registrations at three lock states, with a tagged lock commit,
  a LOCK.md scoping what is and is not frozen, and Deviations sections instead
  of silent edits.
- A written reporting commitment made before monitoring began: quiet windows
  get published, not just events.
- A dated design-limitations audit of my own instrument, a corrected
  false-breach calculation committed with the exact-enumeration script, and a
  declined K=30 upgrade recorded with its fallback. Honest failure is part of
  the record, not something scrubbed from it.

## Skills demonstrated

- Python (measurement harnesses and MCP servers, largely stdlib, heavily
  tested), Go (upstream firewall contributions), CI, mutation testing.
- Applied statistics: Wilson intervals, total-variation distance,
  exact-enumeration nulls, simulation-calibrated thresholds, Cochran's Q,
  McNemar's exact test, pre-registered primary/sensitivity splits.
- LLM provider APIs across Anthropic, OpenAI, Google, DeepSeek, and Z.ai,
  including per-provider reasoning and temperature handling.
- Applied cryptography for audit: AES-256-GCM with AAD, HMAC chain integrity,
  tamper-evident logging.
- Research operations: pre-registration, citation verification at scale,
  responsible handling of naming collisions and concurrent work.

## Resume bullet shortlist

Pick, trim, and tense-shift as needed.

- Built Coffer, an open-source credential vault MCP server that lets LLM
  agents use passwords and API keys without ever seeing them: AES-256-GCM
  vault, fail-closed URL allowlists, HMAC tamper-evident audit; 417 tests.
- Co-authored Biomimetic Gap Analysis (Zenodo DOI, 170 refs): mapped immune
  mechanisms to agent security across 36 patterns and 19 attack scenarios;
  graded 74% of scenarios exploitable against current MCP and LangChain.
- Launched the Biomimetic Defense Catalog, a MITRE-ATT&CK-style open
  knowledge base of biological defense mechanisms mapped to agent security;
  36 full-treatment entries with a tiered community review process.
- Defined the Motion Detector Framework for agent behavioral diagnostics;
  its novel Guardrail Delegation criterion identifies transparent agents that
  structurally mimic social engineering. 13 implemented rules found 4 real
  bugs in production vault telemetry.
- Wrote the four-paper Divergence Series (~41k words, 350+ verified
  references) on reasoning-generation fidelity, including the incremental
  attention drift attack and an 8-type divergence taxonomy.
- Built mcp-tap, a zero-dependency transparent audit wrapper for stdio MCP
  servers with HMAC-chained tamper-evident logs, plus a 15-rule
  transport-agnostic detection engine validated in a pre-registered factorial
  experiment.
- Landed six merged PRs in Pipelock (Go AI-agent firewall): request/response
  join ids in capture receipts and a Windows test-portability series.
- Designed and ran a pre-registered three-study measurement program on LLM
  self-context calibration: 68-item instrument, 12,240-row cross-vendor
  collection over ten models and five providers, sha256-reproducible analysis.
- Operate a continuous drift monitor over five production LLM APIs that
  detected reversible day-scale behavioral regime flips behind unchanged model
  ids, for ~$20/month; conference submission in preparation (INTERCEPT 2027).
