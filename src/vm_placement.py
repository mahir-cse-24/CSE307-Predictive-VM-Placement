"""CSE-307 Track 4 - Predictive VM Placement.

Implements static First-Fit and Best-Fit placement plus an online linear-regression
predictive placer. The simulation uses synthetic VM load traces and counts SLA
violations, host-utilization imbalance, and migrations.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


@dataclass
class VM:
    vm_id: int
    host_id: int | None = None


class PlacementPolicy:
    name = "base"

    def choose_host(self, vm_id: int, demand: float, host_loads: np.ndarray,
                    projected: bool = False, avoid: int | None = None) -> int | None:
        raise NotImplementedError


class FirstFitPolicy(PlacementPolicy):
    name = "First-Fit"

    def choose_host(self, vm_id: int, demand: float, host_loads: np.ndarray,
                    projected: bool = False, avoid: int | None = None) -> int | None:
        for h, load in enumerate(host_loads):
            if h == avoid:
                continue
            if load + demand <= 1.0 + 1e-12:
                return h
        return None


class BestFitPolicy(PlacementPolicy):
    name = "Best-Fit"

    def choose_host(self, vm_id: int, demand: float, host_loads: np.ndarray,
                    projected: bool = False, avoid: int | None = None) -> int | None:
        candidates = []
        for h, load in enumerate(host_loads):
            if h == avoid:
                continue
            remaining = 1.0 - (load + demand)
            if remaining >= -1e-12:
                candidates.append((remaining, h))
        return min(candidates)[1] if candidates else None


def generate_load_trace(seed: int, n_vms: int = 20, steps: int = 120,
                        shift_step: int = 60) -> pd.DataFrame:
    """Generate a reproducible two-phase multi-VM load trace.

    Phase 1: low/moderate, locality-like stationary demand.
    Phase 2: selected VMs experience a persistent step-up and volatility.
    Loads are clipped to [0.02, 0.72] so a single VM cannot consume a full host.
    """
    rng = np.random.default_rng(seed)
    base = rng.uniform(0.08, 0.28, size=n_vms)
    phase2_vms = np.argsort(base)[-7:]
    shift = np.zeros(n_vms)
    shift[phase2_vms] = rng.uniform(0.20, 0.32, size=len(phase2_vms))

    rows = []
    prev = base.copy()
    for t in range(steps):
        phase2 = t >= shift_step
        noise_scale = 0.018 if not phase2 else 0.035
        reversion = 0.25
        target = base + (shift if phase2 else 0.0)
        prev = prev + reversion * (target - prev) + rng.normal(0, noise_scale, n_vms)
        if phase2 and (t % 17 in (0, 1, 2)):
            burst_mask = rng.random(n_vms) < 0.20
            prev[burst_mask] += rng.uniform(0.04, 0.10, burst_mask.sum())
        prev = np.clip(prev, 0.02, 0.72)
        for vm_id in range(n_vms):
            rows.append((t, vm_id, float(prev[vm_id]), int(phase2)))
    return pd.DataFrame(rows, columns=["time", "vm_id", "load", "shift_phase"])


def _pack_static(loads: np.ndarray, policy: PlacementPolicy, n_hosts: int,
                 existing: np.ndarray | None = None,
                 order: List[int] | None = None,
                 avoid_host: Dict[int, int] | None = None) -> Dict[int, int]:
    host_loads = np.zeros(n_hosts, dtype=float) if existing is None else existing.copy()
    assignment: Dict[int, int] = {}
    order = list(range(len(loads))) if order is None else order
    for vm_id in order:
        avoid = avoid_host.get(vm_id) if avoid_host else None
        h = policy.choose_host(vm_id, float(loads[vm_id]), host_loads, avoid=avoid)
        if h is None:
            assignment[vm_id] = -1
        else:
            assignment[vm_id] = h
            host_loads[h] += loads[vm_id]
    return assignment


def initial_assignment(loads: np.ndarray, policy: PlacementPolicy, n_hosts: int) -> Dict[int, int]:
    order = list(np.argsort(-loads))
    return _pack_static(loads, policy, n_hosts, order=order)


def lag_features(history: List[float], window: int = 6) -> np.ndarray:
    vals = np.asarray(history[-window:], dtype=float)
    if len(vals) < window:
        raise ValueError("not enough history")
    diffs = np.diff(vals)
    return np.array([
        vals[-1], vals[-2], vals[-3], vals[-4],
        vals.mean(), vals.std(),
        diffs.mean(),
        vals[-1] - vals[0],
    ], dtype=float)


def make_training_examples(series: List[float], window: int = 6) -> Tuple[np.ndarray, np.ndarray]:
    X, y = [], []
    for i in range(window, len(series)):
        X.append(lag_features(series[:i], window))
        y.append(series[i])
    return np.asarray(X), np.asarray(y)


def fit_global_model(histories: List[List[float]], window: int = 6) -> Tuple[LinearRegression | None, float]:
    """Fit one shared next-load regressor from all VMs' past observations."""
    X_parts, y_parts = [], []
    for history in histories:
        if len(history) >= window + 4:
            X, y = make_training_examples(history, window)
            X_parts.append(X)
            y_parts.append(y)
    if not X_parts:
        return None, 0.10
    X = np.vstack(X_parts)
    y = np.concatenate(y_parts)
    if len(y) < 8:
        return None, 0.10
    model = LinearRegression()
    model.fit(X, y)
    residual = y - model.predict(X)
    mae = float(np.mean(np.abs(residual)))
    return model, mae


