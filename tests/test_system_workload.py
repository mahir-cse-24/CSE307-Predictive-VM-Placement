from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from system_workload import build_trace, load_trace


def test_trace_is_deterministic(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    build_trace(a, steps=20, pages=128, seed=3072026)
    build_trace(b, steps=20, pages=128, seed=3072026)
    assert a.read_bytes() == b.read_bytes()


def test_two_workers_have_equal_trace_shape(tmp_path):
    p = tmp_path / "trace.csv"
    build_trace(p, steps=40, pages=64, seed=1)
    assert len(load_trace(p, 0)) == 40
    assert len(load_trace(p, 1)) == 40
