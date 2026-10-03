# Experimental results

Primary experiment: 8 hosts, 20 VMs, 120 steps, shift at step 60, ten deterministic seeds (100-109).

| Policy | Utilization imbalance | Pre-shift std. | Post-shift std. | Overload/SLA events | Post-shift overload | Migrations |
|---|---:|---:|---:|---:|---:|---:|
| First-Fit | 0.2937 | 0.3886 | 0.1988 | 38.8 | 33.9 | 31.4 |
| Best-Fit | 0.2918 | 0.3901 | 0.1934 | 33.7 | 28.7 | 31.2 |
| Predictive | 0.2485 | 0.3385 | 0.1585 | 21.1 | 21.1 | 27.5 |

Predictive placement reduced mean utilization imbalance by 15.4% versus First-Fit and 14.9% versus Best-Fit. Overload events were reduced by 45.6% and 37.4%, respectively. The primary run also used fewer migrations.

## Paired statistical check

- Utilization imbalance: predictive vs First-Fit p=0.00195; predictive vs Best-Fit p=0.00195.
- Overload events: predictive vs First-Fit p=0.00195; predictive vs Best-Fit p=0.01953.
- Migration count: predictive vs First-Fit p=0.31055; predictive vs Best-Fit p=0.18750.

These tests describe the ten synthetic seeds and should not be treated as evidence of universal superiority.

## Predictor ablation

Regression: MAE 0.0265, RMSE 0.0367, R2 0.9302.

Persistence: MAE 0.0271, RMSE 0.0375, R2 0.9268.

Persistence produced fewer overload events (16.0) but more migrations (37.6), while regression produced 21.1 overload events and 27.5 migrations.

## Optional confidence extension

651 proactive decisions; 95.24% empirical correctness; 64.71% mean confidence; Brier 0.161; ECE 0.305.

## Threshold sensitivity pilot

Using seeds 100-102 only:

| Threshold | Mean post-shift overload | Mean migrations |
|---:|---:|---:|
| 0.85 | 67.7 | 31.0 |
| 0.90 | 41.7 | 26.7 |
| 0.95 | 30.7 | 26.7 |

This pilot is included to show sensitivity, not to claim a globally optimal threshold.
