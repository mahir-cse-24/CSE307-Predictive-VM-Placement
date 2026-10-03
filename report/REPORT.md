# Predictive Virtual Machine Placement Under a Mid-Trace Demand Shift

**Lt Chowdhury Mahir Muhibbullah - 202214172 - CSE-24**

## Abstract

Static VM placement uses demand visible at allocation time. This can become fragile after a workload change. The project compares First-Fit, Best-Fit, and a lightweight online linear-regression predictor. The predictor uses a six-sample history and a 0.90 headroom target. In the ten-seed main experiment, predictive placement achieved utilization imbalance 0.2485, 21.1 overload/SLA events, and 27.5 migrations, compared with 0.2937/38.8/31.4 for First-Fit and 0.2918/33.7/31.2 for Best-Fit.

## Method

The simulation uses 8 homogeneous hosts, 20 VMs, 120 steps, and a workload shift at step 60. Seven VMs enter a ten-step rising demand ramp with additional short bursts. First-Fit chooses the first feasible host; Best-Fit chooses the feasible host with the smallest remaining capacity. The predictive method trains a shared linear regression from past VM histories. Its features are the four latest loads, rolling mean, rolling standard deviation, mean change, and the change across the six-sample window.

## Results

Predictive placement reduces utilization imbalance by 15.4% relative to First-Fit and 14.9% relative to Best-Fit. Overload events fall by 45.6% and 37.4%, respectively. Paired Wilcoxon tests on the same ten seeds show lower utilization imbalance and overload counts for the predictive policy, while migration-count differences are not statistically significant.

## Research extensions

Regression forecasting has MAE 0.0265 and R2 0.9302. A persistence predictor has MAE 0.0271 and R2 0.9268. Persistence creates fewer overload events but 37.6 migrations, while regression produces 21.1 overload events and 27.5 migrations. A three-seed threshold pilot shows a trade-off between proactive headroom and overloads. The optional explanation-confidence extension records 651 proactive decisions with 95.24% empirical correctness, but its confidence score is not well calibrated (ECE 0.305).

## Research context

The related-work section connects the project to vector bin packing, dynamic VM consolidation, migration cost, and prediction-aware overload detection. The main external references are Beloglazov and Buyya (2012), Hsieh et al. (2020), Jangiti and Shankar Sriram (2018), and Awad et al. (2022).

## Limitation

The study uses one normalized resource dimension, homogeneous hosts, a one-step horizon, and a synthetic trace. It is a controlled course experiment rather than a production-cloud benchmark.

The final IEEE-format report is supplied separately as the PDF submission artifact.
