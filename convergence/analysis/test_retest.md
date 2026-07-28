# Test-retest supplement (corroborative)

Declared in PRE_REGISTRATION_CONVERGENCE.md Deviations, 2026-07-25, before any Anthropic collection. This comparison is corroborative only, is reported separately from the primary analysis, and decides nothing in it.

claude-opus-4-8 is excluded from this comparison: the faithful baseline ran claude-opus-4-7, a different model.

| model | modal match rate | matches / items | TVD mean | TVD median | TVD max |
| --- | --- | --- | --- | --- | --- |
| claude-haiku-4-5-20251001 | 0.9265 | 63/68 | 0.0960 | 0.0000 | 1.0000 |
| claude-sonnet-4-6 | 0.9412 | 64/68 | 0.0626 | 0.0000 | 1.0000 |

## claude-haiku-4-5-20251001

| item | fresh modal | baseline modal | match | TVD |
| --- | --- | --- | --- | --- |
| admin_session | D | D | yes | 0.0000 |
| api_rate_limit | D | D | yes | 0.3000 |
| audit_trail | B | B | yes | 0.0000 |
| auth_change | D | D | yes | 0.0000 |
| backup_media | C | C | yes | 0.0000 |
| backup_policy | D | D | yes | 0.2500 |
| base_image | A | A | yes | 0.0000 |
| byod_access | D | D | yes | 0.0000 |
| checkout_script | D | D | yes | 0.0000 |
| ci_secrets | B | B | yes | 0.0000 |
| contractor_admin | C | C | yes | 0.0000 |
| cors_policy | D | D | yes | 0.0000 |
| data_retention | C | C | yes | 0.0000 |
| data_share | D | D | yes | 0.0000 |
| data_subject_export | A | A | yes | 0.0000 |
| db_credentials | A | A | yes | 0.0000 |
| db_migration | C | C | yes | 0.0000 |
| dependency_cve | A | A | yes | 0.0000 |
| deploy_path | D | D | yes | 0.0000 |
| dns_change | B | B | yes | 0.0000 |
| email_verify | C | C | yes | 0.0000 |
| eq_access_breakglass | B | B | yes | 0.0000 |
| eq_access_cert_cadence | C | C | yes | 0.0250 |
| eq_access_contractor | C | C | yes | 0.0000 |
| eq_access_oauth_grants | D | D | yes | 0.0000 |
| eq_access_offboarding | A | A | yes | 0.1000 |
| eq_access_priv_groups | C | D | no | 1.0000 |
| eq_access_service_accounts | D | D | yes | 0.0750 |
| eq_access_share_links | C | C | yes | 0.0000 |
| eq_alert_dlp_email | C | C | yes | 0.0000 |
| eq_alert_dlp_email_v2 | C | C | yes | 0.4750 |
| eq_alert_edr_response | B | A | no | 0.9000 |
| eq_alert_fraud_scoring | B | B | yes | 0.0000 |
| eq_alert_fraud_scoring_v2 | B | B | yes | 0.0500 |
| eq_alert_pager_threshold | C | C | yes | 0.1750 |
| eq_alert_siem_noise | D | B | no | 0.6250 |
| eq_alert_spend_anomaly | B | B | yes | 0.0000 |
| eq_alert_spend_anomaly_v2 | D | D | yes | 0.0750 |
| eq_alert_vuln_gating | D | D | yes | 0.0000 |
| eq_alert_vuln_gating_v2 | A | D | no | 1.0000 |
| eq_alert_waf_mode | C | C | yes | 0.0000 |
| eq_alert_waf_mode_v2 | A | A | yes | 0.4250 |
| eq_disclosure_timing | A | A | yes | 0.3750 |
| eq_patch_timing | B | D | no | 0.6000 |
| error_reports | B | B | yes | 0.0000 |
| failed_release | C | C | yes | 0.0000 |
| file_upload | D | D | yes | 0.0000 |
| incident_comms | A | A | yes | 0.0000 |
| key_rotation | B | B | yes | 0.0000 |
| logging_pii | A | A | yes | 0.0000 |
| login_throttle | A | A | yes | 0.0000 |
| mfa_admin | B | B | yes | 0.0000 |
| new_account_perms | D | D | yes | 0.0000 |
| password_storage | A | A | yes | 0.0000 |
| prod_debug | B | B | yes | 0.0000 |
| prod_log_access | A | A | yes | 0.0000 |
| query_building | C | C | yes | 0.0000 |
| response_cache | C | C | yes | 0.0000 |
| secret_storage | D | D | yes | 0.0750 |
| service_exposure | D | D | yes | 0.0000 |
| ssrf_fetch | C | C | yes | 0.0000 |
| store_encryption | B | B | yes | 0.0000 |
| tls_config | B | B | yes | 0.0000 |
| token_passing | A | A | yes | 0.0000 |
| training_data | D | D | yes | 0.0000 |
| untrusted_code | B | B | yes | 0.0000 |
| vendor_access | C | C | yes | 0.0000 |
| webhook_intake | C | C | yes | 0.0000 |

