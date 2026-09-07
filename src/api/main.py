"""Sirve el pipeline completo, incluido su preprocesamiento."""

import json
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, ConfigDict, Field

from src.data.dataset import FEATURES, ROOT

Binary = Annotated[int, Field(strict=True, ge=0, le=1)]
Nonnegative = Annotated[int, Field(strict=True, ge=0)]
Positive = Annotated[int, Field(strict=True, gt=0)]
LABELS = ["Precio bajo", "Precio medio", "Precio alto", "Precio muy alto"]


class Phone(BaseModel):
    """Especificaciones en las unidades del diccionario del dataset."""

    model_config = ConfigDict(
        extra="forbid",
        allow_inf_nan=False,
        json_schema_extra={
            "example": json.loads((ROOT / "configs/prediction_example.json").read_text())
        },
    )
    battery_power: Positive
    blue: Binary
    clock_speed: Annotated[float, Field(ge=0)]
    dual_sim: Binary
    fc: Nonnegative
    four_g: Binary
    int_memory: Nonnegative
    m_dep: Annotated[float, Field(ge=0)]
    mobile_wt: Positive
    n_cores: Annotated[int, Field(strict=True, ge=1, le=8)]
    pc: Nonnegative
    px_height: Nonnegative
    px_width: Positive
    ram: Positive
    sc_h: Nonnegative
    sc_w: Nonnegative
    talk_time: Nonnegative
    three_g: Binary
    touch_screen: Binary
    wifi: Binary


def create_app(model_path=None):
    path = Path(model_path or os.environ.get("MODEL_PATH", ROOT / "models/best_model.joblib"))

    @asynccontextmanager
    async def lifespan(app):
        # Solo cargar el artefacto generado por nuestro entrenamiento, nunca un archivo del cliente.
        app.state.model = joblib.load(path) if path.is_file() else None
        metadata = path.with_name("model_metadata.json")
        app.state.model_version = (
            json.loads(metadata.read_text()).get("candidate") if metadata.is_file() else None
        )
        yield

    app = FastAPI(
        title="Clasificador de gamas de celulares",
        description="Predice una categoría de 0 a 3; no un precio monetario.",
        lifespan=lifespan,
    )

    def ready():
        if app.state.model is None:
            raise HTTPException(503, "Modelo ausente. Ejecute el entrenamiento y reinicie la API.")
        return app.state.model

    @app.get("/", include_in_schema=False)
    def home():
        return RedirectResponse("/docs")

    @app.get("/health")
    def health():
        ready()
        return {"status": "ok", "model_loaded": True, "model_version": app.state.model_version}

    @app.post("/predict")
    def predict(phone: Phone):
        model = ready()
        frame = pd.DataFrame([phone.model_dump()], columns=FEATURES)
        category = int(model.predict(frame)[0])
        return {"price_range": category, "label": LABELS[category]}

    return app


app = create_app()
