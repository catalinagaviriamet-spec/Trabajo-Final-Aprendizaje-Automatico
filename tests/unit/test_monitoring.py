import numpy as np
import pandas as pd
import pytest

from src.data.dataset import FEATURES, split_data
from src.monitoring.drift import calibrate, compare, distance, make_batches


def test_distance_handles_ties_and_binary_data():
    assert distance([0, 0, 1, 1], [0, 0, 1, 1]) == 0
    assert distance([0, 0, 0, 0], [1, 1, 1, 1]) == 1
    assert distance([0, 0, 1, 1], [0, 1, 1, 1]) == 0.25


def test_shift_alert_and_unchanged_columns():
    reference = pd.DataFrame(np.tile(np.arange(200)[:, None], (1, 20)), columns=FEATURES)
    current = reference.copy()
    assert compare(reference, current, 0.15)["alert_features"] == []
    current["ram"] += 1000
    assert compare(reference, current, 0.15)["alert_features"] == ["ram"]


def test_invalid_and_small_batches():
    with pytest.raises(ValueError):
        distance([1, np.nan], [1, 2])
    frame = pd.DataFrame(np.ones((200, 20)), columns=FEATURES)
    with pytest.raises(ValueError):
        compare(frame, frame.iloc[:10], 0.1)
    with pytest.raises(ValueError):
        compare(frame, frame.rename(columns={"ram": "other"}), 0.1)


def test_calibration_reproducible():
    rng = np.random.default_rng(3)
    frame = pd.DataFrame(rng.normal(size=(400, 20)), columns=FEATURES)
    settings = {"seed": 7, "permutations": 19, "quantile": 0.95}
    a = calibrate(frame.iloc[:200], frame.iloc[200:], settings)
    assert 0 < a < 1
    assert a == calibrate(frame.iloc[:200], frame.iloc[200:], settings)


def test_monitoring_excludes_test_and_keeps_batches_disjoint():
    rng = np.random.default_rng(5)
    frame = pd.DataFrame(rng.integers(1, 100, size=(1000, 20)), columns=FEATURES)
    frame["price_range"] = np.tile([0, 1, 2, 3], 250)
    settings = {"seed": 2026, "ram_shift_mb": 1000, "battery_multiplier": 1.3}
    reference, calibration, current, shifted = make_batches(frame, settings)
    _, test, _, _ = split_data(frame)
    batches = [set(x.index) for x in [reference, calibration, current, test]]
    for i, a in enumerate(batches):
        for b in batches[i + 1 :]:
            assert a.isdisjoint(b)
    assert list(reference.columns) == FEATURES
    pd.testing.assert_frame_equal(
        current.drop(columns=["ram", "battery_power"]),
        shifted.drop(columns=["ram", "battery_power"]),
    )
    np.testing.assert_array_equal(shifted.ram - current.ram, 1000)