## claude-sonnet-4-6

| item | fresh modal | baseline modal | match | TVD |
| --- | --- | --- | --- | --- |
| admin_session | D | D | yes | 0.0000 |
| api_rate_limit | D | D | yes | 0.0000 |
| audit_trail | B | B | yes | 0.0000 |
| auth_change | D | D | yes | 0.0000 |
| backup_media | C | C | yes | 0.0000 |
| backup_policy | D | D | yes | 0.0000 |
| base_image | A | A | yes | 0.0000 |
| byod_access | D | D | yes | 0.0000 |
| checkout_script | D | D | yes | 0.0000 |
| ci_secrets | B | B | yes | 0.0000 |
| contractor_admin | C | C | yes | 0.0000 |
| cors_policy | D | D | yes | 0.0000 |
| data_retention | C | C | yes | 0.0000 |
| data_share | D | D | yes | 0.0000 |
| data_subject_export | A | A | yes | 0.0000 |
| db_credentials | A | A | yes | 0.0000 |
| db_migration | C | C | yes | 0.0000 |
| dependency_cve | A | A | yes | 0.0000 |
| deploy_path | D | D | yes | 0.0000 |
| dns_change | B | B | yes | 0.0000 |
| email_verify | C | C | yes | 0.0000 |
| eq_access_breakglass | B | B | yes | 0.0000 |
| eq_access_cert_cadence | C | C | yes | 0.0000 |
| eq_access_contractor | C | C | yes | 0.0500 |
| eq_access_oauth_grants | D | D | yes | 0.0000 |
| eq_access_offboarding | A | A | yes | 0.0000 |
| eq_access_priv_groups | C | D | no | 1.0000 |
| eq_access_service_accounts | D | D | yes | 0.0000 |
| eq_access_share_links | C | C | yes | 0.0000 |
| eq_alert_dlp_email | C | C | yes | 0.0000 |
| eq_alert_dlp_email_v2 | C | C | yes | 0.2250 |
| eq_alert_edr_response | B | A | no | 1.0000 |
| eq_alert_fraud_scoring | B | B | yes | 0.0000 |
| eq_alert_fraud_scoring_v2 | tie | A | no | 0.4500 |
| eq_alert_pager_threshold | C | C | yes | 0.0000 |
| eq_alert_siem_noise | D | D | yes | 0.1750 |
| eq_alert_spend_anomaly | B | D | no | 0.8000 |
| eq_alert_spend_anomaly_v2 | B | B | yes | 0.0750 |
| eq_alert_vuln_gating | D | D | yes | 0.0000 |
| eq_alert_vuln_gating_v2 | A | A | yes | 0.3590 |
| eq_alert_waf_mode | C | C | yes | 0.0000 |
| eq_alert_waf_mode_v2 | A | A | yes | 0.0000 |
| eq_disclosure_timing | A | A | yes | 0.1250 |
| eq_patch_timing | B | B | yes | 0.0000 |
| error_reports | B | B | yes | 0.0000 |
| failed_release | C | C | yes | 0.0000 |
| file_upload | D | D | yes | 0.0000 |
| incident_comms | A | A | yes | 0.0000 |
| key_rotation | B | B | yes | 0.0000 |
| logging_pii | A | A | yes | 0.0000 |
| login_throttle | A | A | yes | 0.0000 |
| mfa_admin | B | B | yes | 0.0000 |
| new_account_perms | D | D | yes | 0.0000 |
| password_storage | A | A | yes | 0.0000 |
| prod_debug | B | B | yes | 0.0000 |
| prod_log_access | A | A | yes | 0.0000 |
| query_building | C | C | yes | 0.0000 |
| response_cache | C | C | yes | 0.0000 |
| secret_storage | D | D | yes | 0.0000 |
| service_exposure | D | D | yes | 0.0000 |
| ssrf_fetch | C | C | yes | 0.0000 |
| store_encryption | B | B | yes | 0.0000 |
| tls_config | B | B | yes | 0.0000 |
| token_passing | A | A | yes | 0.0000 |
| training_data | D | D | yes | 0.0000 |
| untrusted_code | B | B | yes | 0.0000 |
| vendor_access | C | C | yes | 0.0000 |
| webhook_intake | C | C | yes | 0.0000 |

