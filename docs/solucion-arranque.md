# Diagnóstico del arranque local

Esta guía complementa [la instalación con Docker](docker.md). Ejecute los comandos
desde la carpeta que contiene `compose.yaml`, con Docker Desktop abierto.
Continúe solo cuando el paso anterior termine correctamente.

| Síntoma | Comprobación | Acción |
|---|---|---|
| `docker` no se reconoce | Ejecutar `docker version` | Instalar Docker Desktop y abrir una nueva terminal para actualizar PATH. |
| No se puede conectar al motor | `docker version` muestra cliente pero falla el servidor | Abrir Docker Desktop, esperar a que el motor esté listo y usar contenedores Linux. |
| No encuentra el archivo de configuración | Buscar `compose.yaml` en la carpeta actual | Abrir PowerShell desde esa carpeta; no desde la carpeta superior del ZIP. |
| Falla la descarga de dependencias o del dataset | Leer el primer error de conexión | Comprobar Internet y repetir el paso fallido. No desactivar la comprobación del hash del dataset. |
| Nombre de entrenamiento ocupado | Consultar `docker logs mobile-prices-training` | Conservar la evidencia anterior y utilizar un nombre nuevo al repetir el entrenamiento. |
| Puerto 8000 ocupado | La creación de la API informa un conflicto de puerto | Detener el servicio propio que lo utiliza o cambiar solo el puerto del host como se explica abajo. |
| `/health` devuelve 503 | Revisar `docker compose logs api` y los logs del entrenamiento | Completar el entrenamiento y su aprobación, luego recrear la API. |

## Repetir un entrenamiento conservando el anterior

```powershell
docker compose stop api
docker compose run --name mobile-prices-training-2 train
```

Tras comprobar `"approved": true` y `"metric_reproduced": true`:

```powershell
docker compose up -d --wait --force-recreate api
```

Utilice un nombre distinto en cada repetición. No lance dos entrenamientos sobre
el mismo volumen simultáneamente. La API carga el modelo al arrancar: recrearla
garantiza que use la exportación recién aprobada.

## Usar otro puerto local

En `compose.yaml`, cambie `127.0.0.1:8000:8000` por `127.0.0.1:8001:8000`.
Después ejecute `docker compose up -d --wait api` y abra
<http://127.0.0.1:8001/docs>. El puerto interno del contenedor continúa siendo 8000.

## Evidencia para pedir ayuda

```powershell
docker compose ps -a
docker compose logs --tail 60 api
docker logs --tail 60 mobile-prices-training
```

Comparta el comando que falló y su error completo. Si cambió el nombre del
contenedor de entrenamiento, úselo también al consultar sus logs.
No elimine volúmenes para diagnosticar: contienen el modelo aprobado.
