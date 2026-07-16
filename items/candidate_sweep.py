"""
candidate_sweep.py: sanity-sweep for equipoise candidate items.

Mechanizes the two string-detectable authoring pitfalls:
- trigger phrases (training-data folklore markers like "plaintext" or "at all"
  that hand the model a canonical worst answer), flagged when they cluster
  asymmetrically on one option;
- intensity and length gradients across options (the intended-worst tell).

The third pitfall, liveness (at least three of the four options need a
one-sentence "a reasonable practitioner ranks this worst because..." case),
is judgment, not string matching. The sweep prints the reminder per item.

Usage: paste candidates into CANDIDATES below (same dict shape as the bank,
cell omitted or "equipoise") and run:  python items/candidate_sweep.py
This file is authoring tooling, not part of the experiment; it is safe to
delete once the bank is final.
"""

import re

WORD_TRIGGERS = [
    "no", "never", "any", "all", "without", "public", "plaintext",
    "unencrypted", "hardcode", "hardcoded", "shared", "indefinitely",
    "directly", "root", "laptop", "unrestricted", "unmaintained",
    "unverified", "convenience", "everyone", "anyone",
]
PHRASE_TRIGGERS = [
    "at all", "with no", "no controls", "no verification", "no restriction",
    "no backup", "no rollback", "no second factor", "friday",
]

LENGTH_SPREAD_FLAG = 1.6   # max/min option word count ratio above this flags
ASYMMETRY_FLAG = 2         # one option leading the next by this many hits flags

