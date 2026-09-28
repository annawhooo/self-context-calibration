# Verification passes on the INTERCEPT submission, 2026-09-28

Two multi-agent verification runs were made against the LaTeX in
paper/intercept/ before it was handed to the operator for upload.
This note records what ran and what it changed; the resulting
number ledger is paper/FREEZE_2026-09-26.md (section "Amendments
after the 2026-09-28 verification run"). The raw agent transcripts
are session artifacts and are not committed; they carry local
machine paths and are not part of the public artifact.

## Pass 1 (126 agents, against the first freeze-numbered LaTeX)

Lanes: seven per-section number audits, each finding re-checked by
two adversarial refuters (50 of 53 findings stood); five
claim-check lanes against the dated notes under probe/; a
blind-review scrub including PDF metadata; primary-source citation
verification of every refs.bib entry (arXiv abstract pages, the two
cited web pages); a static LaTeX lint plus a MiKTeX compile; a
voice pass against the operator's writing profile; three reviewer
lenses (statistical skeptic, security-operations practitioner,
CFP evaluator); a completeness critic.

Blockers found and fixed: the gemini 503 day count (nine, not ten;
2026-09-23 was the all-arm outage); the item (g) tally (3 + 4 + 9 +
5 = 21); the cai citation (title and authors were wrong); the
concentration P-values reported under one null only.

Majors found and fixed: the Fig. 1 thread count (fourteen); the
gpt patch-timing two-day excursion; "ten repeat threads" (eight);
the exact-semantics companion sentence; the K=30 band provenance
(now recomputed by a committed script) and the claim that 0.30
sits above the declined bands (it sits inside them); the rollback
rule wording (more than three); the count-vs-null framing (now
split by class); the direction test (now reported conditionally on
the observed threads, with the joint rows kept and labeled); the
covariate-constancy sentence; the "seven return visits" double
count; the pin-registration caveats; the Chauvin positioning; the
tschisgale and thinking-machines references; T1 overfull width;
figure fonts below 6 pt at print size; the abstract length.

Minors applied: about thirty wording, rounding, and voice items,
listed in the ledger amendments.

Not applied, operator decisions (recorded in SUBMISSION_FORM.md):
talk format; vendor and model names under the CFP's literal
blind-review wording; an anonymized artifact mirror for reviewers.

## Pass 2 (87 agents, against the revised LaTeX)

Lanes: the same seven number audits with refuters (35 of 38
findings stood), a blind scrub, a compile-based lint, a voice pass,
and a critic checking that every pass 1 fix landed in both the
LaTeX and the markdown master (it had; the two files differed only
in notation and cross-references).

Majors found and fixed: the phenotype contribution counted five
vendors where the roster has five models on four providers; the
postmortem sentence applied every modifier to all three bugs; the
runs-test count (eleven of thirteen at |z| < 1.6, not ten); a
false clause about the sonnet pooled record; the scope of the
week-scale dwell claim; a reference-convention mismatch between
the class-split null and T1 (now aligned, total 92.14); the
independence caveat's lower-tail exception; "17 recurring slots"
(14 repeat). Compliance: TrueType fonts replace Type 3 in the
figures, every printed glyph is 6 pt or larger, arm labels match
the prose, the two web-post references print the year once, the
last page is balanced, Table II's explanation moved from its
small-caps caption to a note row.

Minors applied: "at least" on the pooled-record tails, "probed
model-days", "per seven probe days", the joint-state descriptor
(9 or 10 of 10 A), sentence splits for every sentence over 45
words, three closers rewritten, "my own network".

Left as operator decisions (SUBMISSION_FORM.md): talk format; the
CFP's literal "no company name" clause against the vendor and
model names the paper measures; the searchability of the title and
section names in the public repository.
