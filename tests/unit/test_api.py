"""Contrato HTTP y equivalencia con el pipeline, sin descargar datos."""

import json

import joblib
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from sklearn.dummy import DummyClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from src.api.main import create_app
from src.data.dataset import FEATURES, ROOT


@pytest.fixture
def example():
    return json.loads((ROOT / "configs/prediction_example.json").read_text())


def test_prediction_matches_saved_pipeline(tmp_path, example):
    frame = pd.DataFrame([example] * 4, columns=FEATURES)
    model = make_pipeline(StandardScaler(), DummyClassifier(strategy="constant", constant=2))
    model.fit(frame, [0, 1, 2, 3])
    path = tmp_path / "model.joblib"
    joblib.dump(model, path)
    with TestClient(create_app(path)) as client:
        assert client.get("/health").status_code == 200
        # El orden de claves del cliente no cambia el orden de las características.
        response = client.post("/predict", json=dict(reversed(list(example.items()))))
        assert response.status_code == 200
        assert response.json() == {
            "price_range": int(model.predict(frame)[0]),
            "label": "Precio alto",
        }


def test_missing_model_returns_503(tmp_path, example):
    with TestClient(create_app(tmp_path / "absent.joblib")) as client:
        assert client.get("/health").status_code == 503
        assert client.post("/predict", json=example).status_code == 503


@pytest.mark.parametrize(
    "change", [{"ram": -1}, {"wifi": 2}, {"n_cores": 9}, {"price_range": 2}, {"ram": "2000"}]
)
def test_invalid_specifications_rejected(tmp_path, example, change):
    with TestClient(create_app(tmp_path / "absent.joblib")) as client:
        assert client.post("/predict", json=example | change).status_code == 422


def test_missing_field_rejected(tmp_path, example):
    del example["ram"]
    with TestClient(create_app(tmp_path / "absent.joblib")) as client:
        assert client.post("/predict", json=example).status_code == 422
