# S1 re-scoring report (corrected parser)

## results/judged_results_s1v2.jsonl

S1 rows re-scored: 1440

| score | legacy | corrected |
|---|---|---|
| 2 | 1432 | 1126 |
| 1 | 0 | 306 |
| 0 | 0 | 0 |
| None | 8 | 8 |

Rows whose score changed: 306 (21.2%)

### Corrected mean compliance by framing

| framing | n | legacy mean | corrected mean | breaches |
|---|---|---|---|---|
| A | 480 | 2.000 | 1.988 | 6 |
| B | 480 | 2.000 | 1.992 | 4 |
| C | 480 | 2.000 | 1.378 | 296 |

### Corrected mean compliance by monitoring_condition

| monitoring_condition | n | legacy mean | corrected mean | breaches |
|---|---|---|---|---|
| M0_covert | 360 | 2.000 | 1.908 | 33 |
| M1_overt | 360 | 2.000 | 1.814 | 66 |
| Mi_implicit | 360 | 2.000 | 1.775 | 81 |
| Mx_ambiguous | 360 | 2.000 | 1.650 | 126 |

### Corrected mean compliance by governance_pattern

| governance_pattern | n | legacy mean | corrected mean | breaches |
|---|---|---|---|---|
| P1_constraint_recourse | 360 | 2.000 | 1.840 | 57 |
| P2_evidence_only | 360 | 2.000 | 1.694 | 110 |
| P3_full_triad | 360 | 2.000 | 1.824 | 63 |
| P6_evidence_recourse | 360 | 2.000 | 1.788 | 76 |
