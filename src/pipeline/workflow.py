"""Prefect controla el orden y los estados; MLflow registra los experimentos."""

import json
from datetime import UTC, datetime
from importlib.metadata import version
from io import BytesIO
from urllib.error import HTTPError, URLError

import pandas as pd
from prefect import flow, get_run_logger, task
from prefect.cache_policies import NO_CACHE

from src.data.dataset import ROOT, config, read_remote_bytes, validate
from src.models.train import train


def retry_network_error(task, task_run, state):
    """Reintenta fallos transitorios, no cambios del checksum ni errores de esquema."""
    try:
        state.result()
    except HTTPError as error:
        return error.code == 429 or error.code >= 500
    except (URLError, TimeoutError, ConnectionError):
        return True
    except Exception:  # noqa: BLE001 - cualquier otro error debe fallar sin reintentos
        return False
    return False


@task(
    name="leer-url-en-memoria",
    persist_result=False,
    cache_policy=NO_CACHE,
    retries=2,
    retry_delay_seconds=5,
    retry_condition_fn=retry_network_error,
)
def read_dataset():
    content = read_remote_bytes()
    get_run_logger().info(
        "Fuente pública verificada por SHA-256; lectura exclusivamente en memoria."
    )
    return pd.read_csv(BytesIO(content))


@task(name="validar-datos", persist_result=False, cache_policy=NO_CACHE)
def validate_dataset(frame):
    validate(frame)
    get_run_logger().info(
        "Contrato aprobado: %s filas y %s predictores.", len(frame), len(frame.columns) - 1
    )
    return frame


@flow(name="preparar-datos", persist_result=False, log_prints=False)
def prepare_dataset():
    """Si lectura o validación fallan, no se alcanza el entrenamiento."""
    return validate_dataset(read_dataset())


@task(name="entrenar-evaluar-registrar", persist_result=False, cache_policy=NO_CACHE, retries=0)
def train_model(frame):
    # El escalado y la partición siguen dentro del código probado; no se vuelve a leer la URL.
    return train(frame=frame)


@flow(name="mobile-prices-pipeline", persist_result=False, log_prints=True)
def training_pipeline(validate_only: bool = False):
    """Orquesta el experimento fijo. No recibe ni registra filas como parámetros del flow."""
    frame = prepare_dataset()
    summary = {
        "mode": "validation" if validate_only else "training",
        "rows": len(frame),
        "predictors": len(frame.columns) - 1,
        "dataset_sha256": config()["dataset_sha256"],
        "prefect_version": version("prefect"),
    }
    if not validate_only:
        evaluation = train_model(frame)
        summary.update(
            {
                "winner": evaluation["winner"],
                "metrics": evaluation["metrics"],
                "acceptance_passed": evaluation["acceptance_passed"],
            }
        )
    summary["completed_at_utc"] = datetime.now(UTC).isoformat()
    # Solo metadatos y métricas, nunca registros del CSV.
    logs = ROOT / "logs"
    logs.mkdir(exist_ok=True)
    (logs / "pipeline_last_run.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    get_run_logger().info("Flujo completado: %s", summary)
    return summary
