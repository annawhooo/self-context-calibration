## T1: breach structure against the exact no-drift null

Window 2026-08-02 to 2026-09-26, 56 calendar days (55 with a probe). Null:
exact enumeration under the smoothed baselines
(recurrence_structure_null.py), charging every arm for all 56
days; the count row is deliberately weak and reported first.

| quantity | observed | expected (null) | P(at least obs.) |
| --- | --- | --- | --- |
| breach entries | 75 | 92.143 | 0.9705 |
| distinct breached slots | 17 | 80.31 | |
| slots with >=2 breaches | 14 | 10.7032 | 0.1877 |
| slots with >=3 breaches | 13 | 1.041844 | 6.699e-11 |
| slots with >=5 breaches | 7 | 0.006255 | 4.384e-20 |
| equipoise share of entries | 75 of 75 | null mass 0.38262 | 5.104e-32 |
| equipoise share, distinct slots | 17 of 17 | | 8.075e-08 |
| unidirectional >=3-threads, joint with clustering | 10 of 13 | 0.174933 tail at 10: 3.779e-15 | |
| unidirectional >=5-threads, joint with clustering | 5 of 7 | 0.0004102 tail at 5: 5.167e-20 | |
| unidirectional >=3-threads, given the 13 threads | 10 of 13 | 1.64 | 6.8e-10 |
| unidirectional >=5-threads, given the 7 threads | 5 of 7 | 0.70 | 3.3e-07 |

Slots within a model-day share a scaffold and are not
independent; per-slot recurrence rows are computed across
days, where the sharing argument does not apply.
