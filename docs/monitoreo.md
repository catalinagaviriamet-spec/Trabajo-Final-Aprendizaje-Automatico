# Monitoreo con particiones reales

Monitorear es revisar si cambian los datos o el servicio después de entrenar.
Data drift significa cambio en la distribución de entrada; no demuestra por sí solo
que disminuyó la precisión. Para medir rendimiento hacen falta etiquetas reales.

## Reproducir

```sh
uv run python -m src.monitoring
docker compose run --rm monitor
```

Son alternativas. Con Docker primero construya la imagen. Abra
`docs/results/monitoring/drift.html`; el JSON conserva únicamente estadísticas agregadas.
El flow de entrenamiento también genera el reporte y lo adjunta al run candidato en
MLflow, con un resumen como artifact de Prefect. No se guarda el CSV ni filas originales.

## Particiones y método

De las 1.600 filas de entrenamiento, una permutación fija separa referencia (800),
calibración (400) y control (400), disjuntos. No se consulta el test reservado.
El escenario de selección usa las 200 filas reales con mayor RAM del control.
No modifica ningún valor ni inventa observaciones. Es un cambio de composición
deliberado para demostrar sensibilidad, no una llegada temporal real de celulares.

La distancia D es la máxima diferencia entre distribuciones acumuladas empíricas,
entre 0 y 1. Admite empates; en binarias es diferencia absoluta de proporciones.
Se calcula sobre las 20 variables. No aplicamos p-valores KS que asumen continuidad.

El umbral es el percentil 99 de los máximos D entre variables en 199 permutaciones
de referencia y calibración. Se conserva cada fila completa al permutar. Para la
selección de 200 filas se recalibra usando 200 filas de calibración, manteniendo
los tamaños 800/200; el control usa 800/400. Los lotes comparados no fijan el umbral.
Es una aproximación empírica bajo intercambiabilidad, no garantía de falsas alertas
de 1 % en producción. Nuevos tamaños o poblaciones requieren recalibración.

La alerta exige D > umbral. D expresa magnitud del cambio; un p-valor pequeño por sí
solo no basta: con n grande puede detectar diferencias minúsculas sin relevancia
operativa. La calibración considera las 20 comparaciones conjuntamente. Este detector
univariado puede omitir cambios en relaciones entre variables.

Resultado: control sin alertas; selección real con alerta en RAM. La alerta por
batería del reporte anterior correspondía a valores alterados y se retiró al recibir
la rúbrica. Ahora todas las comparaciones publicadas usan registros originales.

## Check y códigos de salida

```sh
uv run python -m src.monitoring --check control
uv run python -m src.monitoring --check selected
```

El control retorna 0. La selección retorna 2 por drift. Errores de lectura/contrato
fallan con otro código. `scripts/verify_drift_check.py` y el workflow Docker comprueban
esos resultados explícitamente: aceptar el fallo esperado no oculta fallos inesperados.

## Diseño del servicio y acciones

Las tres integrantes son destinatarias de las alertas. Los siguientes umbrales son
metas iniciales académicas, no SLAs medidos ni exigencias numéricas del profesor.

| Señal | Umbral y ventana propuesta | Acción |
|---|---|---|
| Calidad | Cualquier entrada inválida; 422 > 5 % de 100 solicitudes en 15 min | Rechazar entrada y revisar unidades/origen |
| Salud | 3 fallos de /health consecutivos, consultado cada minuto | Revisar contenedor y artefacto aprobado |
| Latencia | p95 > 1 s en 2 ventanas de 5 min con 100 solicitudes cada una | Investigar carga, CPU y memoria |
| Errores | 5xx > 1 % de 100 solicitudes en 5 min | Revisar logs y considerar rollback |
| Drift | Lote diario con tamaño compatible; D > umbral calibrado | Investigar composición y obtener etiquetas |
| Precisión | F1 < 0,90 o recall < 0,85, mínimo 400 etiquetas y 50 por clase | Revisar errores y evaluar un candidato |

Prometheus mediría el **servicio** (solicitudes, errores, duración); el reporte mide
los **datos**. Prometheus y su dashboard no están implementados en esta versión.
La API no acumula automáticamente lotes y no se notifican alertas de forma automática.
Sin etiquetas no se reporta F1 de producción; sin volumen suficiente, «datos insuficientes».

Consulte [la política de reentrenamiento](politica-de-reentrenamiento.md) y
[los riesgos](riesgos.md). No se reentrena ni promueve un modelo por una alerta aislada.

## Fuentes

- [Distancia KS, SciPy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ks_2samp.html).
- [Permutaciones independientes, SciPy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.permutation_test.html).
