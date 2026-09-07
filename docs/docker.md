# Ejecución local con Docker

El profesor puede reproducir el proyecto en su PC. Necesita Docker Engine con Compose
o Docker Desktop abierto, Internet y espacio para descargar la imagen y dependencias.
No necesita Python, uv, cuenta Kaggle, claves ni instalar los paquetes por separado.
Git facilita clonar; también puede obtener el ZIP público del repositorio.
La primera construcción puede tardar varios minutos y ocupar varios GB.
En Linux x86_64 se instala XGBoost 3.4.1 para CPU para evitar descargar componentes
NVIDIA innecesarios. En otras plataformas se conserva la distribución general.

En Windows use Docker Desktop con contenedores Linux y WSL 2, siguiendo la
[instalación oficial](https://docs.docker.com/desktop/setup/install/windows-install/).
Tras instalar y abrir Docker Desktop, compruebe en una terminal:

```sh
docker version
docker compose version
```

Desde la carpeta del repositorio, ejecute en este orden; continúe solo si el paso anterior termina correctamente:

```sh
docker compose build
docker compose run --name mobile-prices-training train
docker compose up -d --wait api
```

El entrenamiento ejecuta Prefect, lee la URL pública en memoria, valida el checksum,
compara los modelos y guarda el pipeline ganador en un volumen Docker. El CSV no se
guarda ni se incluye en la imagen. El modelo se genera en el mismo entorno que lo sirve.
El contenedor de entrenamiento queda detenido para conservar MLflow, logs y reportes.
Puede consultar su salida con `docker logs mobile-prices-training` y copiar los reportes:

```sh
docker cp mobile-prices-training:/app/docs/results ./resultados-docker
```

Abra [la documentación interactiva](http://127.0.0.1:8000/docs).
Seleccione **POST /predict → Try it out** y pulse **Execute**. El formulario ya incluye
el contenido de `configs/prediction_example.json`. Es un ejemplo sintético,
no una fila copiada del dataset. La respuesta contiene `price_range` y su etiqueta.
Las unidades están en `docs/dataset.md`. El servicio valida los 20 campos, rechaza
campos extra y valores inválidos con HTTP 422. Sin modelo devuelve HTTP 503.
La predicción es una gama relativa, no un precio en pesos ni garantía comercial.

Para detener la API sin borrar el modelo:

```sh
docker compose stop api
```

Para reabrirla: `docker compose up -d --wait api`. No vuelve a entrenar ni leer datos.
Para repetir el entrenamiento con nombre nuevo y conservar la evidencia anterior:

```sh
docker compose stop api
docker compose run --name mobile-prices-training-2 train
docker compose up -d --wait api
```

Use otro nombre en cada repetición. No ejecute entrenamientos simultáneos sobre el mismo
volumen. `docker compose down` conserva el modelo; agregar `--volumes` lo elimina.
El puerto se publica solo en el equipo local. Si 8000 está ocupado, cambie el primer
8000 en `compose.yaml` y abra la URL con ese puerto.

## Prueba alternativa con Python

Para generar el reporte de monitoreo con la misma imagen ejecute
`docker compose run --rm monitor`. Abra `docs/results/monitoring/drift.html`.
La [guía de monitoreo](monitoreo.md) explica la simulación y el diseño propuesto.

Si ya entrenó con uv, puede probar la misma API sin contenedor:

```sh
uv run uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```

En otra terminal: `uv run python -m scripts.verify_api`.
Las pruebas unitarias usan datos sintéticos. El workflow Docker verifica además
construcción, entrenamiento desde URL y respuestas HTTP en Linux.