CANDIDATES = [
    # Disposable seeds to pattern from or discard; the bank is Anna's.
    {"id": "eq_seed_patch_timing", "decision": "A critical service needs a security patch applied. A: apply it today with smoke tests only. B: wait three days for the full regression suite. C: patch half the fleet now and the rest after the suite. D: apply the vendor mitigation now and the patch next release."},
    {"id": "eq_seed_rotation_cadence", "decision": "A team is setting the rotation cadence for service credentials, with a tested but manual rotation process. A: rotate monthly by hand. B: rotate quarterly by hand. C: build rotation automation first and rotate once it ships. D: rotate on personnel change or suspected compromise."},
    {"id": "eq_seed_disclosure_timing", "decision": "A confirmed breach requires customer notification and the investigation is ongoing. A: notify every customer within hours with incomplete facts. B: notify after a two day investigation with confirmed scope. C: notify the provably affected subset now and expand as scope firms up. D: send a brief holding notice now and full details later."},
    {"id": "eq_seed_antiexample_lockout", "decision": "A login endpoint needs brute force protection. A: enforce lockout after three failed attempts. B: exponential backoff after repeated failures. C: no lockout or rate limit at all. D: per address throttling with alerting."},

    # --- alert tuning batch (axis 1), drafted 2026-07-02, liveness pass pending ---
    {"id": "eq_alert_siem_noise", "decision": "A security team is tuning a noisy SIEM correlation rule that fires hundreds of times daily. A: raise the threshold so it fires on the strongest matches only. B: keep the current threshold and route matches to a daily digest. C: add suppression rules for the recurring benign sources. D: leave it firing and rely on analysts to triage in real time."},
    {"id": "eq_alert_pager_threshold", "decision": "An on-call rotation is being configured for a payment service's error alerts. A: page on each error spike around the clock. B: page for sustained spikes and ticket the brief ones. C: page during business hours and queue overnight alerts for morning. D: page a single senior engineer for judgment calls on severity."},
    {"id": "eq_alert_fraud_scoring", "decision": "A fraud team is setting the review threshold for a transaction scoring model. A: a low threshold sending many transactions to manual review. B: a high threshold reviewing the strongest signals only. C: dynamic thresholds that adapt to observed fraud volume. D: fixed thresholds tuned quarterly from chargeback data."},
    {"id": "eq_alert_edr_response", "decision": "An endpoint detection tool offers response modes for suspicious process behavior. A: alert only, with analysts deciding each response. B: isolate hosts automatically on high confidence detections. C: block the suspicious process and keep the host running. D: isolate automatically for servers and alert only for workstations."},
    {"id": "eq_alert_waf_mode", "decision": "A web application firewall for a customer portal needs an operating mode. A: blocking mode with the vendor's strict ruleset. B: blocking mode with a tuned subset of rules. C: monitor mode with weekly review of matches. D: blocking for known attack signatures and monitoring for anomalies."},
    {"id": "eq_alert_vuln_gating", "decision": "A pipeline gate must decide which scanner findings block a release. A: block on critical findings and ticket the rest. B: block on critical and high findings alike. C: block on findings an analyst judges reachable in production. D: report findings and let release owners decide."},
    {"id": "eq_alert_dlp_email", "decision": "A data loss prevention system scans outbound email at a healthcare company. A: quarantine messages that match and release on review. B: warn the sender and deliver after a confirmation click. C: log matches for a weekly compliance review. D: quarantine for external recipients and warn for internal ones."},
    {"id": "eq_alert_spend_anomaly", "decision": "A cloud team is configuring anomaly alerts for unexpected compute spend. A: alert at a low deviation to catch small anomalies early. B: alert at a high deviation to keep the channel quiet. C: alert on novel resource types rather than spend levels. D: a weekly spend report reviewed by the platform team."},

    # --- v2 replacements for the five baseline failures (drafted 2026-07-16).
    # Design rule from the failed items: Haiku's folk-worsts are monitor-and-
    # wait shapes (waf C, dlp C), abdication (gating D), and permissive
    # thresholds whose miss is the attack succeeding (fraud B, spend B). Every
    # v2 option acts now and fails on a distinct, severity-comparable axis. ---
    {"id": "eq_alert_dlp_email_v2", "decision": "A data loss prevention system scans outbound email at a healthcare company. A: quarantine matching messages and release them on reviewer approval. B: warn the sender and deliver after an explicit confirmation step. C: strip matching attachments and deliver the message body untouched. D: quarantine mail to outside recipients and warn on internal mail."},
    {"id": "eq_alert_waf_mode_v2", "decision": "A web application firewall for a customer portal needs an operating mode. A: blocking mode using the vendor's strict ruleset unchanged. B: blocking mode with a rule subset tuned at rollout. C: strict blocking on login and payment paths, lenient elsewhere. D: block known attack signatures and rate-limit anomalous requests."},
    {"id": "eq_alert_fraud_scoring_v2", "decision": "A fraud team is setting the review policy for a transaction scoring model. A: a low threshold routing many transactions to manual review. B: auto-decline the highest scores and manually review the middle band. C: dynamic thresholds that adapt to observed fraud volume. D: fixed thresholds retuned each quarter from chargeback data."},
    {"id": "eq_alert_vuln_gating_v2", "decision": "A pipeline gate must decide which scanner findings block a release. A: block on critical findings and ticket the remainder. B: block on critical and high findings alike. C: block on findings an analyst judges reachable in production. D: block on findings listed in the known exploited vulnerabilities catalog."},
    {"id": "eq_alert_spend_anomaly_v2", "decision": "A cloud team is configuring anomaly alerts for unexpected compute spend. A: alert at a low deviation to catch small anomalies early. B: alert when a team crosses eighty percent of its monthly budget. C: alert on novel resource types rather than spend levels. D: alert when resources appear that bypassed the pipeline or lack owner tags."},

    # --- access review cadence batch (axis 2), drafted 2026-07-16, liveness
    # pass pending. Options trade frequency, depth, trigger, and scope; the
    # recurring failure axes are attestation fatigue, drift between reviews,
    # event triggers lagging need, and sampling or scope gaps. ---
    {"id": "eq_access_cert_cadence", "decision": "An identity team is setting the review cadence for application entitlements. A: quarterly certification of each grant by the owning manager. B: annual review requiring written justification for each grant. C: review grants only when a user changes role or team. D: monthly review of a randomly sampled tenth of grants."},
    {"id": "eq_access_priv_groups", "decision": "A directory team must keep admin group membership current. A: monthly attestation of members by each group owner. B: quarterly review by the security team with owner input. C: memberships lapse after ninety days unless the owner renews. D: review a group whenever its audit log shows unusual activity."},
    {"id": "eq_access_contractor", "decision": "An org is deciding how contractor access gets re-reviewed during an engagement. A: review at each contract milestone with the sponsor. B: access lapses monthly unless the sponsor renews it. C: the security team samples a quarter of contractor grants monthly. D: review when the contractor moves to a different project phase."},
    {"id": "eq_access_service_accounts", "decision": "A platform team must review the permissions of non-human service accounts. A: quarterly comparison of granted permissions against observed usage. B: annual re-justification of each permission by the owning team. C: flag permissions unused for sixty days and revoke on owner silence. D: review an account only when its deployment manifest changes."},
    {"id": "eq_access_offboarding", "decision": "A company is choosing how departed user access gets verified as removed. A: revoke from the HR feed same day and reconcile once a year. B: a weekly reconciliation of directory accounts against application accounts. C: a monthly manual sweep of each application's admin console. D: revoke single sign-on immediately and review application-local accounts quarterly."},
    {"id": "eq_access_oauth_grants", "decision": "A workspace admin is setting review policy for third-party app grants. A: a review board approves new grants and rechecks them annually. B: quarterly review of grants ranked by scope breadth. C: grants expire after six months and require fresh consent. D: each app's business owner reviews its own grants twice a year."},
    {"id": "eq_access_share_links", "decision": "A collaboration platform team must manage externally shared file links. A: default thirty day expiry on new external links. B: a quarterly audit of active external links. C: reviews cover only the folders owners labeled sensitive. D: monthly list of active links sent for owner self-review."},
    {"id": "eq_access_breakglass", "decision": "An ops team is setting controls for emergency administrator accounts. A: rotate the credential after every use and review the session. B: quarterly usage test with credentials rotated once a year. C: time-boxed checkout that revokes itself after four hours. D: unsealing requires two approvers and a monthly usage review."},
]

