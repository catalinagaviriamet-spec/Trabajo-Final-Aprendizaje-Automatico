"""Falla pronto si el entorno, la fuente remota o el directorio de salida no funcionan."""

import importlib
import sys
import tempfile

from src.data.dataset import ROOT, load_data


def main():
    if sys.version_info[:2] != (3, 12):
        raise SystemExit("Este proyecto requiere Python 3.12; ejecute make setup.")
    for name in ["pandas", "numpy", "sklearn", "xgboost", "mlflow", "prefect", "fastapi"]:
        importlib.import_module(name)
    frame = load_data()
    with tempfile.TemporaryDirectory(dir=ROOT):
        pass
    print(f"Entorno y fuente verificados: {len(frame)} filas en memoria. Sin credenciales.")


if __name__ == "__main__":
    main()
