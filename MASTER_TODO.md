# Master To-Do List — All Workstreams

**Compiled 2026-09-05.** Sources swept: this repo (all docs, code, PRs), the six other
`annawhooo` GitHub repos (`divergence-series`, `biomimetic-gap-analysis`,
`biomimetic-defense-catalog`, `motion-detector-framework`, `mcp-tap`, `coffer-mcp`),
Google Drive (divergence corpus, CSA/AARM docs, SOC 2 paper), Gmail, Slack, and
Google Calendar. Every item was verified against the newest evidence available;
items found already completed are listed in the appendix so they don't resurface.

**Excluded by request:** routine operations of the automated daily probe (daily
runs, verdict pushes, report generation) and conditional tripwires that have not
fired (rollback rules, re-baseline reversals).

---

## Deadline map (the next five weeks are the whole story)

| Date | What |
|---|---|
| Mon Sep 14 | Moveworks HM interview, 2:30 PM PDT (accepted) |
| Mon Sep 15 | Last day a `fraud_scoring` step-change run can begin and still resolve pre-freeze |
| Sep 16–17 | CSA AI Security Summit 2026 — **RSVP still needsAction** |
| Fri Sep 18 | AARM Working Group call |
| Fri Sep 26 | **INTERCEPT data freeze** — freeze analysis, figure/number regeneration, freeze write-ups |
| Sep 27–30 | Number swap + verification, IEEE typeset, blind pass, **submit (closes Oct 1)** |
| Sep 27 – Oct 2 | Only window to adopt the recalibration policy by commit before going away |
| Fri Oct 2 | AARM WG call; earliest effective date for recalibration + exact-arithmetic commits |
| **Oct 3–12** | **Away: cruise Oct 3–10 + fall break Oct 8–12.** Post-submission window is effectively Sep 27 – Oct 2, then nothing until Oct 13 |

---

## 1. Self-Context Calibration (`self-context-calibration`)

### Deadline-driven — the INTERCEPT chain

- [ ] **Blind-review / repo-anonymization decision** — contact INTERCEPT organizers now
  for lead time; default "public artifact, link on acceptance," else anonymized
  mirror; repo name stays out of the PDF. (`paper/INTERCEPT_DRAFT.md` §7; decide before submission)
- [ ] **Freeze the gitignored raw rows behind cited drift events** before Sep 26 —
  Jul 31 poke rows, Aug 3 and Aug 6 probe/baseline rows; all three events feed
  paper §3.1.1, so the "freeze deliberately if cited" condition is met.
  (`probe/DRIFT_EVENT_2026-07-31.md`, `..._08-03.md`, `..._08-06.md`)
- [ ] **Sep 26 freeze analysis** — every headline number under both as-recorded and
  exact semantics via `probe/scripts/float_census.py`; regenerate all `[FREEZE]`
  numbers, figures F1–F4, tables T1–T2 (current renders are stamped data-through
  2026-08-20) and swap into the draft. (`probe/FLOAT_POLICY_2026-08-30.md` layer 2; `paper/INTERCEPT_DRAFT.md` numbers policy)
- [ ] **Freeze write-ups** due with the freeze report:
  - the two gpt step-change threads, pre-pin/post-pin boundary maintained
    (`probe/STEP_CHANGE_DECISION_RULES_2026-08-31.md`)
  - haiku `spend_anomaly_v2` Sep 2 RETURN day: single-day visit vs start of a D
    re-dwell (Sep 3–4 data already points to visit) (`probe/SLOW_ALTERNATION_REVISION_2026-09-02.md`)
- [ ] **Sep 27–30: finish and submit** — number-swap verification fan-out (every prose
  figure diffed against script output), IEEE Overleaf template under 4 MB, blind
  pass scrubbing first-person self-references, submission form. Re-verify all
  references and CFP details at submission time, including the
  check-against-PDF tag on arXiv:2605.15164. (`docs/claude_code_handoff_intercept_paper.md`)
- [ ] **Adopt the recalibration policy by commit before leaving Oct 3** — set the
  effective date (≥ Oct 2), strip DRAFT from title/status; adoption before the
  effective date is what makes it a pre-registration. (`probe/RECALIBRATION_POLICY_DRAFT_2026-08-16.md`)
