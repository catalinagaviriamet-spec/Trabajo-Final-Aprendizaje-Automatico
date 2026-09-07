"""Distancias entre distribuciones y calibración conjunta por permutaciones."""

import numpy as np
import pandas as pd

from src.data.dataset import FEATURES, split_data


def distance(reference, current):
    """Máxima distancia entre CDF empíricas; admite empates y variables binarias."""
    a, b = np.sort(np.asarray(reference)), np.sort(np.asarray(current))
    if not len(a) or not len(b) or not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError("Se requieren muestras no vacías, numéricas y finitas.")
    points = np.unique(np.concatenate([a, b]))
    return float(
        np.max(
            np.abs(
                np.searchsorted(a, points, side="right") / len(a)
                - np.searchsorted(b, points, side="right") / len(b)
            )
        )
    )


def validate_batch(frame):
    if list(frame.columns) != FEATURES or frame.empty:
        raise ValueError("El lote debe contener exactamente los 20 predictores en orden.")
    if not all(pd.api.types.is_numeric_dtype(t) for t in frame.dtypes):
        raise ValueError("Los predictores deben ser numéricos.")
    if not np.isfinite(frame.to_numpy()).all():
        raise ValueError("El lote contiene faltantes o infinitos.")


def distances(reference, current):
    validate_batch(reference)
    validate_batch(current)
    return {column: distance(reference[column], current[column]) for column in FEATURES}


def make_batches(frame, settings):
    # No se consulta el test reservado ni se usa price_range como variable de drift.
    train, _, _, _ = split_data(frame)
    shuffled = train.iloc[np.random.default_rng(settings["seed"]).permutation(len(train))]
    half, quarter = len(train) // 2, len(train) // 4
    reference = shuffled.iloc[:half].copy()
    calibration = shuffled.iloc[half : half + quarter].copy()
    current = shuffled.iloc[half + quarter :].copy()
    shifted = current.copy()
    shifted["ram"] = shifted.ram + settings["ram_shift_mb"]
    shifted["battery_power"] = (
        (shifted.battery_power * settings["battery_multiplier"]).round().astype(int)
    )
    return reference, calibration, current, shifted


def calibrate(reference, calibration, settings):
    """Umbral empírico sobre el máximo de las 20 distancias, no 20 tests aislados."""
    validate_batch(reference)
    validate_batch(calibration)
    pool = pd.concat([reference, calibration], ignore_index=True)
    rng = np.random.default_rng(settings["seed"])
    maxima = []
    for _ in range(settings["permutations"]):
        order = rng.permutation(len(pool))
        scores = distances(pool.iloc[order[: len(reference)]], pool.iloc[order[len(reference) :]])
        maxima.append(max(scores.values()))
    return float(np.quantile(maxima, settings["quantile"], method="higher"))


def compare(reference, current, threshold, minimum_rows=200):
    if min(len(reference), len(current)) < minimum_rows:
        raise ValueError(f"Se requieren al menos {minimum_rows} filas por lote.")
    scores = distances(reference, current)
    rows = [
        {
            "feature": column,
            "distance": scores[column],
            "alert": scores[column] > threshold,
            "reference_mean": float(reference[column].mean()),
            "current_mean": float(current[column].mean()),
        }
        for column in FEATURES
    ]
    return {"alert_features": [r["feature"] for r in rows if r["alert"]], "features": rows}
