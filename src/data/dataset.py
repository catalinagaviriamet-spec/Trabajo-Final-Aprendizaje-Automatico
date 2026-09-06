"""Contrato del CSV y separación estable antes de explorar relaciones."""

import hashlib
import json
from io import BytesIO
from pathlib import Path
from urllib.request import urlopen

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[2]
FEATURES = [
    "battery_power",
    "blue",
    "clock_speed",
    "dual_sim",
    "fc",
    "four_g",
    "int_memory",
    "m_dep",
    "mobile_wt",
    "n_cores",
    "pc",
    "px_height",
    "px_width",
    "ram",
    "sc_h",
    "sc_w",
    "talk_time",
    "three_g",
    "touch_screen",
    "wifi",
]
TARGET = "price_range"
BINARY = ["blue", "dual_sim", "four_g", "three_g", "touch_screen", "wifi"]


def config():
    return json.loads((ROOT / "configs/training.json").read_text(encoding="utf-8"))


def read_remote_bytes():
    """Lee URL pública en memoria. No crea CSV, caché en disco ni pide credenciales."""
    settings = config()
    with urlopen(settings["dataset_url"], timeout=60) as response:
        content = response.read()
    if hashlib.sha256(content).hexdigest() != settings["dataset_sha256"]:
        raise ValueError(
            "Checksum inesperado: el dataset remoto no coincide con la versión fijada."
        )
    return content


def validate(df):
    """Contrato de entrenamiento: los ceros de pantalla se reportan, no se borran."""
    if list(df.columns) != FEATURES + [TARGET]:
        raise ValueError("Columnas faltantes, adicionales o en orden inesperado.")
    if df.empty or not all(pd.api.types.is_numeric_dtype(t) for t in df.dtypes):
        raise ValueError("Se requieren filas y columnas numéricas.")
    if not np.isfinite(df.to_numpy()).all():
        raise ValueError("Hay valores faltantes o infinitos.")
    if df.duplicated(subset=FEATURES).any():
        raise ValueError("Especificaciones duplicadas: revisar antes de separar los datos.")
    if set(df[TARGET].unique()) != {0, 1, 2, 3}:
        raise ValueError("La variable objetivo debe contener las cuatro clases 0, 1, 2 y 3.")
    if not df[BINARY].isin([0, 1]).all().all():
        raise ValueError("Las variables binarias solo admiten 0 y 1.")
    if (df[FEATURES] < 0).any().any():
        raise ValueError("No se admiten especificaciones negativas.")
    if not df.n_cores.between(1, 8).all() or not (df.n_cores % 1 == 0).all():
        raise ValueError("n_cores debe ser entero entre 1 y 8 para este dataset.")
    if (df[["battery_power", "ram", "px_width", "mobile_wt"]] <= 0).any().any():
        raise ValueError("Batería, RAM, ancho en píxeles y peso deben ser positivos.")
    return df


def load_data():
    return validate(pd.read_csv(BytesIO(read_remote_bytes())))


def split_data(df):
    """Mismos índices para EDA, baseline y experimentos; test permanece reservado."""
    settings = config()
    return train_test_split(
        df[FEATURES],
        df[TARGET],
        test_size=settings["test_size"],
        random_state=settings["seed"],
        stratify=df[TARGET],
    )


if __name__ == "__main__":
    frame = load_data()
    print(f"CSV verificado: {frame.shape[0]} filas, {len(FEATURES)} predictores.")
