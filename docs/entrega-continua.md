# Entrega continua para ejecución local

`cd.yml` entrega un paquete con la imagen Docker preparada. Es entrega continua:
automatiza el empaquetado después de las pruebas; no instala un servidor en la nube
ni mantiene una API pública encendida. El despliegue en el PC sigue siendo manual.

## Cuándo se ejecuta

Después de un push a `main`, espera a que `Calidad y pruebas` termine correctamente.
Construye exactamente el commit que pasó esas pruebas y comprueba que la imagen
puede importar la API y contiene la ruta `/predict`. Si CI falla, no genera entrega.
Los pull requests no publican paquetes mediante este workflow.

La prueba completa de entrenamiento y API continúa en `docker.yml`. La comprobación
breve de CD no sustituye esa integración ni demuestra calidad predictiva.
No se configura una ejecución nocturna.

## Descargar

1. En GitHub, abrir **Actions → Entrega continua local**.
2. Abrir una ejecución exitosa y buscar **Artifacts** al final.
3. Descargar `entrega-local-...` y extraer el ZIP en una carpeta nueva.

GitHub requiere iniciar sesión para descargar estos artefactos. No se necesitan
tokens, claves de Kaggle ni credenciales dentro de los comandos del proyecto.
Si el profesor prefiere no iniciar sesión, puede seguir la instalación pública desde
el ZIP del repositorio y `docker compose build`, documentada en `docs/docker.md`.
Referencia: https://docs.github.com/en/actions/how-tos/manage-workflow-runs/download-workflow-artifacts

El paquete se conserva siete días; no es un enlace permanente de distribución.
Una nueva actualización de `main` que pase CI genera otra entrega. También se puede
volver a ejecutar el workflow desde Actions. No es necesario modificar archivos
solo para renovar el paquete.

## Contenido del paquete

- `mobile-prices.tar.gz`: imagen Linux x86_64 con Python, dependencias, código y configuración.
- `compose.yaml`: servicios de entrenamiento, API y monitoreo.
- `COMMIT.txt`: versión exacta del código utilizado.
- `SHA256SUMS.txt`: huella del archivo de imagen para verificar su integridad.
- `INSTRUCCIONES.md`: esta guía.

No incluye dataset, modelo entrenado, credenciales ni registros del entrenamiento.
La imagen puede ocupar varios GB al cargarse. Está orientada a Windows con Docker
Desktop y contenedores Linux en equipos x86_64; otras arquitecturas no se verifican
con este workflow.

## Ejecutar en PowerShell

Abrir Docker Desktop y PowerShell dentro de la carpeta extraída. Opcionalmente,
comparar el resultado siguiente con el hash de `SHA256SUMS.txt`:

```powershell
Get-FileHash ./mobile-prices.tar.gz -Algorithm SHA256
```

Cargar la imagen ya construida:

```powershell
docker load --input mobile-prices.tar.gz
```

Entrenar en ese equipo; requiere Internet para consultar los datos en memoria:

```powershell
docker compose run --no-build --name mobile-prices-training-entrega train
```

Continuar solo si termina correctamente y muestra `"approved": true`:

```powershell
docker compose up -d --wait --no-build api
```

Abrir http://127.0.0.1:8000/docs y probar **POST /predict → Try it out → Execute**.
Si ya existe un contenedor con ese nombre, usar un nombre nuevo para el entrenamiento.
Si hay otra API del proyecto encendida en el puerto 8000, detenerla desde su carpeta
original antes de iniciar esta copia. No entrenar simultáneamente en el mismo volumen.

Para generar el reporte visible en `docs/results/monitoring/drift.html`:

```powershell
docker compose run --rm --no-build monitor
```

Para detener la API conservando el modelo:

```powershell
docker compose stop api
```
