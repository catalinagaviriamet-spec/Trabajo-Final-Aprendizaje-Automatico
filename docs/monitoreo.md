# Monitoreo: explicación y demostración

Entrenar es enseñar al modelo con ejemplos. Monitorear es revisar, después de ponerlo
en uso, si los datos y el servicio siguen comportándose como esperamos.
Un aumento de RAM en los celulares nuevos puede cambiar la distribución de entrada:
eso se llama **data drift**. No demuestra por sí solo que el modelo prediga mal.
Para medir errores necesitamos etiquetas reales, que pueden llegar después.

## Qué está implementado

- Reporte reproducible de drift con comparación sin alteraciones y cambio simulado.
- Comparación de las 20 características, con umbral calibrado y semillas fijas.
- Reportes HTML y JSON con estadísticas agregadas; sin filas originales ni CSV local.
- Ejecución manual con Python o Docker, sin modelo entrenado ni credenciales.
- Pruebas unitarias de distancia, alertas, particiones y reproducibilidad.

El reporte es una demostración por lotes. No recoge automáticamente las solicitudes
de la API, no envía notificaciones y no reentrena el modelo. La tabla de operación
que sigue es el diseño propuesto, no una infraestructura de monitoreo ya desplegada.

## Reproducir y abrir el reporte

Desde la raíz del repositorio:

```sh
uv run python -m src.monitoring
```

O con Docker abierto (no necesita Python ni entrenar primero):

```sh
docker compose build
docker compose run --rm monitor
```

Abra `docs/results/monitoring/drift.html` en su navegador. También se genera
`drift.json`, que facilita verificar los números. Solo se necesita Internet para
leer la fuente pública y, la primera vez, construir la imagen. Los resultados se
guardan en la carpeta del proyecto mediante un volumen de Docker.

## Cómo construimos la demostración

El dataset no contiene fechas ni observaciones posteriores al despliegue. Por tanto,
**ninguno de estos lotes representa producción ni una evolución temporal real**.

De las 1.600 filas del entrenamiento original, una permutación con semilla 2026 separa:

| Subconjunto | Filas | Uso |
|---|---:|---|
| Referencia | 800 | Distribución con la que comparamos |
| Calibración | 400 | Fijar el umbral antes de observar los escenarios |
| Lote de control | 400 | Simular la llegada de otro lote sin cambios deliberados |

Los tres subconjuntos son disjuntos. Las 400 filas del test del modelo no se usan.
No utilizamos price_range ni cambiamos el entrenamiento o sus hiperparámetros.
El segundo escenario copia en memoria el lote de control, suma 1.000 MB a RAM y
multiplica la batería por 1,3, redondeando a entero. Esas son las únicas alteraciones.
No asignamos etiquetas reales a ese lote modificado ni calculamos F1 con etiquetas antiguas.

## Medida y umbral

Para cada característica calculamos D, la mayor distancia absoluta entre sus dos
distribuciones acumuladas empíricas. D está entre 0 y 1: cuanto mayor, más distintas
son las distribuciones. Para binarias equivale a la diferencia absoluta de proporciones.
Usamos la distancia KS, **sin aplicar los p-valores estándar que asumen continuidad**.

Mezclamos referencia y calibración, redistribuimos las filas 199 veces preservando
los tamaños 800/400 y calculamos, en cada permutación, el máximo D entre las 20
características. El percentil 99 de esos máximos, con método `higher`, fija el umbral.
Permutar filas completas conserva las asociaciones entre características durante la
calibración. El lote de control y el simulado no participan en ella.

Esta calibración conjunta considera que observamos 20 variables. Es una aproximación
empírica bajo intercambiabilidad, con pocas permutaciones, no una garantía de 1 % de
falsas alertas en producción. Cambiar tamaños, población o variables exige recalibrar.
La comparación alerta cuando D es estrictamente mayor que el umbral. Se exigen al
menos 200 filas por lote; menos observaciones se rechazan como evidencia insuficiente.

Configuración: `configs/monitoring.json`. Código: `src/monitoring/`.
No se añadieron dependencias: se emplean NumPy y pandas ya incluidos en el proyecto.

## Resultado observado

- Umbral: aproximadamente **0,115**.
- Control sin alteraciones: **ninguna característica con alerta**.
- Simulación: **RAM y battery_power con alerta**.

Estos resultados comprueban la demostración elegida, no sensibilidad o especificidad
generales del detector. Sin alerta no significa que todo sea igual: los cambios en
relaciones entre variables pueden pasar inadvertidos en comparaciones univariadas.
Un cambio de datos tampoco equivale a concept drift (cambio en la relación con la etiqueta).

## Diseño de operación propuesto

Las tres integrantes revisan las alertas conjuntamente. Los umbrales siguientes son
decisiones académicas iniciales, no requisitos numéricos del profesor ni SLAs medidos.

| Señal | Frecuencia y umbral inicial | Acción |
|---|---|---|
| Calidad de cada solicitud | Campos faltantes, extras o fuera del contrato: cualquier caso | La API ya devuelve 422; proponer contador agregado y revisar documentación/origen si supera 5 % de al menos 100 solicitudes en 15 minutos |
| Disponibilidad | Consultar /health cada minuto; 3 fallos consecutivos | Revisar contenedor, modelo y logs; reiniciar solo tras identificar el fallo |
| Latencia | p95 > 1 segundo en 2 ventanas de 5 minutos, cada una con al menos 100 solicitudes | Medir CPU/memoria y carga; investigar antes de ampliar recursos. Meta provisional que debe validarse con prueba de carga |
| Errores del servidor | HTTP 5xx > 1 % en 5 minutos y al menos 100 solicitudes | Revisar logs y disponibilidad del modelo; corregir o volver a una versión estable |
| Drift de entradas | Revisar diariamente al reunir un lote de 400; D > umbral calibrado en cualquier variable | Verificar unidades, fuente y mezcla de gamas; contrastar con el siguiente lote y solicitar etiquetas reales |
| Rendimiento con etiquetas reales | F1 macro < 0,90 o recall de alguna clase < 0,85 en un lote independiente de al menos 400 casos y 50 por clase | Revisar errores y representatividad; comparar un candidato con validación independiente antes de reemplazar el modelo |

Sin etiquetas no informaremos accuracy o F1 de producción. Sin volumen suficiente
indicaremos «datos insuficientes», no «todo correcto». Una alerta crítica de contrato
o disponibilidad se atiende inmediatamente; una alerta de drift requiere investigación.
No se promoverá un modelo automáticamente solo por detectar drift.

Para operar de verdad habría que instrumentar contadores y tiempos, programar las
consultas, disponer de etiquetas y acordar cómo obtener lotes nuevos. Manteniendo la
restricción del profesor, procesaríamos esos lotes en memoria desde una fuente autorizada;
solo conservaríamos métricas agregadas, sin cuerpos de solicitudes ni filas del dataset.

## Guion para explicar entre las tres

«La API predice la gama. El monitoreo revisa si están llegando celulares diferentes
a los de referencia. En el control no hay alertas; al aumentar RAM y batería de forma
simulada, ambas se detectan. Antes de reentrenar investigaríamos la causa y mediríamos
el rendimiento con etiquetas reales. Este reporte es una simulación, no producción».

## Referencias metodológicas

- [Distancia KS y sus supuestos, SciPy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ks_2samp.html).
- [Permutaciones de muestras independientes, SciPy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.permutation_test.html).
- Requisito de reporte y diseño: fase 5 de [README.profe](../README.profe).