- [ ] **Probe frequency increase decision** — 60 days of data lands ~Oct 1; Rory
  Ganness is waiting on the 3–4-hour-cycle call. Decide before the cruise even
  if implementation waits. (Slack DM w/ Rory, 2026-08-21)

### Post-freeze / post-submission backlog (realistically Oct 13+)

- [ ] **Float policy layer 3** — one dated commit converting `monitor.py` + null
  scripts to exact integer arithmetic with lattice values stored alongside
  floats and the declined-K30 sanity gates; effective ≥ Oct 2. Publicly promised
  in the draft. (`probe/FLOAT_POLICY_2026-08-30.md`)
- [ ] **DESIGN_LIMITATIONS fix 1** — populate `host` from the actual endpoint,
  per-call latency, response length, `temperature_sent` capture. (`probe/DESIGN_LIMITATIONS.md` fixes #1)
- [ ] **DESIGN_LIMITATIONS fix 3** — equipoise/decisive class annotations + regime
  status in the verdict path (deferred by Ruling 3 until after freeze). (`probe/RULINGS_2026-08-30.md`)
- [ ] **Lock `PRE_REGISTRATION.md`** — resolve the three open pre-lock choices
  (within-Claude spread metric, invalid-in-denominator treatment, present-recall
  void threshold), then dated tag + commit hash. **Gates the generalized v1 real
  run**, which has never occurred.
- [ ] **Run the generalized-family v1 real run** once locked (item bank ready at 68;
  pilot excluded from primary per stopping rule).
- [ ] **Close the convergence independent statistical review — OVERDUE.** The
  two-week blind-review window from late July expired with no review and no
  dated entry. Per the pre-registration's own rule: add the dated entry lifting
  the provisional markers ("review was sought and not obtained"), or obtain the
  review. The Judgment Convergence Note (2026-08-30, in `divergence-series`)
  still describes this as unresolved. (`convergence/PRE_REGISTRATION_CONVERGENCE.md` Deviations)
- [ ] **Trajectory bank for agent-level probing** — planted violations with ground
  truth, minimal pairs, non-roster piloting, bank frozen+hashed before first
  roster call; includes designing the **invocation receipt format** (Jason
  Keirstead's silent-disengagement question — "my current monitor won't see it").
  (`probe/ARCHITECTURE.md` "Next"; Slack DM w/ Jason, 2026-08-21)
- [ ] **Recover/re-upload `TODO.md`** (outputs-staged copy) carrying the
  prior-mapping spin-off; the file exists in no repo. (`docs/chat_session_handoff_2026-07-16.md`)
- [ ] Low: remove the per-model answer-distribution stdout print from
  `convergence/collect.py` (deferral condition expired when collection completed
  2026-07-28). (`convergence/COLLECTION_LOG.md`)

## 2. Divergence Series (`divergence-series` + April Drive corpus)

### Paper B (The_Audit_Gap.md) blockers

- [ ] **Run the four pending Garcia checks** — `*(Garcia check pending.)*` markers in
  §2.1, §2.4 ×2, §10.7 against the Stratosphere v2 draft, then remove markers.
  Highest-value Paper B item. (`The_Audit_Gap.md` lines 29/62/64/2584)
- [ ] **Eyeball the Seth–Sankarapu PDF** (arXiv:2605.15164) to confirm verbatim
  [Vi, Ai] wording before direct quotation — same PDF the INTERCEPT reference
  check flags, one read settles both. (`external_work_dependency_map.md` item 78)
- [ ] **Decide the 10 "undecided" registry items** (19, 21, 24, 27, 28, 30, 31, 34,
  39, 40) — §13.2 sentence/footnote or decline each; explicitly "pending Anna's
  call." (`external_work_dependency_map.md`)

### Metrics, taxonomy, validation

- [ ] **Build the fidelity-score tooling and set thresholds empirically** — the
  metric architecture is done (`Semantic_Drift_Measurement_Methodology.md` §2–3
  implements the taxonomy's §8 score), but threshold_A/threshold_B remain "to be
  determined," which first needs the labeled thinking-text divergence dataset
  (open problem 8, §5.2).
- [ ] **Verify or replace the "Mahmoud et al., 2026" citation** load-bearing for
  Constraint 6 in the Semantic Drift doc (Paper B itself leans on Bricken/Zou,
  so scope is the methodology doc only).
- [ ] **Complete the full human validation of the (now 10-type) taxonomy** against the
  exported conversations, then update/remove the §6 disclaimer — the OOB review
  so far covered only the Type 7 Instance-1 deletion.
- [ ] Human review of prior research sessions for steering/smoothing artifacts
  (Shaun, Calvin, or other trusted party). (April 8 tracker + gaslighting finding checklist)
- [ ] Third-party verification of the literal-search (grep-not-semantic) limitation —
  the record itself says this finding "cannot come from Claude."
- [ ] Peer assessment of whether the "deterministic shared deception"
  monoculture-collapse framing is a new contribution vs Gradient Institute's
  correlated errors (the 0.90 measurement now exists in the Judgment Convergence
  Note; the novelty judgment is the human ask).
- [ ] Low: capture more OOB-anchored Type 7 instances (two is thin); systematic
  six-constraint validation across model families (research-scale).
- [ ] Low: document that only the final taxonomy revision survives (intermediate
  container-session revisions are gone), closing the April "save all versions
  for diffing" concern.

### Outreach & disclosure

- [ ] **Resubmit the April 8 architectural-gaslighting disclosure** via Anthropic's
  HackerOne VDP or modelbugbounty@anthropic.com — the original (which *was*
  sent, contrary to the April conversation record) got only auto-replies, and
  the six Anthropic-side open questions in the Mechanism Description ride on it
  reaching a human. (Gmail thread "Responsible Disclosure: …")
- [ ] Share the April screenshots/write-up with Sebastian Garcia for an uncued
  "what do you make of this?" read.
- [ ] Decide on the drafted Henry Sleight (Anthropic) LinkedIn pitch — taxonomy +
  Ariadne-score telemetry for A3; mentions the Fellows program. (Drive: AI Alignment Research Master File, Part 3)
- [ ] Copy the "Noir Noir" forensic log (Exhibit A, φ=0.0 trace-absence case) into a
  standalone evidence document. (same Master File)
- [ ] Decide where the gaslighting demo goes now that DEF CON has passed (May 1
  deadline missed; talk declined — see feedback item in Parking Lot).

## 3. Biomimetic Gap Analysis (`biomimetic-gap-analysis`, `biomimetic-defense-catalog`, BIO rules in `mcp-tap`)

### The Stratosphere / Sebastian Garcia thread (stalled since April — one email revives all of it)

- [ ] **Re-engage Sebastian Garcia:** send the feedback on their Draftv2 he asked for
  Apr 6 ("Tell me what you think" — never answered), schedule the call deferred
  since Apr 7, softly nudge his promised comments on the gap-analysis paper, and
  revive the unanswered Jul 28 probe-harness offer (thread's last message,
  silent 5+ weeks). (Gmail thread "Your immunity principles paper…")
- [ ] **Formalize the behavioral signatures for Slips' Negative Selection and send
  them** — promised Apr 9; grep confirms nothing exists in any repo.

### Paper & catalog

- [ ] **Reference-integrity pre-submission TODO:** decide cite-or-remove for the 9
  defined-but-uncited references ([35] [39] [44] [51] [67] [68] [69] [177]
  [215]). Explicit blocker left in the manuscript. (`immune-security-mappings.md` HTML comment ~line 1919)
- [ ] **Ship the v2.2 release artifacts** — the Apr 19 expansion (37 mappings / 37
  DPs / 23 scenarios / 9 failure modes) never propagated: README still says
  36/35/19/8, the PDF is the v2.1 build, no new Zenodo version behind the DOI
  people are told to cite.
- [ ] **Build the promised proof-of-concept prototype** — implement 2–3 design
  principles as monitoring capabilities (priority candidates: mappings #2, #20,
  #17, #32). The paper's responsible-disclosure argument for publishing 23
  attack scenarios depends on these existing. (§12.5)
- [ ] Arrange immunologist (+ security) peer review — declared a priority in both
  Limitations and Future Work.
- [ ] Populate `biomimetic-defense-catalog`: INDEX.md claims 36 Tier-1 entries, only
  3 files exist (BDC-001/020/035); also sync the Apr 19 additions (prion
  mapping #37, DPs #36–37) into the index.
- [ ] Low: 15-mechanism candidate queue → Tier 3+ entries (Table 3 flags the first
  four as priorities); second-domain methodology validation; contributor infra
  (.github issue templates, missing LICENSE file, 8-step vs 12-step protocol
  mismatch in CONTRIBUTING.md).

### BIO detection rules (`mcp-tap` — file is titled "must complete before publishing/presenting")

- [ ] **Implement BIO-004b/c/d** (honeytoken filename in listings; canary string in
  response content + `--canaries` arg; mtime/atime stealth-access delta) —
  verified absent, `mcp_detect.py` has only 004a. (`TODO_pre_publication.md`)
- [ ] Implement BIO-010 (chemotaxis: progressive directory narrowing, severity by
  depth + time-clustering).
- [ ] v2: multi-server scenarios so BIO-007 (cross-server correlation) can fire; for
  v1 document it NOT_APPLICABLE.
- [ ] **Generalization + adversarial validation of the rule set** — test against
  production telemetry beyond coffer-mcp, and a red-team round with an attacker
  motivated to defeat the specific rules. Named "necessary next step" in both
  The_Audit_Gap §10.6 and the Motion Detector paper (Open Question 6).

## 4. AI Security (CSA / AARM / papers / tooling)

### CSA & AARM working group

- [ ] **Peer-review CSA Draft 5/7** ("Operationalizing the Agentic Control Plane:
  Integrating the AARM Specification") — individually shared with you
  2026-05-22, comments collected in-doc, paper at v0.9 heading to copyedit;
  while at it, flag (or draft) the **empty §6.2** and the **duplicate §6.3
  numbering**.
- [ ] **AARM benchmarking action items** (Benchmarking doc, 2026-08-17 + group DM):
  follow up with Jens Ernstberger on the KSec harness/schema/scoring; evaluate
  `luckyPipewrench/agent-egress-bench` (per Slack Sep 4: now 256 cases across 18
  attack categories with working runner+validator); define harness requirements
  / build-vs-instructions; locate labeled & unlabeled data; pick up your
  assignments from Akul's To-Dos breakdown and reconnect with the group (last
  activity Aug 6, one missed sync).
- [ ] **RSVP the CSA AI Security Summit, Sep 16–17** — calendar invite still
  needsAction.
- [ ] Pursue the AARM Builders Registry submission path for `mcp-tap`,
  `coffer-mcp`, `motion-detector-framework` (recorded as the recommended
  positioning, 2026-05-09).
- [ ] 3SRM draft: define the promised **second "emerging actor"** in §3.3 (only Tool
  Provider is written) and create the missing §2.3 "Evolution of As-a-Service
  Deployment Models" companion graphic.

### SOC 2 compliance eval (pre-committed in the published paper)

- [ ] Run the repetition follow-on: every cell ×3 for variance estimates — flagged
  in the paper as "the primary target for reviewer scrutiny."
- [ ] Run the paraphrase-robustness study (several equivalent directed phrasings)
  alongside it.
- [ ] Backlog: re-test the idiom-vs-opt-in taxonomy on other stacks (CI/CD secret
  handling, audit-logging middleware are the named next cases).

### Motion Detector / mcp-tap publication blockers

- [ ] **Write the methods section per the pre-registered binarization plan** — strict
  run as headline, `--lenient` as sensitivity appendix. Marked PRIMARY. (`TODO_pre_publication.md`)
- [ ] **Add the BIO-004 review-session methodology section** — specificity vs
  severity as independent axes, gating-tier table, signal-uniqueness,
  multi-sensor complementarity ("paper-worthy framing," currently absent from
  the paper).
- [ ] Resolve the v1-run open questions: s22 broad-glob LOW tier?, verify s03
  BIO-002b no-fire prediction, check s13 BIO-003 RULE_MISSED sensitivity.
- [ ] Decide CONV-005's fate: redefine for scenario-relevant enumeration or retire
  and document as inapplicable (open in two docs).
- [ ] **Implement Rules 018/019 or correct the paper's claim** — paper says "nineteen
  rules implemented," `coffer_detect_v05.py` implements 17 and can't consume
  the transcripts 018/019 require.
- [ ] Implement Criterion #6 (Guardrail Delegation) — blocked-action→human-request
  correlation + the sensitivity classifier it needs; fix its stale "Rule 008"
  numbering (008 was reassigned).
- [ ] Uniformity sweep: filter-primitive audit, gate-count→severity mapping per
  rule, BIO-002→BIO-002a rename.
- [ ] Low: consolidate the two ISO-8601 timestamp parsers; Path D (OS-level audit
  hooks with PID↔MCP-session correlation) + content-transformation-evasion
  detection as v2 research.
- [ ] Low: scope the regulator-facing crosswalk paper (NIST AI RMF / ISO 42001 /
  EU AI Act) that Policy Cards was deferred into (locked decision 2026-05-07).

## 5. Parking Lot (real tasks, no research home)

- [ ] **Finish post-incident credential hygiene (2026-07-19 vault incident)** — the
  diagnostic half landed in coffer-mcp (2026-08-12: verify_chain now classifies
  pre-HMAC entries as unverifiable-not-tampered), but: retire the superseded API
  key, confirm the replacement is the only live key, local environment cleanup
  (all off-repo, unverified), and actually clear/re-key the pre-HMAC entries in
  the local audit chain — coffer has no upgrade path for them yet.
- [ ] Moveworks HM interview **Sep 14, 2:30 PM PDT** with Kyle Hirai (Staff Security
  Engineer, Compliance) — prep.
- [ ] coffer-mcp backlog (`docs/NEXT_STEPS.md`): async exec job pattern (~60s
  client timeout truncates long commands), parameterized argv slots, stdin
  passthrough, retire legacy AAD fallbacks (RR-L6), Fix C generic key-pattern
  scanning, Tier-3 enterprise items (rotation automation, compliance mapping,
  observability, multi-user boundary).
- [ ] Household list (unsent Gmail draft, Aug 1): Dyson battery, mulch, both
  vehicles, golf cart, fence, ceiling fan, reupholster chairs, Xbox
  controllers, paint, garage freezer.

---

## Coverage caveats

- **Five AARM WG meeting recordings** (2026-05-29 → 2026-08-21, mp4s in Drive)
  could not be reviewed; spoken action items unchecked. A direct read of
  #aarm-working-group Aug 21–Sep 5 found no missed Anna-owned items. Recordings
  also at csaurl.org/aarm-recordings.
- **Obsidian vault** (`/mnt/d/Obsidian Vault/AI Research/`) is a local mount not
  reachable from this session — any to-dos living only there are not included.
- One Gmail thread (1a02bbdc9fdf25f8) is permission-denied; its associated drafts
  are empty-bodied, so likely nothing actionable.
- `divergence-series` notes Paper C (Design Principles) has no standalone
  manuscript file in any repo — if it lives somewhere else, that copy wasn't swept.

## Appendix — verified already done (so they stop haunting old trackers)

- Convergence study write-up **and** the monoculture/gradient standalone write-up:
  `Judgment_Convergence_Note.md` (divergence-series, merged 2026-08-31) covers
  both, reports the 2026-07-28 sequencing breach and both provisional-rule
  branches; 0.90 deployed-arm agreement is the finding (supersedes the ~0.93
  preliminary).
- Paper B integration of the gaslighting finding (§3.3, §10.4, §13 — no
  "Scenario #0" label, scenarios run #1–23).
- Formatting Evasion documented (`Honesty_Decay.md` §5); Internal Telemetry
  Resolution / literal-search metric specified (`Divergence_Taxonomy.md` §9, ITR).
- Paper C audit-trail-integrity principle adopted as DP #37 (2026-04-10); Paper D
  divergence detection rule added as Criterion #7 (2026-04-09/10).
- The April 8 responsible-disclosure email **was sent** (the conversation record
  saying "not yet sent" is wrong) — it just never got past auto-replies, hence
  the resubmit item above. Transcript exports and screenshot off-phone storage:
  done.
- April drift-window operator items (float policy, gpt step-change ruling,
  return-watch scope) all closed by the merged Aug 30–Sep 2 notes.
- Dropped by decision, 2026-09-05: the April "Slack message to Brian" share
  (declined; the underlying "no second human has seen the raw evidence" premise
  was already stale) and the DEF CON CFP feedback nudge (feedback will arrive
  unprompted; waiting is the plan).
