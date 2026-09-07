"""Genera reportes agregados: python -m src.monitoring."""

import argparse
import html
import json
from pathlib import Path

from src.data.dataset import ROOT, config, load_data
from src.monitoring.drift import calibrate, compare, make_batches


def render(report):
    sections = []
    for title, key in [("Lote sin alteraciones", "control"), ("Cambio simulado", "simulated")]:
        result = report[key]
        alerts = ", ".join(result["alert_features"]) or "Ninguna"
        rows = "".join(
            f"<tr><td>{html.escape(row['feature'])}</td>"
            f"<td>{row['reference_mean']:.2f}</td><td>{row['current_mean']:.2f}</td>"
            f'<td><meter min="0" max="1" value="{row["distance"]}"></meter> '
            f"{row['distance']:.4f}</td><td>{'REVISAR' if row['alert'] else 'Sin alerta'}</td></tr>"
            for row in result["features"]
        )
        sections.append(
            f"<h2>{title}</h2><p>Variables con alerta: <b>{alerts}</b></p>"
            "<table><thead><tr><th>Variable</th><th>Media referencia</th>"
            "<th>Media lote</th><th>Distancia (0–1)</th><th>Resultado</th>"
            f"</tr></thead><tbody>{rows}</tbody></table>"
        )
    return (
        '<!doctype html><html lang="es"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        "<title>Monitoreo de celulares</title><style>"
        "body{font:16px system-ui;max-width:1100px;margin:40px auto;padding:0 20px;"
        "color:#172b4d;background:#f5f7fb}table{border-collapse:collapse;width:100%;"
        "background:white}td,th{padding:10px;text-align:left;border-bottom:1px solid #ddd}"
        "th{background:#dce7f7}meter{width:100px}h1,h2{color:#174b77}"
        "</style><h1>Monitoreo de datos de celulares</h1>"
        "<p><strong>Demostración simulada. No son datos nuevos de producción.</strong></p>"
        f"<p>Referencia: {report['reference_rows']} filas. "
        f"Calibración: {report['calibration_rows']}. Cada lote comparado: {report['current_rows']}. "
        "Son subconjuntos del entrenamiento; el test reservado no se utiliza.</p>"
        f"<p>Alerta si distancia &gt; <b>{report['threshold']:.4f}</b>. "
        "Umbral calibrado antes de observar el lote comparado. "
        "Una alerta indica cambio en los datos, no pérdida demostrada de precisión.</p>"
        f"<p>Simulación: RAM +{report['settings']['ram_shift_mb']} MB y batería "
        f"×{report['settings']['battery_multiplier']} sobre el mismo lote de control. "
        "Solo se guardan estadísticas agregadas, nunca filas del dataset.</p>"
        + "".join(sections)
        + "<h2>Qué hacemos ante una alerta</h2><p>Revisar unidades, fuente y composición "
        "del lote; obtener etiquetas reales y evaluar el rendimiento antes de decidir "
        "un reentrenamiento. No modificar ni reemplazar automáticamente el modelo.</p>"
        "<p>Sin alerta no significa ausencia de todo cambio: esta prueba revisa cada "
        "variable por separado y puede omitir cambios en relaciones entre variables.</p></html>"
    )


def run(output):
    settings = json.loads((ROOT / "configs/monitoring.json").read_text())
    reference, calibration, current, shifted = make_batches(load_data(), settings)
    threshold = calibrate(reference, calibration, settings)
    report = {
        "kind": "simulation_not_production",
        "dataset_sha256": config()["dataset_sha256"],
        "settings": settings,
        "reference_rows": len(reference),
        "calibration_rows": len(calibration),
        "current_rows": len(current),
        "test_used": False,
        "threshold": threshold,
        "control": compare(reference, current, threshold, settings["minimum_batch_rows"]),
        "simulated": compare(reference, shifted, threshold, settings["minimum_batch_rows"]),
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "drift.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (output / "drift.html").write_text(render(report), encoding="utf-8")
    print(
        json.dumps(
            {
                "threshold": threshold,
                "control": report["control"]["alert_features"],
                "simulated": report["simulated"]["alert_features"],
            }
        )
    )
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "docs/results/monitoring")
    run(parser.parse_args().output)
