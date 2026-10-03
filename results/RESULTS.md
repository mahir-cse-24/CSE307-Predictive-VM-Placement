# Experimental Results

Experiment: 8 hosts, 20 VMs, 120 steps, shift at step 60, ten seeds (100-109).

| Policy | Utilization balance (mean std.) | Post-shift utilization std. | Overload events | Post-shift overload events | Migrations |
|---|---:|---:|---:|---:|---:|
| First-Fit | 0.2874 +/- 0.0116 | 0.1859 | 34.6 +/- 13.9 | 29.6 | 25.5 +/- 5.0 |
| Best-Fit | 0.2921 +/- 0.0150 | 0.1954 | 40.8 +/- 15.9 | 35.5 | 29.1 +/- 6.0 |
| Predictive | 0.2468 +/- 0.0132 | 0.1586 | 23.9 +/- 27.7 | 23.9 | 27.7 +/- 7.5 |

For this synthetic workload, predictive placement reduced overall overload events by about 30.9% relative to First-Fit and 41.4% relative to Best-Fit. It reduced mean utilization imbalance by about 14.1% and 15.5%, respectively. The predictive migration count was 8.6% higher than First-Fit and 4.8% lower than Best-Fit.

Optional explanation-confidence extension: 277 proactive decisions, 99.28% empirical correctness, mean confidence 0.786. The two incorrect decisions had mean confidence 0.842, versus 0.786 for correct decisions, so the simple confidence rule was not well calibrated.
