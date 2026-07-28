# Convergence analysis (pre-registered)

Spec: convergence/PRE_REGISTRATION_CONVERGENCE.md, lock tag prereg-lock-convergence-2026-07-24, Deviations through 2026-07-25. Cluster bootstrap over items, B = 2000, seed 20260722, percentile 90% intervals.

## Integrity

| model | arm | rows | unparsed | rate | echo ids | tie items | dup slots |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude-haiku-4-5-20251001 | A | 680 | 0 | 0.0000 | claude-haiku-4-5-20251001 (680) | 0 | 0 |
| claude-haiku-4-5-20251001 | B | 680 | 0 | 0.0000 | claude-haiku-4-5-20251001 (680) | 1 | 0 |
| claude-opus-4-8 | A | 680 | 0 | 0.0000 | claude-opus-4-8 (680) | 0 | 0 |
| claude-opus-4-8 | B | 680 | 0 | 0.0000 | claude-opus-4-8 (680) | 0 | 0 |
| claude-sonnet-4-6 | A | 680 | 0 | 0.0000 | claude-sonnet-4-6 (680) | 1 | 0 |
| claude-sonnet-4-6 | B | 680 | 0 | 0.0000 | claude-sonnet-4-6 (680) | 0 | 0 |
| deepseek-v4-flash | A | 680 | 0 | 0.0000 | deepseek-v4-flash (680) | 5 | 0 |
| deepseek-v4-flash | B | 680 | 5 | 0.0074 | deepseek-v4-flash (680) | 1 | 0 |
| deepseek-v4-pro | A | 680 | 0 | 0.0000 | deepseek-v4-pro (680) | 0 | 0 |
| deepseek-v4-pro | B | 680 | 0 | 0.0000 | deepseek-v4-pro (680) | 0 | 0 |
| gemini-3.1-pro-preview | B | 680 | 2 | 0.0029 | gemini-3.1-pro-preview (680) | 0 | 0 |
| gemini-3.6-flash | B | 680 | 0 | 0.0000 | gemini-3.6-flash (680) | 0 | 0 |
| glm-5.2 | A | 680 | 0 | 0.0000 | glm-5.2 (680) | 1 | 0 |
| glm-5.2 | B | 680 | 53 | 0.0779 | glm-5.2 (680) | 2 | 0 |
| gpt-5.6-sol | A | 680 | 0 | 0.0000 | gpt-5.6-sol (680) | 0 | 0 |
| gpt-5.6-sol | B | 680 | 0 | 0.0000 | gpt-5.6-sol (680) | 2 | 0 |
| gpt-5.6-terra | A | 680 | 0 | 0.0000 | gpt-5.6-terra (680) | 1 | 0 |
| gpt-5.6-terra | B | 680 | 0 | 0.0000 | gpt-5.6-terra (680) | 0 | 0 |

## Voids

- Arm A: no model voided (all unparsed rates at or below 0.20).
- Arm B: no model voided (all unparsed rates at or below 0.20).

## Primary (Arm A)

Models: claude-haiku-4-5-20251001, claude-sonnet-4-6, claude-opus-4-8, gpt-5.6-terra, gpt-5.6-sol, deepseek-v4-flash, deepseek-v4-pro, glm-5.2.

| quantity | value |
| --- | --- |
| within-lab, lab-balanced | 0.8905 |
| within-lab, pair-weighted | 0.9029 |
| within-lab mean, anthropic | 0.9216 |
| within-lab mean, deepseek | 0.8382 |
| within-lab mean, openai | 0.9118 |
| cross-lab mean | 0.8593 |
| difference (lab-balanced within minus cross) | 0.0312 |
| 90% interval | [0.0072, 0.0583] |

**Decision:** Within-lab agreement exceeds cross-lab agreement: within-lab (lab-balanced) 0.8905, cross-lab 0.8593, difference +0.0312, 90% interval [+0.0072, +0.0583].

Absolute cross-lab agreement 0.8593, against 0.25 (chance on four options) and 1.00 (identical judgment). Agreement is not accuracy.

## Sensitivities (reported alongside the primary, never substituted)

### 1. Excluding unparsed rate > 0.10

Excluded: none. Within (lab-balanced) 0.8905, cross 0.8593, difference 0.0312, 90% interval [0.0072, 0.0583]. Identical to the primary (no model excluded).

