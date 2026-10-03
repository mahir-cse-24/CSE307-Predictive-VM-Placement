# CSE-307 Track 4 - Predictive VM Placement

**Student:** Lt Chowdhury Mahir Muhibbullah  
**Student ID:** 202214172  
**Section:** CSE-24  
**Course:** CSE-307 Operating Systems, Spring 2026

## Project scope

This repository implements Track 4 of the CSE-307 term-paper brief:

- static First-Fit VM-to-host placement,
- static Best-Fit VM-to-host placement,
- a lightweight regression model that predicts near-future VM load and places VMs proactively,
- a synthetic multi-VM workload with a deliberate shift at step 60,
- host-utilization balance, overload/SLA events, and migration count,
- the optional explanation-confidence extension.

The primary experiment uses 8 homogeneous hosts, 20 VMs, 120 simulation steps, and ten deterministic seeds (100-109). Seven VMs enter a rising demand regime at step 60 and the post-shift phase also contains short bursts.

## Main results

| Policy | Utilization imbalance | Overload/SLA events | Migrations |
|---|---:|---:|---:|
| First-Fit | 0.2937 | 38.8 | 31.4 |
| Best-Fit | 0.2918 | 33.7 | 31.2 |
| Predictive regression | 0.2485 | 21.1 | 27.5 |

Relative to First-Fit, predictive placement reduced mean utilization imbalance by about 15.4% and overload events by about 45.6%. Relative to Best-Fit, the reductions were about 14.9% and 37.4%. Migration count was also lower in the primary experiment.

A paired Wilcoxon check on the ten seeds found lower utilization imbalance for predictive placement than both First-Fit and Best-Fit (p=0.00195 for each comparison). Overload counts were also lower (p=0.00195 versus First-Fit and p=0.01953 versus Best-Fit). Migration-count differences were not statistically significant.

## Why the predictive policy is different

The predictor is a shared online linear-regression model. It uses a six-sample VM history and four recent load values, rolling mean, rolling standard deviation, mean load change, and oldest-to-newest change in the window.

The model only sees history available before the placement decision. A host projected above the 0.90 proactive threshold becomes a candidate for repair. A VM is moved only when another host can remain at or below the threshold after the move.

## Research extensions

Predictor ablation compares regression with a persistence forecast that carries the latest load forward. Regression gives MAE 0.0265, RMSE 0.0367, and R2 0.9302. Persistence gives MAE 0.0271, RMSE 0.0375, and R2 0.9268. Regression therefore predicts slightly better, while persistence produces fewer overload events but many more migrations. This shows why forecast error and scheduler quality should not be treated as the same objective.

A small threshold-sensitivity pilot tests proactive thresholds of 0.85, 0.90, and 0.95 on seeds 100-102. Mean post-shift overload events are 67.7, 41.7, and 30.7, while mean migrations are 31.0, 26.7, and 26.7. The pilot is a sensitivity check, not a final threshold optimization study.

## Optional +10 explanation-confidence extension

The rule-based extension generated 651 proactive decisions. Empirical correctness was 95.24%, mean confidence was 64.71%, Brier score was 0.161, and expected calibration error was 0.305. Incorrect decisions had slightly higher mean confidence than correct decisions, so the confidence score is not a calibrated probability. Each decision still leaves an auditable explanation record.

## Research context

The paper adds a short related-work review on VM placement as bin/vector packing, dynamic VM consolidation and migration cost, and utilization prediction for overload detection. The main external references are Beloglazov and Buyya (2012), Hsieh et al. (2020), Jangiti and Shankar Sriram (2018), and Awad et al. (2022). Their systems are larger and more complex than this course experiment; they are used to frame the design rather than to claim that this implementation matches a production scheduler.

See the research directory for the extended discussion.

## Reproducibility

Install the dependencies with:

    python -m pip install -r requirements.txt

Run the main experiment with:

    python src/vm_placement.py --seeds 10 --out-dir results

Run the statistical and bonus analysis with:

    python src/research_analysis.py
    python src/sensitivity.py

Run tests with:

    python -m pytest -q

The repository includes a GitHub Actions test workflow.

## Repository structure

src/
  vm_placement.py
  research_analysis.py
  sensitivity.py
  plot_results.py

tests/
  test_vm_placement.py

results/
  RESULTS.md
  primary_summary.csv
  statistical_tests.csv
  predictor_ablation.csv
  confidence_summary.csv
  threshold_sensitivity.csv

figures/
  main_results.svg
  pre_post_shift.svg
  predictor_ablation.svg
  threshold_sensitivity.svg

research/
  related_work.md
  experimental_analysis.md

report/
  REPORT.md

## AI assistance disclosure

ChatGPT was used for implementation scaffolding, debugging support, literature-search support, and document editing. The experiment uses fixed seeds and executable source so that the student can rerun and inspect the work. The CSE-307 brief requires the experimental design, results, and analysis to be understood and owned by the student.

## Submission

Submit the GitHub repository together with the separate 3-page IEEE PDF report. The course brief also requires a short in-class walkthrough/demo.
