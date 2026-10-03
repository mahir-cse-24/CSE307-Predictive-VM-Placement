from pathlib import Path
import pandas as pd
from vm_placement import PlacementConfig, generate_load_trace, simulate

rows = []
for threshold in [0.85, 0.90, 0.95]:
    for seed in [100, 101, 102]:
        cfg = PlacementConfig(proactive_threshold=threshold)
        trace = generate_load_trace(seed, cfg)
        events, decisions, _ = simulate(trace, "Predictive", cfg, "regression")
        post = events[events.time >= cfg.shift_step]
        rows.append({
            "threshold": threshold,
            "seed": seed,
            "util_std": events.utilization_std.mean(),
            "post_util_std": post.utilization_std.mean(),
            "overload": events.overloaded_hosts.sum(),
            "post_overload": post.overloaded_hosts.sum(),
            "migrations": events.migration_count.iloc[-1],
            "decisions": len(decisions),
        })

df = pd.DataFrame(rows)
out = Path(__file__).resolve().parents[1] / "results" / "threshold_sensitivity.csv"
df.to_csv(out, index=False)
print(df.groupby("threshold").mean(numeric_only=True).round(4))
