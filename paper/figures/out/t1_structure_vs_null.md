## T1: breach structure against the exact no-drift null

Window 2026-08-02 to 2026-08-20, 19 probe days. Null: exact enumeration under
the smoothed baselines (recurrence_structure_null.py); the
count row is deliberately weak and reported first.

| quantity | observed | expected (null) | P(at least obs.) |
| --- | --- | --- | --- |
| breach entries | 43 | 31.206 | 0.02566 |
| distinct breached slots | 17 | 29.81 | |
| slots with >=2 breaches | 9 | 1.3550 | 1.133e-05 |
| slots with >=3 breaches | 7 | 0.042969 | 4.407e-14 |
| slots with >=5 breaches | 3 | 2.41e-05 | 2.136e-15 |
| equipoise share of entries | 43 of 43 | null mass 0.38149 | 1.009e-18 |
| equipoise share, distinct slots | 17 of 17 | | 7.678e-08 |
| unidirectional >=3-threads | 6 of 7 | 0.007581 tail at 6: 2.131e-16 | |
| unidirectional >=5-threads | 3 of 3 | 1.67e-06 tail at 3: 6.353e-19 | |

Slots within a model-day share a scaffold and are not
independent; per-slot recurrence rows are computed across
days, where the sharing argument does not apply.
