# Clasificación de gamas de precio de celulares

Proyecto de Aprendizaje automático en la nube — Especialización en Ciencia de Datos e IA,
Universidad de Medellín.

**Integrantes:** [Carolina Tirado Osorio](https://github.com/Caro-Tirado), [Yerlith Zabala](https://github.com/Yerlith)
y [Ana Catalina Gaviria](https://github.com/catalinagaviriamet-spec).
**Entrega:** sábado 12 de septiembre de 2026.

El diseño del proyecto se ha trabajado conjuntamente entre las tres integrantes:
la definición del problema, la selección de datos y las decisiones metodológicas
se discuten en equipo. La revisión y el desarrollo de las siguientes fases también
se realizarán de forma conjunta. Consulte la [guía de colaboración](docs/colaboracion.md).

## Abrir y probar la API FastAPI

**[Abrir la API local para hacer una predicción](http://127.0.0.1:8000/docs)**

Este enlace funciona después de iniciar el proyecto con Docker en el mismo PC
donde abre el navegador. `127.0.0.1` significa «este equipo»: GitHub aloja el código,
pero no mantiene la API encendida ni conecta al equipo de las integrantes.

- **Primera vez:** siga [API y Docker en otro PC](#api-y-docker-en-otro-pc).
- **Con la API iniciada:** abra el enlace y seleccione **POST /predict → Try it out → Execute**.
  El ejemplo ya está precargado y devuelve `price_range: 2`, «Precio alto».
- **Para experimentar:** cambie `ram` de 2000 a 1000 y ejecute otra vez;
  con las demás características del ejemplo iguales devuelve «Precio medio».
- **Si no abre:** compruebe que Docker esté funcionando y ejecute
  `docker compose up -d --wait api` desde el repositorio, después de entrenar.

Código de la API: [src/api/main.py](src/api/main.py).
Guía completa de instalación y uso: [docs/docker.md](docs/docker.md).

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
- Pipeline Prefect con validación, reintentos de conexión y programación local configurable.
- API FastAPI de predicción y ejecución reproducible con Docker Compose.
- Reporte de drift con particiones reales y diseño de monitoreo con umbrales y acciones.
- Pruebas unitarias y controles de calidad con Ruff y GitHub Actions.

**Pendientes de cierre:** revisión conjunta de la entrega y contribuciones individuales. La [revisión de la rúbrica](docs/revision-rubrica.md) distingue evidencias y límites frente al nivel 5.
El workflow deploy.yml sigue siendo una plantilla manual, sin despliegue real.

## Comandos de la rúbrica

Con Git, uv y Make instalados: `make setup`, `make smoke`, `make train` y `make promote`, en ese orden. En Windows puede usar Make desde WSL o los comandos `uv run` equivalentes. `make check` ejecuta calidad, pruebas y control de outputs; `make model-card` genera la ficha. Tolerancia de reproducción: ±0,005 en accuracy y F1 macro respecto al resultado publicado. Las salidas de notebooks se limpian antes de publicar con `uv run python -m scripts.notebook_outputs`.

## Inicio rápido

Requisitos: Git y [uv](https://docs.astral.sh/uv/getting-started/installation/).
Este proyecto usa Python 3.12. Si aún no lo tienes, `uv` puede instalarlo por ti.

### 1) Clonar y preparar el entorno

```sh
git clone https://github.com/catalinagaviriamet-spec/Trabajo-Final-Aprendizaje-Automatico.git
cd Trabajo-Final-Aprendizaje-Automatico
uv sync --locked --python 3.12
```

`uv sync` crea el entorno virtual y instala las dependencias del archivo `uv.lock`.
No necesitas activar el entorno manualmente si usas `uv run`.

### 2) Ejecutar la validación de datos

```sh
uv run python -m src.data.dataset
```

Este paso valida el dataset, comprueba el esquema y realiza la verificación inicial del flujo de datos.

### 3) Entrenar el modelo

```sh
uv run python -m src.models.train
```

Este comando ejecuta el pipeline completo de entrenamiento, compara modelos y guarda los resultados locales y en MLflow.

### 4) Abrir los notebooks

```sh
uv run jupyter lab
```

Abre los notebooks en este orden:

1. `01_eda.ipynb`
2. `02_baseline.ipynb`
3. `03_experiments.ipynb`

En Jupyter, selecciona el kernel de Python 3 del entorno del proyecto.

### 5) Ver resultados

Los archivos de resultados ya incluidos en el repositorio se pueden consultar sin entrenar nuevamente. Si deseas repetir la experimentación, vuelve a ejecutar el entrenamiento.

## Comandos útiles

Con el proyecto ya configurado, puedes usar estas opciones:

```sh
make install
make train
make test
make lint
make mlflow
```

- `make install`: instala dependencias
- `make train`: ejecuta el entrenamiento
- `make test`: corre las pruebas unitarias
- `make lint`: valida estilo y formato
- `make mlflow`: abre la interfaz de MLflow en http://127.0.0.1:5000

## Notas importantes

- La lectura del dataset usa Internet y no requiere bajar un CSV manualmente.
- La reproducción del experimento con la misma configuración es consistente.
- El modelo ganador se evalúa sobre un conjunto de prueba separado; la validación cruzada se usa para elegir el mejor pipeline.
- Los artefactos de MLflow y los modelos generados quedan en tu entorno local y no se suben a GitHub.

## Arquitectura y uso de MLflow

La arquitectura detallada del proyecto y la guía de interpretación de MLflow se encuentran en [docs/arquitectura_mlflow.md](docs/arquitectura_mlflow.md).

### Alias `champion`

El entrenamiento solo asigna `candidate`. Ejecute `make promote` (o `uv run python -m src.models.gate`) para comprobar y promover el artefacto; Docker ejecuta ambos pasos secuencialmente.

El alias `champion` identifica la versión del modelo registrado que cumple las metas del proyecto. La asignación se hace solo si:

- F1 macro en test >= 0.90
- recall mínimo por clase >= 0.85

Esto permite distinguir claramente entre modelos experimentales y la versión validada oficialmente para este proyecto.

## Resultados y selección

Primer experimento: ganó la regresión logística (C=10), con F1 macro CV de 0.9630.
En test obtuvo **97.5 % de accuracy (390/400)** y **F1 macro de 0.9750**.
Verificación local: 32 pruebas aprobadas y tres notebooks ejecutados sin errores.

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

## Automatizar con Prefect

```sh
uv run python -m src.pipeline check
uv run python -m src.pipeline run
```

El primer comando valida; el segundo entrena y registra el modelo. Los datos se mantienen
en memoria. Consulte la [guía de Prefect](docs/pipeline.md) para abrir el panel y activar
el horario diario de ejemplo a las 08:00 de Colombia. La programación requiere servidor
y ejecutor activos; no queda funcionando automáticamente al clonar el repositorio.

## API y Docker en otro PC

Con Docker Desktop abierto e Internet, desde la raíz ejecute en orden:

```sh
docker compose build
docker compose run --name mobile-prices-training train
docker compose up -d --wait api
```

Abra http://127.0.0.1:8000/docs y pruebe POST /predict con el JSON sintético de
configs/prediction_example.json. No necesita Python, cuenta Kaggle ni contraseñas.
El entrenamiento lee los datos en memoria y guarda el modelo en un volumen Docker.
Consulte la [guía completa](docs/docker.md) para instalación, repetición y diagnóstico.

## Monitoreo

```sh
uv run python -m src.monitoring
```

Con Docker: `docker compose run --rm monitor`, después de construir la imagen.
Abra `docs/results/monitoring/drift.html`: el lote sin alteraciones no genera alertas;
una selección de filas reales con mayor RAM genera alerta en RAM, sin alterar valores.
No son observaciones temporales de producción y no demuestran pérdida de precisión.
Consulte la [explicación, metodología y diseño de monitoreo](docs/monitoreo.md).
Solo se guardan estadísticas agregadas; la API no recolecta automáticamente lotes.

## Calidad

```sh
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

CI ejecuta estas verificaciones en cada push y pull request. El workflow Docker y API
también construye, entrena y prueba HTTP en Linux cuando cambia la implementación.
No requiere credenciales cloud. .pre-commit-config.yaml contiene hooks opcionales que usan
uv; para activarlos instale pre-commit y ejecute pre-commit install.

## Organización del repositorio

| Ruta | Contenido |
|---|---|
| configs/training.json | Fuente fija, checksum, partición, metas y semilla |
| src/data/ | Lectura por URL y contrato de datos |
| src/features/ | Preprocesamiento dentro del pipeline |
| src/models/ | Candidatos, búsqueda, evaluación y tracking |
| src/pipeline/ | Flows y tareas de Prefect; ejecución única y programada |
| configs/pipeline.json | Horario de ejemplo y zona horaria |
| notebooks/ | EDA, baseline y lectura de experimentos |
| tests/unit/ | Contrato, particiones y aislamiento del escalado |
| docs/ | Dataset, plan, cronograma y resultados |
| src/api/ | API FastAPI, salud y predicción de un celular |
| Dockerfile, compose.yaml | Entrenamiento y servicio local en contenedores |
| src/monitoring/ | Reporte de drift y calibración del umbral sin usar test |
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

Ya se incorporó [rubrica-instructor.md](rubrica-instructor.md). El profesor también menciona datasets-curados.md,
mvp-minimo-aprobable.md, peer-review-template.md y starter-template/; esos
materiales aún no fueron adjuntados y sus enlaces relativos en README.profe no funcionan.
