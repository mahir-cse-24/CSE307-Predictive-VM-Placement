#!/usr/bin/env python3
"""Summarize measured Ubuntu/VMware system experiment data."""
from __future__ import annotations

import argparse
import pandas as pd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="results/system_experiment.csv")
    ap.add_argument("--output", default="results/system_summary.csv")
    args = ap.parse_args()

    df = pd.read_csv(args.input)
    if df.empty:
        raise SystemExit("No system measurements found. Run the collector inside Ubuntu/VMware first.")

    summary = (df.groupby("condition", as_index=False)
               .agg(
                   runs=("run", "count"),
                   mean_elapsed_s=("elapsed_s", "mean"),
                   sd_elapsed_s=("elapsed_s", "std"),
                   mean_user_s=("user_s", "mean"),
                   mean_system_s=("system_s", "mean"),
                   mean_minor_faults=("minor_faults", "mean"),
                   mean_major_faults=("major_faults", "mean"),
                   mean_pgfault_delta=("pgfault_delta", "mean"),
                   mean_pgmajfault_delta=("pgmajfault_delta", "mean"),
                   mean_pswpin_delta=("pswpin_delta", "mean"),
                   mean_pswpout_delta=("pswpout_delta", "mean"),
                   visible_cpus=("visible_cpus", "first"),
                   mem_total_gb=("mem_total_gb", "mean"),
               ))
    summary.to_csv(args.output, index=False)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
