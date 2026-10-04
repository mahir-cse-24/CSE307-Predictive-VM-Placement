# Run guide

## Ubuntu/VMware experiment

Prepare the fixed workload inside the Ubuntu guest:

```bash
bash scripts/prepare_workload.sh
```

Run the five VMware conditions:

```bash
bash scripts/run_condition.sh vm_1gb_1vcpu
bash scripts/run_condition.sh vm_2gb_1vcpu
bash scripts/run_condition.sh vm_4gb_1vcpu
bash scripts/run_condition.sh vm_2gb_2vcpu
bash scripts/run_condition.sh vm_2gb_4vcpu
```

The same trace is reused for every condition. After all runs:

```bash
python3 src/analyze_system.py
python3 src/plot_system.py
```

The main data file is `results/system_experiment.csv`.

## Retained placement extension

The original Track 4 simulator remains available under `src/`, with its research analysis and result files under `research/` and `results/`.

Do not replace missing Ubuntu/VMware measurements with simulated values.
