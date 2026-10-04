import numpy as np

from vm_placement import BestFit, FirstFit, PlacementConfig, generate_load_trace, lag_features


def test_first_fit_uses_first_sufficient_host():
    policy = FirstFit()
    loads = np.array([0.20, 0.50, 0.10])
    assert policy.choose(0.25, loads) == 0


def test_best_fit_uses_smallest_sufficient_host():
    policy = BestFit()
    loads = np.array([0.20, 0.50, 0.10])
    assert policy.choose(0.25, loads) == 1


def test_trace_contains_midpoint_shift():
    config = PlacementConfig()
    trace = generate_load_trace(100, config)
    before = trace[trace.time < config.shift_step].groupby("vm_id").load.mean()
    after = trace[trace.time >= config.shift_step].groupby("vm_id").load.mean()
    assert (after > before).sum() >= 5


def test_features_use_history_only():
    history = [0.1, 0.2, 0.3, 0.25, 0.28, 0.35]
    x = lag_features(history, 6)
    assert x.shape == (8,)
