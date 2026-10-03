"""Track 4: predictive VM placement with First-Fit and Best-Fit baselines."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

HOST_CAPACITY = 1.0
N_HOSTS = 8
N_VMS = 20
STEPS = 120
SHIFT_STEP = 60
HISTORY_WINDOW = 6


@dataclass(frozen=True)
class PlacementConfig:
    hosts: int = N_HOSTS
    vms: int = N_VMS
    steps: int = STEPS
    shift_step: int = SHIFT_STEP
    history_window: int = HISTORY_WINDOW
    proactive_threshold: float = 0.90


class FirstFit:
    name = "First-Fit"

    def choose(self, demand: float, host_loads: np.ndarray, avoid: int | None = None) -> int | None:
        for host, load in enumerate(host_loads):
            if host == avoid:
                continue
            if load + demand <= HOST_CAPACITY + 1e-12:
                return host
        return None


class BestFit:
    name = "Best-Fit"

    def choose(self, demand: float, host_loads: np.ndarray, avoid: int | None = None) -> int | None:
        candidates: list[tuple[float, int]] = []
        for host, load in enumerate(host_loads):
            if host == avoid:
                continue
            residual = HOST_CAPACITY - (load + demand)
            if residual >= -1e-12:
                candidates.append((residual, host))
        return min(candidates)[1] if candidates else None


def generate_load_trace(seed: int, config: PlacementConfig = PlacementConfig()) -> pd.DataFrame:
    """Two-phase workload with a rising demand shift and short bursts."""
    rng = np.random.default_rng(seed)
    base = rng.uniform(0.08, 0.28, config.vms)
    stressed = np.argsort(base)[-7:]
    shift = np.zeros(config.vms)
    shift[stressed] = rng.uniform(0.20, 0.32, len(stressed))

    prev = base.copy()
    rows = []
    for t in range(config.steps):
        phase2 = t >= config.shift_step
        if phase2:
            ramp = min(1.0, (t - config.shift_step + 1) / 10.0)
            target = base + ramp * shift
            noise = 0.030 + 0.010 * ramp
        else:
            target = base
            noise = 0.018
        prev = prev + 0.35 * (target - prev) + rng.normal(0, noise, config.vms)
        if phase2 and t % 13 in (0, 1, 2):
            mask = rng.random(config.vms) < 0.25
            if mask.any():
                prev[mask] += rng.uniform(0.05, 0.12, mask.sum())
        prev = np.clip(prev, 0.02, 0.72)
        for vm in range(config.vms):
            rows.append((t, vm, float(prev[vm]), "post" if phase2 else "pre"))
    return pd.DataFrame(rows, columns=["time", "vm_id", "load", "phase"])


def initial_assignment(loads: np.ndarray, policy, n_hosts: int) -> Dict[int, int]:
    order = list(np.argsort(-loads))
    host_loads = np.zeros(n_hosts)
    assignment = {}
    for vm in order:
        host = policy.choose(float(loads[vm]), host_loads)
        assignment[vm] = -1 if host is None else host
        if host is not None:
            host_loads[host] += loads[vm]
    return assignment


def host_loads(loads: np.ndarray, assignment: Dict[int, int], n_hosts: int) -> np.ndarray:
    out = np.zeros(n_hosts)
    for vm, host in assignment.items():
        if host >= 0:
            out[host] += loads[vm]
    return out


def lag_features(history: List[float], window: int) -> np.ndarray:
    vals = np.asarray(history[-window:], dtype=float)
    if len(vals) < window:
        raise ValueError("insufficient history")
    d = np.diff(vals)
    return np.array([
        vals[-1], vals[-2], vals[-3], vals[-4],
        vals.mean(), vals.std(), d.mean(), vals[-1] - vals[0]
    ], dtype=float)


def train_regression(histories: List[List[float]], window: int):
    Xs, ys = [], []
    for history in histories:
        if len(history) <= window:
            continue
        for i in range(window, len(history)):
            Xs.append(lag_features(history[:i], window))
            ys.append(history[i])
    if len(ys) < 8:
        return None, np.nan
    model = LinearRegression().fit(np.asarray(Xs), np.asarray(ys))
    residual = np.asarray(ys) - model.predict(np.asarray(Xs))
    return model, float(np.mean(np.abs(residual)))


def predict_one(history: List[float], model, window: int, mode: str, model_mae: float):
    if mode == "persistence":
        return float(history[-1]), 0.55
    if model is None or len(history) < window:
        return float(history[-1]), 0.50
    pred = float(model.predict(lag_features(history, window).reshape(1, -1))[0])
    confidence = float(np.clip(1.0 - (model_mae / 0.12), 0.50, 0.98))
    return float(np.clip(pred, 0.02, 0.95)), confidence


def predictive_repack(predicted: np.ndarray, assignment: Dict[int, int],
                      n_hosts: int, threshold: float) -> Dict[int, int]:
    projected = host_loads(predicted, assignment, n_hosts)
    new_assignment = dict(assignment)
    overloaded = [h for h in range(n_hosts) if projected[h] > threshold]
    for source in sorted(overloaded, key=lambda h: projected[h], reverse=True):
        vms = sorted(
            [vm for vm, h in new_assignment.items() if h == source],
            key=lambda vm: predicted[vm], reverse=True,
        )
        for vm in vms:
            demand = predicted[vm]
            if projected[source] <= threshold + 1e-12:
                break
            choices = []
            for dest in range(n_hosts):
                if dest == source:
                    continue
                residual = threshold - (projected[dest] + demand)
                if residual >= -1e-12:
                    choices.append((residual, dest))
            if choices:
                _, dest = min(choices)
                projected[source] -= demand
                projected[dest] += demand
                new_assignment[vm] = dest
    return new_assignment


def reactive_repair(current_loads: np.ndarray, next_loads: np.ndarray,
                    assignment: Dict[int, int], policy, n_hosts: int):
    """Move VMs only after a host is observed overloaded."""
    working = dict(assignment)
    observed = host_loads(current_loads, working, n_hosts)
    migrations = 0
    for source in sorted(
        [h for h in range(n_hosts) if observed[h] > HOST_CAPACITY],
        key=lambda h: observed[h], reverse=True,
    ):
        vms = sorted(
            [vm for vm, h in working.items() if h == source],
            key=lambda vm: current_loads[vm], reverse=True,
        )
        for vm in vms:
            if observed[source] <= HOST_CAPACITY + 1e-12:
                break
            demand = float(next_loads[vm])
            dest = policy.choose(demand, observed, avoid=source)
            if dest is None:
                continue
            observed[source] -= current_loads[vm]
            observed[dest] += demand
            working[vm] = dest
            migrations += 1
    return working, migrations


def simulate(trace: pd.DataFrame, policy_name: str, config: PlacementConfig,
             predictor: str = "regression"):
    matrix = trace.pivot(index="time", columns="vm_id", values="load").to_numpy()
    policy = FirstFit() if policy_name == "First-Fit" else BestFit()
    assignment = initial_assignment(matrix[0], policy, config.hosts)
    histories = [[float(matrix[0, vm])] for vm in range(config.vms)]
    rows, decisions = [], []
    forecast_actual, forecast_pred = [], []
    migrations = 0

    for t in range(config.steps):
        if t > 0:
            if policy_name in ("First-Fit", "Best-Fit"):
                assignment, m = reactive_repair(
                    matrix[t - 1], matrix[t], assignment, policy, config.hosts
                )
                migrations += m
            else:
                if predictor == "persistence":
                    model, model_mae = None, np.nan
                else:
                    model, model_mae = train_regression(histories, config.history_window)
                preds = np.zeros(config.vms)
                conf = np.zeros(config.vms)
                for vm in range(config.vms):
                    preds[vm], conf[vm] = predict_one(
                        histories[vm], model, config.history_window, predictor,
                        model_mae if not np.isnan(model_mae) else 0.12,
                    )
                before = dict(assignment)
                assignment = predictive_repack(
                    preds, assignment, config.hosts, config.proactive_threshold
                )
                for vm in range(config.vms):
                    forecast_pred.append(preds[vm])
                    forecast_actual.append(matrix[t, vm])
                    if before[vm] != assignment[vm] and before[vm] >= 0 and assignment[vm] >= 0:
                        src, dst = before[vm], assignment[vm]
                        after = host_loads(matrix[t], assignment, config.hosts)
                        correct = int(
                            after[src] <= HOST_CAPACITY + 1e-12
                            and after[dst] <= HOST_CAPACITY + 1e-12
                        )
                        decisions.append({
                            "time": t, "vm_id": vm, "source": src, "destination": dst,
                            "confidence": conf[vm], "correct": correct,
                        })
                        migrations += 1

        actual_hosts = host_loads(matrix[t], assignment, config.hosts)
        rows.append({
            "time": t,
            "phase": "post-shift" if t >= config.shift_step else "pre-shift",
            "utilization_mean": actual_hosts.mean(),
            "utilization_std": actual_hosts.std(),
            "max_utilization": actual_hosts.max(),
            "overloaded_hosts": int(np.sum(actual_hosts > HOST_CAPACITY + 1e-12)),
            "migration_count": migrations,
        })
        for vm in range(config.vms):
            histories[vm].append(float(matrix[t, vm]))

    metrics = {}
    if forecast_actual:
        metrics["forecast_mae"] = mean_absolute_error(forecast_actual, forecast_pred)
        metrics["forecast_rmse"] = mean_squared_error(forecast_actual, forecast_pred) ** 0.5
        metrics["forecast_r2"] = r2_score(forecast_actual, forecast_pred)
    return pd.DataFrame(rows), pd.DataFrame(decisions), metrics


def run_all(seeds: list[int], config: PlacementConfig, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    summary, events, bonus = [], [], []
    policies = [
        ("First-Fit", None),
        ("Best-Fit", None),
        ("Predictive", "regression"),
        ("Predictive-Persistence", "persistence"),
    ]
    for seed in seeds:
        trace = generate_load_trace(seed, config)
        for policy, predictor in policies:
            actual_policy = "Predictive" if policy == "Predictive-Persistence" else policy
            ev, dec, metrics = simulate(trace, actual_policy, config, predictor or "regression")
            pre = ev[ev.time < config.shift_step]
            post = ev[ev.time >= config.shift_step]
            summary.append({
                "seed": seed, "policy": policy,
                "util_std_mean": ev.utilization_std.mean(),
                "util_std_pre": pre.utilization_std.mean(),
                "util_std_post": post.utilization_std.mean(),
                "overload_events": int(ev.overloaded_hosts.sum()),
                "overload_events_pre": int(pre.overloaded_hosts.sum()),
                "overload_events_post": int(post.overloaded_hosts.sum()),
                "migrations": int(ev.migration_count.iloc[-1]),
                "max_util_post": post.max_utilization.mean(),
                "forecast_mae": metrics.get("forecast_mae", np.nan),
                "forecast_rmse": metrics.get("forecast_rmse", np.nan),
                "forecast_r2": metrics.get("forecast_r2", np.nan),
            })
            e = ev.copy()
            e["seed"] = seed
            e["policy"] = policy
            events.append(e)
            if not dec.empty:
                d = dec.copy()
                d["seed"] = seed
                d["policy"] = policy
                bonus.append(d)
    s = pd.DataFrame(summary)
    e = pd.concat(events, ignore_index=True)
    b = pd.concat(bonus, ignore_index=True) if bonus else pd.DataFrame()
    s.to_csv(out_dir / "summary_by_run.csv", index=False)
    e.to_csv(out_dir / "events_by_step.csv", index=False)
    b.to_csv(out_dir / "bonus_decisions.csv", index=False)
    return s, e, b


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=10)
    parser.add_argument("--out-dir", default="results")
    parser.add_argument("--threshold", type=float, default=0.90)
    args = parser.parse_args()
    cfg = PlacementConfig(proactive_threshold=args.threshold)
    summary, _, bonus = run_all(
        list(range(100, 100 + args.seeds)), cfg, Path(args.out_dir)
    )
    print(
        summary.groupby("policy").agg({
            "util_std_mean": ["mean", "std"],
            "overload_events": ["mean", "std"],
            "migrations": ["mean", "std"],
        }).round(4)
    )
    if not bonus.empty:
        print(
            "bonus decisions:", len(bonus),
            "accuracy:", bonus.correct.mean(),
            "mean confidence:", bonus.confidence.mean(),
        )
