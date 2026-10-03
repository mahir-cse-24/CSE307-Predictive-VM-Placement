import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from vm_placement import FirstFitPolicy, BestFitPolicy, generate_load_trace, lag_features, make_training_examples


def test_first_fit_uses_first_sufficient_host():
    policy = FirstFitPolicy()
    loads = np.array([0.20, 0.50, 0.10])
    assert policy.choose_host(0, 0.25, loads) == 0


def test_best_fit_uses_smallest_sufficient_host():
    policy = BestFitPolicy()
    loads = np.array([0.20, 0.50, 0.10])
    assert policy.choose_host(0, 0.25, loads) == 1


def test_trace_contains_midpoint_shift():
    trace = generate_load_trace(100)
    before = trace[trace.time < 60].groupby('vm_id').load.mean()
    after = trace[trace.time >= 60].groupby('vm_id').load.mean()
    assert (after > before).sum() >= 5


def test_features_use_history_only():
    history = [0.1, 0.2, 0.3, 0.25, 0.28, 0.35]
    x = lag_features(history, 6)
    assert x.shape == (8,)
    X, y = make_training_examples(history + [0.4], 6)
    assert X.shape[0] == 1
    assert np.isclose(y[0], 0.4)