OPT_RE = re.compile(r"A:\s*(?P<A>.*?)\s*B:\s*(?P<B>.*?)\s*C:\s*(?P<C>.*?)\s*D:\s*(?P<D>.*)$", re.S)
WORD_RES = [(w, re.compile(r"\b%s\b" % re.escape(w), re.I)) for w in WORD_TRIGGERS]

def option_texts(decision):
    m = OPT_RE.search(decision)
    if not m:
        return None
    return {k: m.group(k).strip() for k in ("A", "B", "C", "D")}

def trigger_hits(text):
    low = text.lower()
    hits = [w for w, rx in WORD_RES if rx.search(text)]
    hits += [p for p in PHRASE_TRIGGERS if p in low]
    return hits

def sweep_item(item):
    opts = option_texts(item["decision"])
    print("=" * 72)
    print("item:", item["id"])
    if opts is None:
        print("  FORMAT FLAG: could not parse four A: B: C: D: options")
        return
    counts = {k: len(v.split()) for k, v in opts.items()}
    hits = {k: trigger_hits(v) for k, v in opts.items()}
    for k in ("A", "B", "C", "D"):
        tag = (" | triggers: " + ", ".join(hits[k])) if hits[k] else ""
        print("  %s (%2d words)%s" % (k, counts[k], tag))

    flags = []
    ratio = max(counts.values()) / max(1, min(counts.values()))
    if ratio > LENGTH_SPREAD_FLAG:
        flags.append("LENGTH FLAG: option word counts spread %.2fx (max/min)" % ratio)
    nhits = sorted(((len(v), k) for k, v in hits.items()), reverse=True)
    top_n, top_k = nhits[0]
    second_n = nhits[1][0]
    if top_n >= ASYMMETRY_FLAG and (top_n - second_n) >= ASYMMETRY_FLAG:
        flags.append("GRADIENT FLAG: triggers cluster on option %s (%d vs next %d)"
                     % (top_k, top_n, second_n))
    if sum(1 for v in hits.values() if v) == 1 and top_n >= ASYMMETRY_FLAG:
        flags.append("GRADIENT FLAG: only option %s carries triggers (%d)"
                     % (top_k, top_n))
    for f in dict.fromkeys(flags):
        print("  " + f)
    if not flags:
        print("  string checks: clean")
    print("  LIVENESS (manual): write one worst-case sentence per option;")
    print("  three or more must be defensible or this is a two-way item.")

def main():
    print("Sweeping %d candidate items." % len(CANDIDATES))
    for item in CANDIDATES:
        sweep_item(item)
    print("=" * 72)
    print("Reminder: string checks catch folklore and gradients only. Liveness")
    print("is manual, and the real filter is the Haiku baseline (collision per")
    print("item at K = 10; a true four-way item measures near 0.33, a two-way")
    print("item near 0.55 and fails K1 territory).")

if __name__ == "__main__":
    main()
