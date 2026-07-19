"""
Bank integrity test for the v1.5 bank edit (thirteen round-two screened
candidates merged into items/items.py).

Pins:
  1. len(ITEMS) == 68, with 45 derivable and 23 equipoise items.
  2. All item ids unique.
  3. Every item has non-empty id, decision, and cell fields.
  4. The thirteen merged ids are present with cell "equipoise" and their
     decision strings byte-identical to their items/candidate_sweep.py
     CANDIDATES source (this enforces verbatim, no rewording).
  5. No eq_seed_* item (seeds and the antiexample) leaked into the bank.

Run: python tests/test_bank_integrity.py   (plain asserts, exit 1 on failure;
also collectable by pytest). No network, no file dependencies.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from items.items import ITEMS  # noqa: E402
from items.candidate_sweep import CANDIDATES  # noqa: E402

MERGED_IDS = [
    "eq_alert_waf_mode_v2",
    "eq_alert_fraud_scoring_v2",
    "eq_alert_vuln_gating_v2",
    "eq_alert_spend_anomaly_v2",
    "eq_alert_dlp_email_v2",
    "eq_access_cert_cadence",
    "eq_access_priv_groups",
    "eq_access_contractor",
    "eq_access_service_accounts",
    "eq_access_offboarding",
    "eq_access_oauth_grants",
    "eq_access_share_links",
    "eq_access_breakglass",
]


def run():
    fails = []

    def check(name, cond, got=None):
        if cond:
            print("  PASS: %s" % name)
        else:
            print("  FAIL: %s | got %r" % (name, got))
            fails.append(name)

    bank_by_id = {i["id"]: i for i in ITEMS if isinstance(i, dict) and "id" in i}
    cand_by_id = {c["id"]: c for c in CANDIDATES}

    print("=== bank size and cell counts ===")
    check("len(ITEMS) == 68", len(ITEMS) == 68, len(ITEMS))
    n_derivable = sum(1 for i in ITEMS if i.get("cell") == "derivable")
    n_equipoise = sum(1 for i in ITEMS if i.get("cell") == "equipoise")
    check("45 derivable items", n_derivable == 45, n_derivable)
    check("23 equipoise items", n_equipoise == 23, n_equipoise)

    print("=== id uniqueness and required fields ===")
    ids = [i.get("id") for i in ITEMS]
    dupes = sorted({x for x in ids if ids.count(x) > 1})
    check("all ids unique", not dupes, dupes)
    bad_fields = [i.get("id") for i in ITEMS
                  if not all(isinstance(i.get(k), str) and i.get(k)
                             for k in ("id", "decision", "cell"))]
    check("every item has non-empty id, decision, cell", not bad_fields, bad_fields)

    print("=== thirteen merged items: presence, cell, verbatim decision ===")
    for mid in MERGED_IDS:
        item = bank_by_id.get(mid)
        if item is None:
            check("%s present in bank" % mid, False, "missing")
            continue
        check("%s cell == equipoise" % mid, item.get("cell") == "equipoise",
              item.get("cell"))
        src = cand_by_id.get(mid)
        if src is None:
            check("%s present in CANDIDATES source" % mid, False, "missing")
            continue
        check("%s decision byte-identical to CANDIDATES" % mid,
              item.get("decision") == src["decision"],
              "mismatch" if item.get("decision") != src["decision"] else None)

    print("=== seeds and antiexample stay out of the bank ===")
    leaked_seeds = sorted(x for x in bank_by_id if x.startswith("eq_seed_"))
    check("no eq_seed_* id in the bank", not leaked_seeds, leaked_seeds)

    print()
    print("FAILURES: %d %s" % (len(fails), fails if fails else "- ALL PASS"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(run())


def test_bank_integrity():  # pytest entry point
    assert run() == 0
