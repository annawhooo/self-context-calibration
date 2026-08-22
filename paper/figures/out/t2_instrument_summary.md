## T2: instrument summary

| parameter | value |
| --- | --- |
| item bank | 68 forced-choice judgment items (45 decisive, 23 designed-equipoise) |
| models | 5 production APIs, one pinned arm each |
| alarm slots | 340 (115 equipoise), zero sentinels |
| cadence | daily, 13:00 UTC, K=10 samples per item |
| baseline | frozen n=20 per slot (two pooled same-day K=10 runs, 2026-08-02) |
| alarm bands (p99) | 0.40 x311, 0.45 x28, 0.50 x1 |
| breach test | per-item TVD vs baseline, strictly above band; same-day rerun disambiguates |
| verdict grammar | CLEAN, EVENT, TRANSIENT, UNSTABLE, ECHO_CHANGE, ERROR |
| expected false breaches | 1.64/day (smoothed truth), 0.05/day (empirical truth), exact enumeration |
| record to date | 19 probe days, 60,270 calls |
| operating cost | about 20 USD per month |
