"""Genera la ficha desde la evaluación, para no mantener métricas escritas a mano."""

import json

from src.data.dataset import ROOT


def main():
    evaluation = json.loads((ROOT / "docs/results/evaluation.json").read_text())
    metrics = evaluation["metrics"]
    rows = []
    for group in range(4):
        result = evaluation["classification_report"][str(group)]
        rows.append(
            f"| {group} | {result['support']:.0f} | {result['precision']:.4f} | "
            f"{result['recall']:.4f} | {result['f1-score']:.4f} |"
        )
    text = f"""# Ficha del modelo

Generada por `make model-card` desde `docs/results/evaluation.json`.

- Modelo: {evaluation["winner"]}; parámetros: {evaluation["best_params"]}.
- Selección: validación cruzada en entrenamiento; test reservado de {evaluation["test_rows"]} filas.
- Accuracy: {metrics["test_accuracy"]:.4f}; F1 macro: {metrics["test_f1_macro"]:.4f}.
- SHA-256 de datos: `{evaluation["dataset_sha256"]}`.
- Preprocesamiento: incluido dentro del pipeline sklearn registrado.
- Uso: demostración académica de gamas 0–3, no precios monetarios ni decisión comercial real.
- Promoción: entrenamiento registra `candidate`; el comando separado `make promote` evalúa el gate.

## Resultados desglosados por clase real

| Clase | Casos | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
{chr(10).join(rows)}

Estas clases son subgrupos del resultado, no grupos demográficos. No se dispone de
fabricante, país, fechas o atributos sensibles para evaluar equidad por esos grupos.
El test no representa celulares actuales; no prueba generalización comercial.
No se ajustan hiperparámetros después de revisar los errores de test.

## Reproducibilidad

Tolerancia absoluta declarada: 0,005 para accuracy y F1 macro respecto al resultado
publicado (0,975 y 0,9750347085). Diferencias mayores exigen investigar entorno/datos,
no cambiar la referencia para que el chequeo pase. Semillas y particiones están fijadas.
"""
    (ROOT / "docs/model-card.md").write_text(text, encoding="utf-8")
    print("docs/model-card.md generado.")


if __name__ == "__main__":
    main()
