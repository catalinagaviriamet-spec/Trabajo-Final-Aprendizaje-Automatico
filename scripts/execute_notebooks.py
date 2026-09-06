"""Ejecuta los tres notebooks usando exactamente el Python del entorno activo."""

import sys
import tempfile
from pathlib import Path

import nbformat
from jupyter_client.kernelspec import KernelSpecManager
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]

with tempfile.TemporaryDirectory() as kernel_dir:
    kernel = Path(kernel_dir) / "python-project"
    kernel.mkdir()
    import json

    (kernel / "kernel.json").write_text(
        json.dumps(
            {
                "argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
                "display_name": "Python del proyecto",
                "language": "python",
            }
        ),
        encoding="utf-8",
    )
    manager = KernelSpecManager(kernel_dirs=[kernel_dir])
    from jupyter_client import KernelManager

    for path in sorted((ROOT / "notebooks").glob("*.ipynb")):
        print(f"Ejecutando {path.name}...", flush=True)
        nb = nbformat.read(path, as_version=4)
        nbformat.validate(nb)
        km = KernelManager(kernel_name="python-project", kernel_spec_manager=manager)
        NotebookClient(
            nb, km=km, timeout=600, resources={"metadata": {"path": str(ROOT)}}
        ).execute()
        nbformat.validate(nb)
        nbformat.write(nb, path)
        print(f"OK: {path.name}", flush=True)
