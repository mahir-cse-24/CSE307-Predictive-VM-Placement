#!/usr/bin/env python3
"""Create figures from measured Ubuntu/VMware experiment data."""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="results/system_summary.csv")
    ap.add_argument("--outdir", default="figures")
    args = ap.parse_args()

    df = pd.read_csv(args.input)
    if df.empty:
        raise SystemExit("No summary data available.")

    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)

    for metric, ylabel, filename in [
        ("mean_elapsed_s", "Mean elapsed time (s)", "system_elapsed.png"),
        ("mean_major_faults", "Mean major page faults", "system_major_faults.png"),
        ("mean_pswpout_delta", "Mean pages swapped out", "system_swap_out.png"),
    ]:
        plt.figure(figsize=(7, 4))
        plt.bar(df["condition"], df[metric])
        plt.ylabel(ylabel)
        plt.xlabel("VM resource condition")
        plt.xticks(rotation=25, ha="right")
        plt.tight_layout()
        plt.savefig(out / filename, dpi=180)
        plt.close()


if __name__ == "__main__":
    main()
