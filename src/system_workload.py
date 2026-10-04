#!/usr/bin/env python3
"""Deterministic memory/CPU workload for the CSE-307 term paper.

The same trace and workload parameters should be reused for every VMware
condition. The program uses two worker processes, a fixed working-set size,
and a fixed sequence of page indexes. It reports elapsed time and OS-level
resource counters.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import resource
import time
from multiprocessing import Process, Queue
from pathlib import Path
from typing import Dict, List

PAGE = 4096


def lcg(seed: int) -> int:
    return (1664525 * seed + 1013904223) & 0xFFFFFFFF


def build_trace(path: Path, steps: int, pages: int, seed: int = 3072026) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    x = seed & 0xFFFFFFFF
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["step", "worker", "page_index"])
        for step in range(steps):
            for worker in (0, 1):
                x = lcg(x)
                page = x % pages
                w.writerow([step, worker, page])


def load_trace(path: Path, worker: int) -> List[int]:
    vals: List[int] = []
    with path.open() as f:
        r = csv.DictReader(f)
        for row in r:
            if int(row["worker"]) == worker:
                vals.append(int(row["page_index"]))
    return vals


def checksum_bytes(buf: bytearray) -> str:
    return hashlib.sha256(buf[: min(len(buf), 1024 * 1024)]).hexdigest()[:16]


def worker(worker_id: int, trace_path: str, working_set_mb: int,
           inner_loops: int, q: Queue) -> None:
    trace = load_trace(Path(trace_path), worker_id)
    pages = (working_set_mb * 1024 * 1024) // PAGE
    buf = bytearray(pages * PAGE)

    start = time.perf_counter()
    checksum = 0
    for _ in range(inner_loops):
        for idx in trace:
            p = (idx % pages) * PAGE
            value = (buf[p] + worker_id + 1) & 0xFF
            buf[p] = value
            checksum = (checksum + value) & 0xFFFFFFFF

    elapsed = time.perf_counter() - start
    ru = resource.getrusage(resource.RUSAGE_SELF)
    q.put({
        "worker": worker_id,
        "elapsed_s": elapsed,
        "user_s": ru.ru_utime,
        "system_s": ru.ru_stime,
        "minor_faults": ru.ru_minflt,
        "major_faults": ru.ru_majflt,
        "voluntary_ctx": ru.ru_nvcsw,
        "involuntary_ctx": ru.ru_nivcsw,
        "checksum": checksum,
        "sample_hash": checksum_bytes(buf),
    })


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trace", type=Path, required=True)
    ap.add_argument("--working-set-mb", type=int, default=160,
                    help="working-set per worker; keep identical across runs")
    ap.add_argument("--inner-loops", type=int, default=8)
    args = ap.parse_args()

    q: Queue = Queue()
    procs = [Process(target=worker, args=(w, str(args.trace),
                                         args.working_set_mb,
                                         args.inner_loops, q))
             for w in (0, 1)]

    t0 = time.perf_counter()
    for p in procs:
        p.start()
    rows = [q.get() for _ in procs]
    for p in procs:
        p.join()
    elapsed = time.perf_counter() - t0

    rows.sort(key=lambda x: x["worker"])
    total_user = sum(r["user_s"] for r in rows)
    total_system = sum(r["system_s"] for r in rows)
    total_minor = sum(r["minor_faults"] for r in rows)
    total_major = sum(r["major_faults"] for r in rows)
    total_ctx = sum(r["voluntary_ctx"] + r["involuntary_ctx"] for r in rows)
    print(json_dumps({
        "elapsed_s": elapsed,
        "workers": 2,
        "working_set_mb_per_worker": args.working_set_mb,
        "inner_loops": args.inner_loops,
        "user_s": total_user,
        "system_s": total_system,
        "minor_faults": total_minor,
        "major_faults": total_major,
        "context_switches": total_ctx,
        "workers_detail": rows,
    }))


def json_dumps(obj: Dict) -> str:
    import json
    return json.dumps(obj, sort_keys=True)


if __name__ == "__main__":
    main()
