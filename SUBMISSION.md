# CSE-307 submission checklist

## Online submission

Submit the GitHub repository:

https://github.com/mahir-cse-24/CSE307-Predictive-VM-Placement

Submit the separate three-page IEEE PDF report.

If the course portal accepts an additional archive, submit the complete ZIP as a backup.

## What the repository contains

- source code for First-Fit, Best-Fit, regression-based prediction, and the reactive/proactive placement logic;
- unit tests;
- reproducible workload generation with fixed seeds;
- main results and statistical analysis;
- predictor ablation;
- threshold-sensitivity pilot;
- optional explanation-confidence analysis;
- research notes and related-work references;
- GitHub Actions workflow for automated tests.

## 3-5 minute walkthrough

1. Define the problem: static placement uses current load; the workload changes at step 60.
2. Explain First-Fit and Best-Fit.
3. Show the regression features and 0.90 proactive threshold.
4. Show the main result table and the post-shift comparison.
5. Mention the statistical check, predictor ablation, and optional confidence extension.
6. State the limitations: one normalized resource, homogeneous hosts, one-step forecast, synthetic trace.

## Important interpretation

The paper does not claim that predictive placement is universally better. The experiment supports the conclusion only for the tested synthetic configuration. The migration result is treated separately from utilization and SLA events, and the optional confidence score is explicitly reported as poorly calibrated.

## Printed copy

The course guideline requires a printed report and a 3-5 minute in-class walkthrough in addition to the GitHub link and soft-copy PDF.
