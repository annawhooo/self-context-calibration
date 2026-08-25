## T1: breach structure against the exact no-drift null

Window 2026-08-02 to 2026-08-25, 24 probe days. Null: exact enumeration under
the smoothed baselines (recurrence_structure_null.py); the
count row is deliberately weak and reported first.

| quantity | observed | expected (null) | P(at least obs.) |
| --- | --- | --- | --- |
| breach entries | 51 | 39.424 | 0.04273 |
| distinct breached slots | 17 | 37.19 | |
| slots with >=2 breaches | 10 | 2.1474 | 7.396e-05 |
| slots with >=3 breaches | 7 | 0.087680 | 6.274e-12 |
| slots with >=5 breaches | 5 | 8.516e-05 | 2.809e-23 |
| equipoise share of entries | 51 of 51 | null mass 0.38159 | 4.584e-22 |
| equipoise share, distinct slots | 17 of 17 | | 7.71e-08 |
| unidirectional >=3-threads | 6 of 7 | 0.015361 tail at 6: 1.471e-14 | |
| unidirectional >=5-threads | 4 of 5 | 5.864e-06 tail at 4: 3.307e-23 | |

Slots within a model-day share a scaffold and are not
independent; per-slot recurrence rows are computed across
days, where the sharing argument does not apply.
