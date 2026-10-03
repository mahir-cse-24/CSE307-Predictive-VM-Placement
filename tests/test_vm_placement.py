import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from vm_placement import BestFit, FirstFit, generate_load_trace, lag_features, predictive_repack


def test_first_fit():
    h = np.array([0.20, 0.50, 0.10])
    assert FirstFit().choose(0.25, h) == 0


def test_best_fit():
    h = np.array([0.20, 0.50, 0.10])
    assert BestFit().choose(0.25, h) == 1


def test_shift_changes_demand():
    trace = generate_load_trace(100)
    before = trace[trace.time < 60].groupby("vm_id").load.mean()
    after = trace[trace.time >= 60].groupby("vm_id").load.mean()
    assert (after > before).sum() >= 5


def test_feature_shape():
    assert lag_features([0.1, 0.2, 0.3, 0.4, 0.3, 0.35], 6).shape == (8,)


def test_predictive_repack_respects_target_when_possible():
    assignment = {0: 0, 1: 0, 2: 1, 3: 1}
    predicted = np.array([0.5, 0.45, 0.2, 0.2])
    new_assignment = predictive_repack(predicted, assignment, 3, 0.90)
    loads = np.zeros(3)
    for vm, host in new_assignment.items():
        loads[host] += predicted[vm]
    assert loads.max() <= 0.90 + 1e-9
