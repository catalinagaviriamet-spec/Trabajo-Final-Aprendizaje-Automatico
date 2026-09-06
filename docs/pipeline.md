# Pipeline de entrenamiento con Prefect

## Para qué sirve

Prefect organiza los pasos, registra si completaron o fallaron y permite programar
ejecuciones. MLflow conserva los parámetros, métricas y versiones del modelo.
Las tres integrantes comparten el diseño y la revisión de este flujo.

```text
mobile-prices-pipeline
  preparar-datos
    leer-url-en-memoria → validar-datos
  entrenar-evaluar-registrar → resumen de ejecución
```

La URL pública está fijada a una versión del CSV con SHA-256. Se lee en memoria
sin cuentas, contraseñas ni archivos de datos locales. Un fallo de conexión se
reintenta hasta dos veces, con cinco segundos entre intentos. Un cambio de checksum
o un error de esquema detiene el flujo. El entrenamiento no se reintenta automáticamente
para evitar duplicar versiones en MLflow tras un fallo parcial.

El entrenamiento reutiliza el código del primer experimento. Las particiones y el
escalado se hacen como antes: test reservado y StandardScaler dentro de cada fold.
No se vuelve a leer la URL después de validar. No se han añadido variables derivadas.

## Ejecutar una vez

Desde la raíz del repositorio:

```sh
uv sync --locked --python 3.12
uv run python -m src.pipeline check
uv run python -m src.pipeline run
```

`check` solo lee y valida, sin entrenar. `run` ejecuta todo. Ambos levantan un servidor
temporal local de Prefect y lo apagan al terminar. No requieren cuenta Prefect Cloud.
La primera ejecución puede tardar mientras se inicializa el servidor.

En la terminal deben aparecer las tareas en estado `Completed`. El resumen agregado
queda en `logs/pipeline_last_run.json`. Se mantienen los resultados habituales en
`docs/results/`, el modelo local en `models/best_model.joblib` y el registro MLflow.

Cada ejecución completa crea nuevas ejecuciones y una versión de modelo en MLflow;
reemplaza los reportes locales. Con la misma fuente y configuración es una reproducción
del experimento, no evidencia de rendimiento sobre datos nuevos. No se reajustan
parámetros a partir de los errores del test ya observado.

## Ver el panel y activar la programación

La configuración de ejemplo en `configs/pipeline.json` indica **todos los días a las
08:00, zona America/Bogota**. Es una propuesta didáctica editable, no una exigencia del
profesor. No se mantiene activa automáticamente al clonar el repositorio.

Abra una primera terminal desde la raíz:

```sh
uv run python -m src.pipeline server
```

Espere a que el servidor indique que está listo y abra http://127.0.0.1:4200.
En una segunda terminal:

```sh
uv run python -m src.pipeline serve
```

Este comando registra `mobile-prices-pipeline/entrenamiento-local` y queda escuchando
ejecuciones programadas o iniciadas desde el panel. Limita el ejecutor a un flujo a la
vez. No lance además entrenamientos manuales simultáneos porque comparten los reportes
y artefactos locales.

Para ejecutar inmediatamente y ver el resultado en ese mismo panel, puede usar una
tercera terminal (cuando no haya otro entrenamiento en curso):

```sh
uv run python -m src.pipeline run --api-url http://127.0.0.1:4200/api
```

Para detener la programación, pulse **Ctrl+C en la terminal de serve**; Prefect pausa
el horario al cerrar normalmente. Luego detenga el servidor con Ctrl+C. Si el equipo
se apaga abruptamente, revise y pause el deployment al volver a abrir el panel.
El computador debe estar encendido, con Internet y ambos procesos activos para que
el horario se ejecute. Este mecanismo no enciende un equipo apagado.

## Qué se guarda y qué no

- Se guardan estados, logs y metadatos de Prefect en `logs/prefect/`, ignorados por Git.
- El lector, las tareas y los flows declaran `persist_result=False`; las tareas también
  usan `NO_CACHE`. No se serializan sus DataFrames como resultados de Prefect.
- Los únicos parámetros del flow son opciones de ejecución; no recibe filas del dataset
  como parámetros. Los logs muestran conteos y métricas, no registros individuales.
- La carpeta `data/` conserva únicamente `.gitkeep`.
- Los modelos son artefactos derivados locales y no se publican en GitHub.

## Verificación

Pruebas unitarias: reintentos solo para errores transitorios, interrupción antes del
entrenamiento si falla validación, paso del mismo objeto en memoria y persistencia
desactivada. La suite completa tiene 18 pruebas.

La [evidencia de integración](results/pipeline_verification.json) registra el flujo,
estados de las tareas, métricas reproducidas, ausencia de CSV local y horario aceptado
por un servidor de prueba. El deployment de verificación se registra **pausado** y ese
servidor se apaga al terminar; no demuestra una ejecución diaria desatendida.

Para repetir esa verificación con entrenamiento real:

```sh
uv run python -m scripts.verify_pipeline
```

En la verificación en Windows, Prefect 3.8.5 emitió al salir un aviso de limpieza
de su SQLite temporal porque el archivo seguía en uso. Las tareas, la consulta de sus
estados y el registro del horario finalizaron correctamente antes de ese aviso. Ese
archivo contiene metadatos de la prueba, no el CSV. La ejecución normal `check` también
se comprobó y cerró su servidor sin errores de eventos.

Referencias oficiales: [ejecución local](https://docs.prefect.io/v3/how-to-guides/deployment_infra/run-flows-in-local-processes),
[horarios](https://docs.prefect.io/v3/how-to-guides/deployments/create-schedules) y
[persistencia de resultados](https://docs.prefect.io/v3/how-to-guides/workflows/cache-workflow-steps).
