# CSE-307 submission checklist

## Before submitting

- [ ] Run all five Ubuntu/VMware resource conditions.
- [ ] Use the same `results/workload_trace.csv` for all five conditions.
- [ ] Keep the SHA-256 trace hash unchanged across runs.
- [ ] Complete three runs for each condition.
- [ ] Run `python3 src/analyze_system.py`.
- [ ] Run `python3 src/plot_system.py`.
- [ ] Check `results/system_experiment.csv` for all expected rows.
- [ ] Check `results/system_summary.csv`.
- [ ] Put the measured values into the primary result table in `report/term_paper.tex`.
- [ ] Compile the LaTeX report and confirm it is 3-4 pages.
- [ ] Open the compiled PDF and check the tables, figures, references, and student information.
- [ ] Run the repository tests.

## Required submission items

The course instruction asks for a GitHub repository and a 3-4 page PDF term paper. The report should contain in-text citations and references, and the workload must remain the same across experiments.

Submit:

1. GitHub repository: `https://github.com/mahir-cse-24/CSE307-Predictive-VM-Placement`
2. Compiled IEEE PDF.
3. Printed copy, where required by the course.
4. The 3-5 minute walkthrough/demo.

The repository also keeps the predictive VM-placement study as a separate extension. That material remains in the GitHub submission because it covers the retained Track 4 requirements.

## Walkthrough order

1. State the research question and show the five VM configurations.
2. Show that one workload trace is reused in every condition.
3. Show the OS counters collected from Ubuntu.
4. Explain the measured changes in memory pressure and CPU allocation.
5. Briefly show the retained predictive placement results and why it is labelled as an extension.

## Result integrity

The Ubuntu/VMware measurements must come from the actual Ubuntu guest. Do not replace missing measurements with values from another computer, a simulation, or an example.
