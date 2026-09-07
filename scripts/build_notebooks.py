"""Genera notebooks didácticos; ejecutar solo para reconstruir sus fuentes."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)}


def code(text):
    return {
        "cell_type": "code",
        "metadata": {},
        "source": text.splitlines(keepends=True),
        "execution_count": None,
        "outputs": [],
    }


setup = code("""from pathlib import Path
import sys

ROOT = Path.cwd()
if not (ROOT / "README.profe").exists():
    ROOT = ROOT.parent
if not (ROOT / "README.profe").exists():
    raise RuntimeError("Abra Jupyter desde la raíz del proyecto")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from src.data.dataset import load_data, split_data, config

df = load_data()
X_train, X_test, y_train, y_test = split_data(df)
print("Entrenamiento:", X_train.shape, "Test reservado:", X_test.shape)
""")

notebooks = {
    "01_eda": [
        md("""# 01 — Exploración de datos de celulares

**Pregunta:** ¿qué especificaciones se asocian con las cuatro gamas de precio?

EDA significa análisis exploratorio de datos. Primero comprobamos la calidad;
después exploramos exclusivamente las 1.600 filas de entrenamiento. Las 400 de
test se reservan para el final. Ejecute las celdas en orden con el entorno del proyecto.
"""),
        setup,
        md(
            "## 1. Auditoría de estructura\nContar nulos o clases no se utiliza para ajustar modelos."
        ),
        code("""print("Dimensiones:", df.shape)
print("Duplicados:", df.duplicated().sum())
display(pd.DataFrame({"tipo": df.dtypes.astype(str), "nulos": df.isna().sum()}))
display(df.price_range.value_counts().sort_index().rename("filas"))
"""),
        md(
            "## 2. Distribuciones del entrenamiento\nLos códigos de gama tienen orden, pero no son precios monetarios."
        ),
        code("""train = X_train.assign(price_range=y_train)
display(X_train.describe().round(2))
fig, ax = plt.subplots(figsize=(6, 3))
y_train.value_counts().sort_index().plot.bar(ax=ax, color="#267a9e")
ax.set(xlabel="Gama", ylabel="Celulares", title="Clases en entrenamiento")
plt.tight_layout()
plt.show()
"""),
        md(
            "## 3. Valores que merecen revisión\nUn cero en alto de píxeles o ancho físico no describe una pantalla real. Se conserva el dato original y se documenta; no lo sustituimos arbitrariamente."
        ),
        code("""display((X_train[["px_height", "sc_w"]] == 0).sum().rename("ceros en entrenamiento"))
"""),
        md(
            "## 4. Correlación\nSpearman resume asociaciones monotónicas con el orden de las gamas. No demuestra causalidad ni reemplaza la importancia predictiva del modelo."
        ),
        code("""correlation = train.corr(method="spearman")["price_range"].drop("price_range")
display(correlation.sort_values(ascending=False).round(3).rename("Spearman"))
fig, ax = plt.subplots(figsize=(8, 6))
correlation.sort_values().plot.barh(ax=ax, color="#267a9e")
ax.set(title="Asociación con la gama — solo entrenamiento", xlabel="Spearman")
plt.tight_layout()
plt.show()
"""),
        code("""fig, axes = plt.subplots(1, 3, figsize=(12, 3.5))
for column, ax in zip(["ram", "battery_power", "px_width"], axes):
    sns.boxplot(data=train, x="price_range", y=column, ax=ax)
plt.tight_layout()
plt.show()
"""),
        md("""## 5. Decisiones para modelar

- Conservar inicialmente las 20 variables y las filas originales.
- No aplicar sobremuestreo: las clases están equilibradas.
- Escalar para regresión logística y SVM dentro de cada fold; los árboles no lo requieren.
- Contrastar la hipótesis de RAM leyendo la tabla anterior; una asociación fuerte no significa que defina por sí sola el precio.
- No hay fechas: el monitoreo compara particiones reales del dataset como demostración de sesgo de selección, no como vigilancia temporal de producción.

**Para discutir en grupo:** ¿qué variables tienen asociación débil? ¿Puede una variable
con poca correlación ser útil al combinarla con otras? ¿Qué limita trasladar este dataset al mercado actual?
"""),
    ],
    "02_baseline": [
        md("""# 02 — Modelo de referencia