def predict_next(history: List[float], model: LinearRegression | None,
                 mae: float, window: int = 6) -> Tuple[float, float]:
    if model is None or len(history) < window:
        pred = float(history[-1])
        return pred, 0.50
    x = lag_features(history, window).reshape(1, -1)
    pred = float(model.predict(x)[0])
    confidence = float(np.clip(1.0 - mae / 0.12, 0.50, 0.98))
    return pred, confidence


def choose_predictive_assignment(predicted: np.ndarray, current_assignment: Dict[int, int],
                                  n_hosts: int, threshold: float = 0.90) -> Dict[int, int]:
    """Greedy proactive re-packing using predicted next-step VM loads."""
    loads = np.asarray(predicted, dtype=float)
    projected = np.zeros(n_hosts, dtype=float)
    new_assignment = dict(current_assignment)
    for vm_id, h in current_assignment.items():
        if h >= 0:
            projected[h] += loads[vm_id]

    overloaded = [h for h in range(n_hosts) if projected[h] > threshold + 1e-12]
    for source in sorted(overloaded, key=lambda h: projected[h], reverse=True):
        vm_candidates = [vm for vm, h in new_assignment.items() if h == source]
        vm_candidates.sort(key=lambda vm: loads[vm], reverse=True)
        for vm_id in vm_candidates:
            demand = loads[vm_id]
            if projected[source] <= threshold + 1e-12:
                break
            candidates = []
            for dest in range(n_hosts):
                if dest == source:
                    continue
                if projected[dest] + demand <= threshold + 1e-12:
                    rem = threshold - (projected[dest] + demand)
                    candidates.append((rem, dest))
            if not candidates:
                continue
            _, dest = min(candidates)
            projected[source] -= demand
            projected[dest] += demand
            new_assignment[vm_id] = dest
    return new_assignment


def explain_decision(vm_id: int, source: int, dest: int, predicted_load: float,
                     confidence: float, source_proj: float, dest_proj: float,
                     actual_next_load: float) -> Tuple[str, float, bool]:
    actual_ok = (source_proj - predicted_load + actual_next_load <= 1.0 + 1e-12
                 and dest_proj - predicted_load + actual_next_load <= 1.0 + 1e-12)
    text = (f"VM {vm_id} was moved from host {source} to host {dest} because its "
            f"predicted next-step load was {predicted_load:.2f}; the predicted destination "
            f"load was {dest_proj:.2f}, leaving headroom before the SLA threshold.")
    return text, float(confidence), bool(actual_ok)


