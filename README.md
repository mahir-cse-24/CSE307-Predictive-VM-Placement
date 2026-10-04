# CSE-307 Term Paper

**Title:** VM Resource Effects on an Ubuntu Workload  
**Student:** Lt Chowdhury Mahir Muhibbullah  
**Student ID:** 202214172  
**Section:** CSE-24  
**Course:** CSE-307 Operating Systems, Spring 2026

## Project scope

The main experiment runs one fixed workload inside an Ubuntu VMware guest. The VM is tested with five resource configurations:

| Condition | RAM | vCPU |
|---|---:|---:|
| A | 1 GB | 1 |
| B | 2 GB | 1 |
| C | 4 GB | 1 |
| D | 2 GB | 2 |
| E | 2 GB | 4 |

The workload trace is created once and reused in every condition. The guest records elapsed time, CPU time, minor and major page faults, context switches, swap activity, visible CPU count, guest memory, and system information.

The repository also contains a separate predictive VM-placement extension that retains the Track 4 requirements from the supplied course brief. It includes First-Fit, Best-Fit, regression-based near-future load prediction, a demand shift, utilization balance, overload/SLA events, migrations, predictor ablation, threshold sensitivity, and the explanation-confidence check.

## Repository layout

```text
src/
  system_workload.py
  collect_vm_experiment.py
  analyze_system.py
  plot_system.py
scripts/
  prepare_workload.sh
  run_condition.sh
results/
  workload_trace.csv
  system_experiment.csv
  system_summary.csv
figures/
research_extension/
report/
tests/
VMWARE_EXPERIMENT.md
SUBMISSION.md
```

## Run the main experiment

Follow `VMWARE_EXPERIMENT.md` from inside the Ubuntu guest.

Generate the workload once:

```bash
bash scripts/prepare_workload.sh
```

After each VMware resource configuration is applied, run the matching command:

```bash
bash scripts/run_condition.sh vm_1gb_1vcpu
bash scripts/run_condition.sh vm_2gb_1vcpu
bash scripts/run_condition.sh vm_4gb_1vcpu
bash scripts/run_condition.sh vm_2gb_2vcpu
bash scripts/run_condition.sh vm_2gb_4vcpu
```

Then aggregate and plot the measurements:

```bash
python3 src/analyze_system.py
python3 src/plot_system.py
```

The primary raw file is `results/system_experiment.csv`.

## Result rule

Do not enter guessed or simulated values in the Ubuntu/VMware result table. The paper must use the CSV collected inside the Ubuntu guest. The prepared package leaves those cells open until the five conditions are actually run.

## Report

The paper is written in IEEEtran LaTeX. The source is in `report/term_paper.tex`, and the compiled paper is `report/term_paper.pdf`.

The paper uses a compact experiment-design figure, result figures from the retained placement study, and tables for the VM conditions, system measurements, placement results, predictor ablation, and threshold sensitivity.

## Final submission

Submit through the course submission channel:

1. The public GitHub repository.
2. The final 3-page PDF after the Ubuntu/VMware results have been entered.
3. The printed paper required by the course.
4. The 3-5 minute walkthrough.

See `SUBMISSION.md` for the checklist.