Un baseline es un punto de comparación. DummyClassifier ignora las especificaciones;
la regresión logística aprende a distinguir cuatro categorías (aunque su nombre diga
«regresión», aquí es un clasificador). Solo usamos validación cruzada en entrenamiento.
"""),
        setup,
        code("""from sklearn.model_selection import StratifiedKFold, cross_validate
from src.models.candidates import candidates

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
rows = []
for name in ["dummy", "logistic_regression"]:
    pipeline, _ = candidates()[name]
    scores = cross_validate(pipeline, X_train, y_train, cv=cv,
                            scoring={"f1_macro": "f1_macro", "accuracy": "accuracy"})
    rows.append({"modelo": name, "F1 macro medio": scores["test_f1_macro"].mean(),
                 "desviación F1": scores["test_f1_macro"].std(),
                 "accuracy media": scores["test_accuracy"].mean()})
display(pd.DataFrame(rows).round(4))
"""),
        md("""## Interpretación

Accuracy es la fracción de aciertos. F1 combina precisión y recall; macro promedia
las cuatro clases con igual peso. Predecir siempre una clase da 25 % de accuracy en
datos equilibrados, pero F1 macro no tiene por qué ser 25 %.

El escalador se ajusta dentro de cada fold, nunca con todos los datos antes de validar.
No hemos calculado métricas de test en este notebook. En el siguiente se comparan
algoritmos e hiperparámetros y se documenta la selección final.
"""),
    ],
    "03_experiments": [
        md("""# 03 — Experimentos y evaluación final

Se comparan 12 configuraciones: Dummy, regresión logística, SVM, Random Forest y
XGBoost. Los dos últimos están sugeridos por el profesor. Gana el F1 macro medio
en validación cruzada; test no decide el ganador.

Este notebook muestra la ejecución guardada por `python -m src.models.train`.
Si no existe, la ejecuta. Para reproducir desde cero use ese comando; no cambie
hiperparámetros después de leer test para luego presentar ese mismo test como nuevo.
"""),
        setup,
        code("""import json
from src.models.train import train

results = ROOT / "docs/results"
if not (results / "evaluation.json").exists():
    train()
evaluation = json.loads((results / "evaluation.json").read_text(encoding="utf-8"))
display(pd.read_csv(results / "leaderboard.csv"))
print("Modelo seleccionado por CV:", evaluation["winner"])
print("Parámetros:", evaluation["best_params"])
"""),
        md(
            "## Test reservado\nSon 400 ejemplos que no participaron en el ajuste. Las métricas describen este dataset, no una validación comercial externa."
        ),
        code("""display(pd.Series(evaluation["metrics"], name="valor"))
display(pd.DataFrame(evaluation["classification_report"]).T)
print("Cumple metas académicas propuestas:", evaluation["acceptance_passed"])
from IPython.display import Image, display
display(Image(filename=str(results / "confusion_matrix.png")))
"""),
        md("""## Tracking y registro

La ejecución guarda parámetros, métricas y artefactos en MLflow local (`mlflow.db`).
Para abrirlo, desde la raíz ejecute:

```text
uv run mlflow ui --backend-store-uri sqlite:///mlflow.db --host 127.0.0.1 --port 5000
```

Abra http://127.0.0.1:5000. En el experimento `mobile-price-classification` verá
una ejecución por algoritmo y el CSV con todas sus configuraciones. El mejor pipeline
se registra como `mobile-price-classifier`; recibe alias `candidate`; `make promote` ejecuta el gate antes de asignar `champion`.
La base y los modelos permanecen locales, mientras las métricas se publican en GitHub.

**Siguiente etapa:** explicar los errores, orquestar con Prefect y servir el pipeline
completo. No afirmar que Random Forest o XGBoost son mejores sin leer los resultados.
"""),
    ],
}

for name, cells in notebooks.items():
    for i, cell in enumerate(cells):
        cell["id"] = f"{name}-{i}"
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.12"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    (ROOT / f"notebooks/{name}.ipynb").write_text(
        json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8"
    )
