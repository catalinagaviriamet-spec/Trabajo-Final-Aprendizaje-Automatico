"""Prueba HTTP contra la API en ejecución: python -m scripts.verify_api."""

import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from src.data.dataset import ROOT


def verify():
    base = "http://127.0.0.1:8000"
    with urlopen(f"{base}/health", timeout=10) as response:
        assert json.load(response)["model_loaded"]
    example = json.loads((ROOT / "configs/prediction_example.json").read_text())
    request = Request(
        f"{base}/predict",
        data=json.dumps(example).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urlopen(request, timeout=10) as response:
        prediction = json.load(response)
        assert prediction["price_range"] in range(4)
        assert prediction["label"]
    request.data = b"{}"
    try:
        urlopen(request, timeout=10)
    except HTTPError as error:
        assert error.code == 422
    else:
        raise AssertionError("La API aceptó especificaciones incompletas")
    print(json.dumps({"health": "ok", "prediction": prediction, "invalid_request": 422}))


if __name__ == "__main__":
    verify()