### 2. Single Anthropic representative (three recomputes)

| sole representative | within (lab-balanced) | cross | diff | 90% interval |
| --- | --- | --- | --- | --- |
| claude-haiku-4-5-20251001 | 0.8750 | 0.8507 | 0.0243 | [-0.0062, 0.0583] |
| claude-opus-4-8 | 0.8750 | 0.8518 | 0.0232 | [-0.0096, 0.0589] |
| claude-sonnet-4-6 | 0.8750 | 0.8495 | 0.0255 | [-0.0057, 0.0605] |

Difference range across the three recomputes: [0.0232, 0.0255]. each recompute removes all Anthropic within-lab pairs by construction; no single representative is designated.

### 3. Set-intersection tie matching

Within (lab-balanced) 0.9167, cross 0.8836, difference 0.0330, 90% interval [0.0066, 0.0621].

## Secondary

### p(modal) over items (self-collision), by arm

| arm | model | mean | median | min | max |
| --- | --- | --- | --- | --- | --- |
| A | claude-haiku-4-5-20251001 | 0.9941 | 1.0000 | 0.6000 | 1.0000 |
| A | claude-opus-4-8 | 0.9956 | 1.0000 | 0.9000 | 1.0000 |
| A | claude-sonnet-4-6 | 0.9912 | 1.0000 | 0.5000 | 1.0000 |
| A | deepseek-v4-flash | 0.9191 | 1.0000 | 0.4000 | 1.0000 |
| A | deepseek-v4-pro | 0.9412 | 1.0000 | 0.5000 | 1.0000 |
| A | glm-5.2 | 0.9603 | 1.0000 | 0.5000 | 1.0000 |
| A | gpt-5.6-sol | 0.9735 | 1.0000 | 0.6000 | 1.0000 |
| A | gpt-5.6-terra | 0.9544 | 1.0000 | 0.5000 | 1.0000 |
| B | claude-haiku-4-5-20251001 | 0.9309 | 1.0000 | 0.4000 | 1.0000 |
| B | claude-opus-4-8 | 0.9853 | 1.0000 | 0.7000 | 1.0000 |
| B | claude-sonnet-4-6 | 0.9750 | 1.0000 | 0.5000 | 1.0000 |
| B | deepseek-v4-flash | 0.9485 | 1.0000 | 0.4000 | 1.0000 |
| B | deepseek-v4-pro | 0.9574 | 1.0000 | 0.4000 | 1.0000 |
| B | gemini-3.1-pro-preview | 0.9827 | 1.0000 | 0.6250 | 1.0000 |
| B | gemini-3.6-flash | 0.9897 | 1.0000 | 0.8000 | 1.0000 |
| B | glm-5.2 | 0.9712 | 1.0000 | 0.5000 | 1.0000 |
| B | gpt-5.6-sol | 0.9676 | 1.0000 | 0.5000 | 1.0000 |
| B | gpt-5.6-terra | 0.9765 | 1.0000 | 0.6000 | 1.0000 |

### Tier gradient (within Anthropic, OpenAI, DeepSeek only; vendor tier order, small to flagship)

| lab | arm | tier order: mean p(modal) |
| --- | --- | --- |
| anthropic | A | claude-haiku-4-5-20251001 0.9941 -> claude-sonnet-4-6 0.9912 -> claude-opus-4-8 0.9956 |
| anthropic | B | claude-haiku-4-5-20251001 0.9309 -> claude-sonnet-4-6 0.9750 -> claude-opus-4-8 0.9853 |
| deepseek | A | deepseek-v4-flash 0.9191 -> deepseek-v4-pro 0.9412 |
| deepseek | B | deepseek-v4-flash 0.9485 -> deepseek-v4-pro 0.9574 |
| openai | A | gpt-5.6-terra 0.9544 -> gpt-5.6-sol 0.9735 |
| openai | B | gpt-5.6-terra 0.9765 -> gpt-5.6-sol 0.9676 |

### Arm A versus Arm B (descriptive)

Arm A versus Arm B is descriptive and confounded by construction: reasoning means adaptive on one lab, a token budget on another, and always-on elsewhere, and Arm B adds Google. It is the deployed-configuration comparison, never a controlled contrast.

