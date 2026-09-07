"""Evita publicar salidas y rutas del entorno sin impedir ejecutar notebooks localmente."""

import argparse
import json

from src.data.dataset import ROOT


def main(check=False):
    dirty = []
    for path in sorted((ROOT / "notebooks").glob("*.ipynb")):
        notebook = json.loads(path.read_text(encoding="utf-8"))
        changed = False
        for cell in notebook["cells"]:
            if cell["cell_type"] == "code":
                changed |= bool(cell.get("outputs") or cell.get("execution_count") is not None)
                cell["outputs"] = []
                cell["execution_count"] = None
                cell["metadata"] = {}
        if changed:
            dirty.append(path.name)
            if not check:
                path.write_text(
                    json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8"
                )
    if check and dirty:
        raise SystemExit("Notebooks con salidas: " + ", ".join(dirty))
    print("Notebooks sin salidas publicables.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    main(parser.parse_args().check)
