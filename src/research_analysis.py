from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
summary = pd.read_csv(RESULTS / "summary_by_run.csv")
base = summary[summary.policy.isin(["First-Fit", "Best-Fit", "Predictive"])].copy()
wide = base.pivot(index="seed", columns="policy")
rows = []

for metric in ["util_std_mean", "overload_events", "migrations"]:
    for baseline in ["First-Fit", "Best-Fit"]:
        d = wide[metric][baseline] - wide[metric]["Predictive"]
        stat, p = wilcoxon(d)
        nonzero = d[d != 0]
        ranks = nonzero.abs().rank()
        w_plus = ranks[nonzero > 0].sum()
        w_minus = ranks[nonzero < 0].sum()
        rank_biserial = float((w_plus - w_minus) / (w_plus + w_minus)) if len(nonzero) else 0.0
        rows.append({
            "metric": metric,
            "comparison": f"Predictive vs {baseline}",
            "mean_baseline_minus_predictive": d.mean(),
            "median_baseline_minus_predictive": d.median(),
            "wilcoxon_p": p,
            "wins_predictive": int((d > 0).sum()),
            "rank_biserial": rank_biserial,
        })

pd.DataFrame(rows).to_csv(RESULTS / "statistical_tests.csv", index=False)

ablation = summary[summary.policy.isin(["Predictive", "Predictive-Persistence"])].groupby("policy").agg(
    forecast_mae=("forecast_mae", "mean"),
    forecast_rmse=("forecast_rmse", "mean"),
    forecast_r2=("forecast_r2", "mean"),
    util_std_mean=("util_std_mean", "mean"),
    overload_events=("overload_events", "mean"),
    migrations=("migrations", "mean"),
).reset_index()
ablation.to_csv(RESULTS / "predictor_ablation.csv", index=False)

bonus = pd.read_csv(RESULTS / "bonus_decisions.csv")
if not bonus.empty:
    prob = bonus.confidence.to_numpy()
    y = bonus.correct.to_numpy()
    brier = float(np.mean((prob - y) ** 2))
    bins = pd.cut(prob, bins=[0.49, 0.6, 0.7, 0.8, 0.9, 1.0], include_lowest=True)
    calibration = []
    for _, group in bonus.assign(conf_bin=bins).groupby("conf_bin", observed=False):
        if len(group):
            calibration.append((
                float(group.confidence.mean()),
                float(group.correct.mean()),
                len(group),
            ))
    ece = float(sum(n * abs(conf - acc) for conf, acc, n in calibration) / len(bonus))
    pd.DataFrame([{
        "decisions": len(bonus),
        "accuracy": y.mean(),
        "mean_confidence": prob.mean(),
        "brier_score": brier,
        "ece": ece,
        "mean_confidence_correct": bonus.loc[bonus.correct == 1, "confidence"].mean(),
        "mean_confidence_incorrect": bonus.loc[bonus.correct == 0, "confidence"].mean()
            if (bonus.correct == 0).any() else np.nan,
    }]).to_csv(RESULTS / "confidence_summary.csv", index=False)