| arm | within (lab-balanced) | within (pair-weighted) | cross | diff | 90% interval |
| --- | --- | --- | --- | --- | --- |
| A | 0.8905 | 0.9029 | 0.8593 | 0.0312 | [0.0072, 0.0583] |
| B | 0.9032 | 0.9142 | 0.9020 | 0.0012 | [-0.0162, 0.0178] |

### Pair agreement matrices

Arm A (models in roster order):

| | claude-haiku-4-5-20251001 | claude-sonnet-4-6 | claude-opus-4-8 | gpt-5.6-terra | gpt-5.6-sol | deepseek-v4-flash | deepseek-v4-pro | glm-5.2 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| claude-haiku-4-5-20251001 | - | 0.9706 | 0.8971 | 0.8382 | 0.9118 | 0.8529 | 0.8529 | 0.8971 |
| claude-sonnet-4-6 | 0.9706 | - | 0.8971 | 0.8382 | 0.9118 | 0.8529 | 0.8382 | 0.8971 |
| claude-opus-4-8 | 0.8971 | 0.8971 | - | 0.8824 | 0.9265 | 0.8088 | 0.8529 | 0.8971 |
| gpt-5.6-terra | 0.8382 | 0.8382 | 0.8824 | - | 0.9118 | 0.7794 | 0.8382 | 0.8824 |
| gpt-5.6-sol | 0.9118 | 0.9118 | 0.9265 | 0.9118 | - | 0.8088 | 0.8676 | 0.8824 |
| deepseek-v4-flash | 0.8529 | 0.8529 | 0.8088 | 0.7794 | 0.8088 | - | 0.8382 | 0.8235 |
| deepseek-v4-pro | 0.8529 | 0.8382 | 0.8529 | 0.8382 | 0.8676 | 0.8382 | - | 0.8235 |
| glm-5.2 | 0.8971 | 0.8971 | 0.8971 | 0.8824 | 0.8824 | 0.8235 | 0.8235 | - |

Arm B (models in roster order):

| | claude-haiku-4-5-20251001 | claude-sonnet-4-6 | claude-opus-4-8 | gpt-5.6-terra | gpt-5.6-sol | deepseek-v4-flash | deepseek-v4-pro | glm-5.2 | gemini-3.6-flash | gemini-3.1-pro-preview |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| claude-haiku-4-5-20251001 | - | 0.9412 | 0.9265 | 0.8824 | 0.9118 | 0.8676 | 0.9118 | 0.9118 | 0.8824 | 0.9118 |
| claude-sonnet-4-6 | 0.9412 | - | 0.9412 | 0.8824 | 0.9118 | 0.8971 | 0.9265 | 0.9118 | 0.9118 | 0.9412 |
| claude-opus-4-8 | 0.9265 | 0.9412 | - | 0.8824 | 0.9265 | 0.8824 | 0.8971 | 0.9265 | 0.9118 | 0.9118 |
| gpt-5.6-terra | 0.8824 | 0.8824 | 0.8824 | - | 0.8824 | 0.8235 | 0.8824 | 0.8824 | 0.8824 | 0.8824 |
| gpt-5.6-sol | 0.9118 | 0.9118 | 0.9265 | 0.8824 | - | 0.8971 | 0.9118 | 0.9265 | 0.9412 | 0.9118 |
| deepseek-v4-flash | 0.8676 | 0.8971 | 0.8824 | 0.8235 | 0.8971 | - | 0.8971 | 0.8971 | 0.8824 | 0.8676 |
| deepseek-v4-pro | 0.9118 | 0.9265 | 0.8971 | 0.8824 | 0.9118 | 0.8971 | - | 0.9265 | 0.9265 | 0.9118 |
| glm-5.2 | 0.9118 | 0.9118 | 0.9265 | 0.8824 | 0.9265 | 0.8971 | 0.9265 | - | 0.8971 | 0.9265 |
| gemini-3.6-flash | 0.8824 | 0.9118 | 0.9118 | 0.8824 | 0.9412 | 0.8824 | 0.9265 | 0.8971 | - | 0.8971 |
| gemini-3.1-pro-preview | 0.9118 | 0.9412 | 0.9118 | 0.8824 | 0.9118 | 0.8676 | 0.9118 | 0.9265 | 0.8971 | - |

Per-item and per-pair records: per_item.csv, per_pair.csv. Test-retest supplement (corroborative, never entering the primary): test_retest.md / test_retest.json.

