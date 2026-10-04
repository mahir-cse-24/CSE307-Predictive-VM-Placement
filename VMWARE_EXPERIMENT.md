# Ubuntu/VMware experiment

This is the main experiment for the term paper. It tests one fixed workload under different guest resource allocations and records operating-system measurements.

## VM configurations

Use the same Ubuntu VM for all conditions.

| Condition | RAM | vCPU |
|---|---:|---:|
| A | 1 GB | 1 |
| B | 2 GB | 1 |
| C | 4 GB | 1 |
| D | 2 GB | 2 |
| E | 2 GB | 4 |

Only the VMware resource allocation changes. Keep the Ubuntu installation, workload file, worker count, and workload parameters unchanged.

## Prepare Ubuntu

```bash
sudo apt update
sudo apt install -y python3 python3-pip
python3 --version
uname -a
lscpu
free -h
```

From the project directory, create the trace once:

```bash
bash scripts/prepare_workload.sh
```

Save the SHA-256 hash reported by the script. The hash must match for every condition.

## Run the conditions

After setting the VM RAM and vCPU values in VMware, boot Ubuntu and run:

```bash
bash scripts/run_condition.sh vm_1gb_1vcpu
```

Then repeat after changing the VM to the next configuration:

```bash
bash scripts/run_condition.sh vm_2gb_1vcpu
bash scripts/run_condition.sh vm_4gb_1vcpu
bash scripts/run_condition.sh vm_2gb_2vcpu
bash scripts/run_condition.sh vm_2gb_4vcpu
```

The script performs three runs for each condition.

## Measurements

The collector records elapsed time, user and system CPU time, minor and major page faults, context switches, page-fault counters from `/proc/vmstat`, swap-in and swap-out deltas, visible CPUs, guest memory, kernel and OS information, and the workload hash.

## Analyze the results

After all conditions have been collected:

```bash
python3 src/analyze_system.py
python3 src/plot_system.py
```

The main raw data file is:

```text
results/system_experiment.csv
```

The summary file is:

```text
results/system_summary.csv
```

## Comparison rule

The workload is held constant across all five conditions. This is necessary for a direct comparison because a different access sequence could change page-fault and timing measurements even when the VM resources stay the same.

Do not invent missing measurements. The final report should use the data collected from the Ubuntu guest.
