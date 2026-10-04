#!/usr/bin/env python3
"""Run one fixed workload and collect VM/OS measurements.

Run this from inside the Ubuntu VM after configuring VMware resources.
The workload trace must be identical for every condition.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_os_release() -> dict:
    out = {}
    p = Path("/etc/os-release")
    if p.exists():
        for line in p.read_text(errors="ignore").splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                out[k] = v.strip().strip('"')
    return out


def read_meminfo() -> dict:
    d = {}
    for line in Path("/proc/meminfo").read_text(errors="ignore").splitlines():
        m = re.match(r"(\w+):\s+(\d+)\s+kB", line)
        if m:
            d[m.group(1)] = int(m.group(2)) * 1024
    return d


def read_vmstat() -> dict:
    d = {}
    for line in Path("/proc/vmstat").read_text(errors="ignore").splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1].isdigit():
            d[parts[0]] = int(parts[1])
    return d


def hypervisor_line() -> str:
    try:
        out = subprocess.check_output(["lscpu"], text=True, stderr=subprocess.DEVNULL)
        for line in out.splitlines():
            if "Hypervisor" in line:
                return line.strip()
    except Exception:
        pass
    return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--condition", required=True)
    ap.add_argument("--trace", default=str(ROOT / "results" / "workload_trace.csv"))
    ap.add_argument("--working-set-mb", type=int, default=160)
    ap.add_argument("--inner-loops", type=int, default=8)
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--out", default=str(ROOT / "results" / "system_experiment.csv"))
    args = ap.parse_args()

    osr = read_os_release()
    vm0 = read_vmstat()
    rows = []

    workload = [sys.executable, str(ROOT / "src" / "system_workload.py"),
                "--trace", args.trace,
                "--working-set-mb", str(args.working_set_mb),
                "--inner-loops", str(args.inner_loops)]

    for run_no in range(1, args.runs + 1):
        t0 = time.perf_counter()
        cp = subprocess.run(workload, capture_output=True, text=True, check=True)
        elapsed_outer = time.perf_counter() - t0
        result = json.loads(cp.stdout)
        vm1 = read_vmstat()
        mem1 = read_meminfo()

        rows.append({
            "condition": args.condition,
            "run": run_no,
            "os": osr.get("PRETTY_NAME", osr.get("NAME", "")),
            "kernel": platform.release(),
            "vmware_hypervisor_line": hypervisor_line(),
            "visible_cpus": os.cpu_count() or 1,
            "mem_total_gb": round(mem1.get("MemTotal", 0) / 2**30, 3),
            "mem_available_gb": round(mem1.get("MemAvailable", 0) / 2**30, 3),
            "elapsed_s": result["elapsed_s"],
            "outer_elapsed_s": elapsed_outer,
            "user_s": result["user_s"],
            "system_s": result["system_s"],
            "minor_faults": result["minor_faults"],
            "major_faults": result["major_faults"],
            "context_switches": result["context_switches"],
            "pgfault_delta": vm1.get("pgfault", 0) - vm0.get("pgfault", 0),
            "pgmajfault_delta": vm1.get("pgmajfault", 0) - vm0.get("pgmajfault", 0),
            "pswpin_delta": vm1.get("pswpin", 0) - vm0.get("pswpin", 0),
            "pswpout_delta": vm1.get("pswpout", 0) - vm0.get("pswpout", 0),
            "working_set_mb_per_worker": args.working_set_mb,
            "workers": 2,
            "inner_loops": args.inner_loops,
            "trace_sha256": hashlib.sha256(Path(args.trace).read_bytes()).hexdigest(),
        })

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    exists = out.exists() and out.stat().st_size > 0
    import csv
    with out.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        if not exists:
            w.writeheader()
        w.writerows(rows)

    print(json.dumps({"condition": args.condition, "runs_added": len(rows), "output": str(out)}, indent=2))


if __name__ == "__main__":
    main()
