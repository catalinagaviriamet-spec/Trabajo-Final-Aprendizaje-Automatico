# Ficha del modelo

Generada por `make model-card` desde `docs/results/evaluation.json`.

- Modelo: logistic_regression; parámetros: {'model__C': 10}.
- Selección: validación cruzada en entrenamiento; test reservado de 400 filas.
- Accuracy: 0.9750; F1 macro: 0.9750.
- SHA-256 de datos: `f9e8cd3154b8684a1be0ff401b1fba7750710af6bd076a399c6ce7ceb979c624`.
- Preprocesamiento: incluido dentro del pipeline sklearn registrado.
- Uso: demostración académica de gamas 0–3, no precios monetarios ni decisión comercial real.
- Promoción: entrenamiento registra `candidate`; el comando separado `make promote` evalúa el gate.

## Resultados desglosados por clase real

| Clase | Casos | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| 0 | 100 | 0.9899 | 0.9800 | 0.9849 |
| 1 | 100 | 0.9796 | 0.9600 | 0.9697 |
| 2 | 100 | 0.9515 | 0.9800 | 0.9655 |
| 3 | 100 | 0.9800 | 0.9800 | 0.9800 |

Estas clases son subgrupos del resultado, no grupos demográficos. No se dispone de
fabricante, país, fechas o atributos sensibles para evaluar equidad por esos grupos.
El test no representa celulares actuales; no prueba generalización comercial.
No se ajustan hiperparámetros después de revisar los errores de test.

## Reproducibilidad

Tolerancia absoluta declarada: 0,005 para accuracy y F1 macro respecto al resultado
publicado (0,975 y 0,9750347085). Diferencias mayores exigen investigar entorno/datos,
no cambiar la referencia para que el chequeo pase. Semillas y particiones están fijadas.
