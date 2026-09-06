import numpy as np
import pandas as pd
import pytest
from sklearn.base import clone

from src.data.dataset import BINARY, FEATURES, split_data, validate
from src.models.candidates import candidates


def test_remote_loading_uses_memory_without_creating_files(frame, monkeypatch, tmp_path):
    import hashlib
    from io import BytesIO

    from src.data import dataset

    content = frame.to_csv(index=False).encode("utf-8")
    settings = dataset.config()
    settings["dataset_sha256"] = hashlib.sha256(content).hexdigest()
    monkeypatch.setattr(dataset, "config", lambda: settings)
    monkeypatch.setattr(dataset, "urlopen", lambda *args, **kwargs: BytesIO(content))
    monkeypatch.chdir(tmp_path)
    pd.testing.assert_frame_equal(dataset.load_data(), frame)
    assert list(tmp_path.iterdir()) == []


def test_changed_remote_content_is_rejected(monkeypatch):
    from io import BytesIO

    from src.data import dataset

    monkeypatch.setattr(dataset, "urlopen", lambda *args, **kwargs: BytesIO(b"modified"))
    with pytest.raises(ValueError, match="Checksum"):
        dataset.read_remote_bytes()


@pytest.fixture
def frame():
    rng = np.random.default_rng(42)
    df = pd.DataFrame(rng.integers(1, 100, (80, 20)), columns=FEATURES)
    df[BINARY] = rng.integers(0, 2, (80, len(BINARY)))
    df["n_cores"] = rng.integers(1, 9, 80)
    df["price_range"] = np.tile([0, 1, 2, 3], 20)
    return df


def test_split_is_disjoint_stratified_and_reproducible(frame):
    x_train, x_test, y_train, y_test = split_data(validate(frame))
    assert set(x_train.index).isdisjoint(x_test.index)
    assert set(x_train.index) | set(x_test.index) == set(frame.index)
    assert y_test.value_counts().to_dict() == {0: 4, 1: 4, 2: 4, 3: 4}
    assert len(y_train) == 64
    assert "price_range" not in x_train
    pd.testing.assert_frame_equal(x_train, split_data(frame)[0])


@pytest.mark.parametrize(
    "corruption", ["missing", "infinite", "binary", "target", "duplicate", "column"]
)
def test_invalid_data_is_rejected(frame, corruption):
    if corruption == "missing":
        frame.loc[0, "ram"] = np.nan
    elif corruption == "infinite":
        frame["ram"] = frame.ram.astype(float)
        frame.loc[0, "ram"] = np.inf
    elif corruption == "binary":
        frame.loc[0, "wifi"] = 4
    elif corruption == "target":
        frame.loc[0, "price_range"] = 9
    elif corruption == "duplicate":
        frame.loc[1] = frame.loc[0]
    else:
        frame = frame.drop(columns="ram")
    with pytest.raises(ValueError):
        validate(frame)


def test_scaling_is_learned_from_training_only(frame):
    x_train, x_test, y_train, _ = split_data(frame)
    pipeline = clone(candidates()["logistic_regression"][0]).fit(x_train, y_train)
    np.testing.assert_allclose(pipeline.named_steps["scale"].mean_, x_train.mean())
    original = pipeline.named_steps["scale"].mean_.copy()
    pipeline.predict(x_test * 10)
    np.testing.assert_array_equal(original, pipeline.named_steps["scale"].mean_)