def simulate(policy_name: str, trace: pd.DataFrame, n_hosts: int = 8,
             proactive_threshold: float = 0.90, history_window: int = 6) -> Tuple[pd.DataFrame, pd.DataFrame]:
    vm_ids = sorted(trace.vm_id.unique())
    n_vms = len(vm_ids)
    steps = int(trace.time.max()) + 1
    load_matrix = trace.pivot(index="time", columns="vm_id", values="load").loc[:, vm_ids].to_numpy()

    if policy_name == "First-Fit":
        placer: PlacementPolicy = FirstFitPolicy()
    elif policy_name == "Best-Fit":
        placer = BestFitPolicy()
    elif policy_name == "Predictive":
        placer = BestFitPolicy()
    else:
        raise ValueError(policy_name)

    assignment = initial_assignment(load_matrix[0], placer, n_hosts)
    histories: List[List[float]] = [[float(load_matrix[0, vm])] for vm in range(n_vms)]
    event_rows = []
    bonus_rows = []
    migration_count = 0

    def host_actual_loads(t: int, assn: Dict[int, int]) -> np.ndarray:
        loads = np.zeros(n_hosts, dtype=float)
        for vm in range(n_vms):
            h = assn[vm]
            if h >= 0:
                loads[h] += load_matrix[t, vm]
        return loads

    for t in range(steps):
        if t > 0:
            if policy_name == "Predictive":
                preds = np.zeros(n_vms)
                confs = np.zeros(n_vms)
                model, model_mae = fit_global_model(histories, history_window)
                for vm in range(n_vms):
                    pred, conf = predict_next(histories[vm], model, model_mae, history_window)
                    preds[vm] = np.clip(pred, 0.02, 0.95)
                    confs[vm] = conf
                before = dict(assignment)
                assignment = choose_predictive_assignment(preds, assignment, n_hosts, proactive_threshold)
                for vm in range(n_vms):
                    if before[vm] != assignment[vm] and before[vm] >= 0 and assignment[vm] >= 0:
                        migration_count += 1
                        src = before[vm]
                        dst = assignment[vm]
                        src_proj = sum(preds[x] for x, h in assignment.items() if h == src)
                        dst_proj = sum(preds[x] for x, h in assignment.items() if h == dst)
                        text, conf, correct = explain_decision(
                            vm, src, dst, preds[vm], confs[vm], src_proj, dst_proj, load_matrix[t, vm]
                        )
                        bonus_rows.append({
                            "time": t, "vm_id": vm, "source": src, "destination": dst,
                            "predicted_load": preds[vm], "confidence": conf,
                            "correct": int(correct), "explanation": text
                        })
            else:
                actual_prev = host_actual_loads(t - 1, assignment)
                if np.any(actual_prev > 1.0 + 1e-12):
                    source_hosts = [h for h in range(n_hosts) if actual_prev[h] > 1.0 + 1e-12]
                    for source in sorted(source_hosts, key=lambda h: actual_prev[h], reverse=True):
                        vm_candidates = [vm for vm, h in assignment.items() if h == source]
                        vm_candidates.sort(key=lambda vm: load_matrix[t - 1, vm], reverse=True)
                        for vm in vm_candidates:
                            if actual_prev[source] <= 1.0 + 1e-12:
                                break
                            demand = load_matrix[t, vm]
                            dest = placer.choose_host(vm, float(demand), actual_prev, avoid=source)
                            if dest is None:
                                continue
                            actual_prev[source] -= load_matrix[t - 1, vm]
                            actual_prev[dest] += demand
                            assignment[vm] = dest
                            migration_count += 1

        actual_hosts = host_actual_loads(t, assignment)
        overload_events = int(np.sum(actual_hosts > 1.0 + 1e-12))
        mean_util = float(actual_hosts.mean())
        util_std = float(actual_hosts.std())
        max_util = float(actual_hosts.max())
        event_rows.append({
            "time": t, "phase": "post-shift" if t >= steps // 2 else "pre-shift",
            "mean_host_utilization": mean_util,
            "host_utilization_std": util_std,
            "max_host_utilization": max_util,
            "overload_events": overload_events,
            "migration_count": migration_count,
        })
        for vm in range(n_vms):
            histories[vm].append(float(load_matrix[t, vm]))

    return pd.DataFrame(event_rows), pd.DataFrame(bonus_rows)


def summarize(events: pd.DataFrame, shift_step: int) -> Dict[str, float]:
    pre = events[events.time < shift_step]
    post = events[events.time >= shift_step]
    return {
        "util_std_mean": float(events.host_utilization_std.mean()),
        "util_std_pre": float(pre.host_utilization_std.mean()),
        "util_std_post": float(post.host_utilization_std.mean()),
        "max_util_mean": float(events.max_host_utilization.mean()),
        "max_util_post": float(post.max_host_utilization.mean()),
        "overload_events": int(events.overload_events.sum()),
        "overload_events_pre": int(pre.overload_events.sum()),
        "overload_events_post": int(post.overload_events.sum()),
        "migrations": int(events.migration_count.iloc[-1]),
    }


def run_experiment(seeds: List[int], out_csv: str, out_events: str, out_bonus: str) -> pd.DataFrame:
    summaries = []
    all_events = []
    all_bonus = []
    for seed in seeds:
        trace = generate_load_trace(seed)
        for policy in ["First-Fit", "Best-Fit", "Predictive"]:
            events, bonus = simulate(policy, trace)
            s = summarize(events, shift_step=60)
            s.update({"seed": seed, "policy": policy})
            summaries.append(s)
            tmp = events.copy()
            tmp["seed"] = seed
            tmp["policy"] = policy
            all_events.append(tmp)
            if len(bonus):
                b = bonus.copy()
                b["seed"] = seed
                all_bonus.append(b)
    df = pd.DataFrame(summaries)
    df.to_csv(out_csv, index=False)
    pd.concat(all_events, ignore_index=True).to_csv(out_events, index=False)
    if all_bonus:
        pd.concat(all_bonus, ignore_index=True).to_csv(out_bonus, index=False)
    else:
        pd.DataFrame(columns=["seed", "time", "vm_id", "confidence", "correct", "explanation"]).to_csv(out_bonus, index=False)
    return df


if __name__ == "__main__":
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=10)
    parser.add_argument("--out-dir", default="results")
    args = parser.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    df = run_experiment(
        list(range(100, 100 + args.seeds)),
        str(out / "summary_by_run.csv"),
        str(out / "events_by_step.csv"),
        str(out / "bonus_decisions.csv"),
    )
    print(df.groupby("policy").agg({
        "util_std_mean": ["mean", "std"],
        "overload_events": ["mean", "std"],
        "migrations": ["mean", "std"],
    }).round(4))
