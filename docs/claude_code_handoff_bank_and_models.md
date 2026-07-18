# Code handoff: bank edit and --models argument (pre-baseline blockers)

Context: the v1.5 merge (de59adb) records the bank change; this handoff
executes it, plus one harness ergonomics change, so the Sonnet and Opus
baseline arms can run over the full bank without constant juggling. Scope is
exactly these two changes and their tests. No analyzer changes; the v1.5
analyzer reconciliation is a separate later handoff.

## Change 1: items.py bank edit

Move the thirteen round-two screened candidates from
items/candidate_sweep.py CANDIDATES into the items.py bank, decision text
copied verbatim, no rewording of any kind. The thirteen IDs:

eq_alert_waf_mode_v2, eq_alert_fraud_scoring_v2, eq_alert_vuln_gating_v2,
eq_alert_spend_anomaly_v2, eq_alert_dlp_email_v2, eq_access_cert_cadence,
eq_access_priv_groups, eq_access_contractor, eq_access_service_accounts,
eq_access_offboarding, eq_access_oauth_grants, eq_access_share_links,
eq_access_breakglass

Cell field: all thirteen get cell "equipoise", matching the eq_ prefix
convention. The cell field is legacy plumbing under v1.5; item roles are
assigned per model from baselines at analysis time. Add a one-line comment
in items.py saying exactly that, so nobody reads cell as a v1.5 role.

Do NOT move: eq_seed_* items, the antiexample item, or anything else in
CANDIDATES. Do not modify candidate_sweep.py; the frozen screening jsonl is
the screening record and the sweep file stays as the authoring tool.

After the edit: len(ITEMS) == 68, 45 derivable + 23 equipoise, all ids
unique, every item has id, decision, cell.

## Change 2: --models argument

Add --models to the harness CLI: a comma-separated list of model IDs,
validated against THINKING_CONFIG keys, applied to both arms, run in the
order given. An unknown ID errors out before any API call is made. Default
behavior with the flag absent is unchanged (the MODELS constant, currently
Haiku-only, stays as is). Implementation shape is your choice; the pinned
behavior is: --models claude-sonnet-4-6,claude-opus-4-7 runs exactly those
two, in that order, and nothing else.

## Tests (TDD, extend tests/)

- Bank integrity: 68 items, unique ids, required fields present, and the
  thirteen new decision strings byte-identical to their CANDIDATES source
  (import both modules and compare; this enforces verbatim).
- --models parsing: valid list accepted in order, unknown ID raises before
  any network call, absent flag falls back to MODELS. No API calls in tests.
- Existing needle-parser fixture suite: all pass, zero regressions.

## Hard constraints

- Verbatim decision text; the byte-identical test is the enforcement.
- No changes to MODELS default, THINKING_CONFIG, K_BASELINE, the parser,
  prompts, or the analyzer.
- No em dashes anywhere.

## Report back

Bank count and integrity test result; verbatim check result; --models
behavior demonstrated (parse-level, no calls); full suite status; anything
you were forced to deviate on (should be nothing).
