from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)

events = pd.read_csv(RESULTS / "events_by_step.csv")
summary = pd.read_csv(RESULTS / "summary_by_run.csv")

ts = events.groupby(["policy", "time"], as_index=False).agg(
    util_std=("host_utilization_std", "mean"),
    max_util=("max_host_utilization", "mean"),
    overload=("overload_events", "mean"),
)
for metric, ylabel, name in [
    ("util_std", "Host utilization standard deviation", "utilization_balance.png"),
    ("max_util", "Mean maximum host utilization", "max_utilization.png"),
    ("overload", "Average overloaded hosts per step", "sla_events.png"),
]:
    plt.figure(figsize=(6.5, 3.3))
    for policy, g in ts.groupby("policy"):
        plt.plot(g.time, g[metric], label=policy)
    plt.axvline(60, linestyle="--", linewidth=1)
    plt.xlabel("Simulation step")
    plt.ylabel(ylabel)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG / name, dpi=220)
    plt.close()

agg = summary.groupby("policy").agg(
    utilization_balance=("util_std_mean", "mean"),
    overload_events=("overload_events", "mean"),
    migrations=("migrations", "mean"),
).reset_index()

fig, axes = plt.subplots(1, 3, figsize=(9, 3.2))
for ax, metric, ylabel in zip(
    axes,
    ["utilization_balance", "overload_events", "migrations"],
    ["Mean host-utilization std.", "Mean overload events", "Mean migrations"],
):
    ax.bar(agg.policy, agg[metric])
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", rotation=20)
fig.tight_layout()
fig.savefig(FIG / "summary_metrics.png", dpi=220)
plt.close(fig)

bonus = pd.read_csv(RESULTS / "bonus_decisions.csv")
if not bonus.empty:
    by_bin = bonus.assign(conf_bin=(bonus.confidence * 10).astype(int) / 10).groupby("conf_bin").agg(
        decisions=("correct", "size"), empirical_accuracy=("correct", "mean")
    ).reset_index()
    plt.figure(figsize=(5.8, 3.3))
    plt.plot(by_bin.conf_bin, by_bin.empirical_accuracy, marker="o", label="Empirical accuracy")
    plt.plot([0.5, 1.0], [0.5, 1.0], linestyle="--", label="Perfect calibration")
    plt.xlabel("Rule-based confidence")
    plt.ylabel("Decision correctness")
    plt.xlim(0.5, 1.0)
    plt.ylim(0, 1.05)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG / "confidence_calibration.png", dpi=220)
    plt.close()
