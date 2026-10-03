# Enhanced experimental analysis

## Primary experiment

Configuration: 8 homogeneous hosts, 20 VMs, 120 time steps, shift at step 60, ten deterministic seeds (100-109), host capacity 1.0, proactive threshold 0.90, history window 6.

| Policy | Utilization imbalance | Pre-shift std. | Post-shift std. | Overload/SLA events | Post-shift overload | Migrations |
|---|---:|---:|---:|---:|---:|---:|
| First-Fit | 0.2937 | 0.3886 | 0.1988 | 38.8 | 33.9 | 31.4 |
| Best-Fit | 0.2918 | 0.3901 | 0.1934 | 33.7 | 28.7 | 31.2 |
| Predictive | 0.2485 | 0.3385 | 0.1585 | 21.1 | 21.1 | 27.5 |

Predictive placement reduced utilization imbalance by 15.4% versus First-Fit and 14.9% versus Best-Fit. Overload events fell by 45.6% and 37.4%, respectively.

## Paired statistical check

Because the same ten seeds are used for each policy, paired Wilcoxon signed-rank tests are used as a robustness check. Predictive utilization imbalance is lower than First-Fit (p=0.00195) and Best-Fit (p=0.00195). Overload events are also lower than First-Fit (p=0.00195) and Best-Fit (p=0.01953). Migration-count differences are not statistically significant (p=0.31055 versus First-Fit; p=0.18750 versus Best-Fit). These p-values describe the ten synthetic seeds only.

## Predictor ablation

Regression produces mean one-step MAE 0.0265, RMSE 0.0367, and R2 0.9302. Persistence produces MAE 0.0271, RMSE 0.0375, and R2 0.9268.

Persistence results in fewer overload events (16.0) but 37.6 migrations. Regression produces 21.1 overload events and 27.5 migrations. The small forecast-error advantage of regression therefore does not translate into a win on every scheduling metric.

## Threshold sensitivity pilot

A small three-seed pilot (100-102) varies the proactive threshold. Mean post-shift overload events are 67.7 at 0.85, 41.7 at 0.90, and 30.7 at 0.95. Mean migrations are 31.0, 26.7, and 26.7. The pilot is intentionally treated as a sensitivity check rather than a final optimization study.

## Confidence extension

The rule-based explanation extension produced 651 proactive decisions. Accuracy was 95.24%, mean confidence was 64.71%, Brier score was 0.161, and ECE was 0.305. Incorrect decisions had slightly higher mean confidence than correct decisions. The confidence score is therefore useful for auditing but is not well calibrated.
