# Clasificación de gamas de precio de celulares

Proyecto de Aprendizaje automático en la nube — Especialización en Ciencia de Datos e IA,
Universidad de Medellín.

**Integrantes:** Carolina Tirado Osorio, [Yerlith Zabala](https://github.com/Yerlith)
y [Ana Catalina Gaviria](https://github.com/catalinagaviriamet-spec).
**Entrega:** sábado 12 de septiembre de 2026.

El diseño del proyecto se ha trabajado conjuntamente entre las tres integrantes:
la definición del problema, la selección de datos y las decisiones metodológicas
se discuten en equipo. La revisión y el desarrollo de las siguientes fases también
se realizarán de forma conjunta. Consulte la [guía de colaboración](docs/colaboracion.md).

## Problema y objetivo

Apoyar a una fábrica hipotética en la clasificación de un celular en una gama de precio
a partir de 20 especificaciones técnicas. price_range contiene cuatro categorías:
0 bajo, 1 medio, 2 alto y 3 muy alto. El modelo predice una gama; no calcula precios en
pesos ni reemplaza una evaluación comercial con costos, competencia y demanda.

Usamos el [CSV indicado por el equipo](https://github.com/Yerlith/Aprendizaje-automatico/blob/25f42d01c0f239d5b5daf51cb48b4370404a3ffb/data/mobile_prices.csv),
con 2.000 filas, 20 predictores y 500 casos por clase.
La procedencia, unidades y limitaciones están en el [diccionario](docs/dataset.md).
Las instrucciones originales se conservan sin cambios en [README.profe](README.profe).

## Qué está implementado

- Lectura remota en memoria de una versión fija del dataset y verificación SHA-256.
- Validación de esquema, valores, clases y duplicados.
- Notebooks explicados de EDA, baseline y experimentos.
- Comparación de Dummy, regresión logística, SVM, Random Forest y XGBoost.
- Validación cruzada estratificada de cinco folds y test separado 80/20, semilla 42.
- Tracking en MLflow, registro del mejor pipeline y alias champion si cumple las metas.
- Pruebas unitarias y controles de calidad con Ruff y GitHub Actions.

**Pendientes del proyecto completo:** Prefect y scheduling, API, Docker, reporte de drift
y guía de despliegue. Las carpetas correspondientes se conservan para esas fases.
El workflow deploy.yml sigue siendo una plantilla manual, sin despliegue real.

## Instalación y primer recorrido

Requisitos: Git y [uv](https://docs.astral.sh/uv/getting-started/installation/).
Use Python 3.12; uv puede instalarlo si no está disponible. Ejecute en una terminal:

```sh
git clone https://github.com/catalinagaviriamet-spec/Trabajo-Final-Aprendizaje-Automatico.git
cd Trabajo-Final-Aprendizaje-Automatico
uv sync --locked --python 3.12
uv run python -m src.data.dataset
uv run python -m src.models.train
uv run jupyter lab
```

uv sync crea .venv e instala las versiones de uv.lock. No necesita activar el
entorno cuando usa uv run. La lectura por URL requiere Internet, sin descarga manual, CSV local ni cuenta Kaggle.
Abra los notebooks en orden 01, 02 y 03. En Jupyter seleccione el kernel Python 3
del entorno del proyecto. El notebook 03 muestra los resultados guardados; si faltan,
ejecuta el entrenamiento. Los resultados incluidos en GitHub se pueden leer sin entrenar.

Para repetir el experimento ejecute de nuevo el comando de entrenamiento.
Se crean nuevas ejecuciones MLflow y se reemplazan los reportes locales. Repetir con la
misma configuración verifica reproducción; no convierte el test en un conjunto nuevo.

## Resultados y selección

Primer experimento: ganó la regresión logística (C=10), con F1 macro CV de 0.9630.
En test obtuvo **97.5 % de accuracy (390/400)** y **F1 macro de 0.9750**.
Verificación local: 10 pruebas aprobadas y tres notebooks ejecutados sin errores.

Consulte la [comparación por validación cruzada](docs/results/leaderboard.csv), la
[evaluación final](docs/results/evaluation.json) y el [resumen interpretado](docs/resultados.md).

El criterio de selección es el mayor F1 macro medio en entrenamiento con validación
cruzada. El test de 400 celulares solo se evalúa para el ganador. Las metas iniciales
propuestas son F1 macro >= 0.90 y recall >= 0.85 por clase; no son umbrales del profesor.
No se asume que los algoritmos más complejos sean los mejores.

## Abrir MLflow

Desde la raíz, en otra terminal:

```sh
uv run mlflow ui --backend-store-uri sqlite:///mlflow.db --host 127.0.0.1 --port 5000
```

Abra http://127.0.0.1:5000 y busque mobile-price-classification. En Models aparece
mobile-price-classifier. El alias champion se asigna solo si pasa las metas académicas.
MLflow y el modelo binario son locales; para reconstruirlos en otro equipo ejecute el
entrenamiento. Los artefactos no se suben a GitHub.

## Calidad

```sh
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

CI ejecuta estas verificaciones en cada push y pull request. No entrena modelos ni
consume servicios cloud. .pre-commit-config.yaml contiene hooks opcionales que usan
uv; para activarlos instale pre-commit y ejecute pre-commit install.

## Organización del repositorio

| Ruta | Contenido |
|---|---|
| configs/training.json | Fuente fija, checksum, partición, metas y semilla |
| src/data/ | Lectura por URL y contrato de datos |
| src/features/ | Preprocesamiento dentro del pipeline |
| src/models/ | Candidatos, búsqueda, evaluación y tracking |
| notebooks/ | EDA, baseline y lectura de experimentos |
| tests/unit/ | Contrato, particiones y aislamiento del escalado |
| docs/ | Dataset, plan, cronograma y resultados |
| src/api/, src/monitoring/ | Reservadas para siguientes fases |
| data/, models/, logs/ | Carpetas de estructura; data permanece vacía; modelos y logs ignorados por Git |
| scripts/build_notebooks.py | Reconstruye fuentes de notebooks; borra sus salidas al ejecutarse |
| .github/workflows/ | CI implementado y despliegue pendiente |

## Plan y limitaciones

Consulte el [cronograma diario del 6 al 12 de septiembre](docs/plan_proyecto.md),
con responsabilidad y revisión conjunta. Cada integrante debe aportar commits propios y entender el flujo.

La RAM puede estar asociada con la gama, pero correlación no significa causalidad.
Existen ceros cuestionables en dimensiones de pantalla; se documentan y se conservan
en el primer experimento. No hay fechas ni precios monetarios: no se ha demostrado
vigencia comercial ni drift real. Se necesita validación externa antes de uso empresarial.

El profesor menciona rubrica-instructor.md, datasets-curados.md,
mvp-minimo-aprobable.md, peer-review-template.md y starter-template/; esos
materiales aún no fueron adjuntados y sus enlaces relativos en README.profe no funcionan.
