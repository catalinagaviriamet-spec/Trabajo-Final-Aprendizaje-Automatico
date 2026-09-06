"""Aísla los metadatos de Prefect del perfil personal durante las pruebas."""

import os
from pathlib import Path

os.environ["PREFECT_HOME"] = str(Path(__file__).resolve().parents[1] / "logs/prefect-tests")
os.environ["PREFECT_SERVER_ANALYTICS_ENABLED"] = "false"
