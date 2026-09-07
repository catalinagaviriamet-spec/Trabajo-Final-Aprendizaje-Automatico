# Ficha del dataset

El [diccionario completo](dataset.md) contiene procedencia, las unidades de las 21
columnas y decisiones sobre ceros. [metadata.json](../data/raw/metadata.json) conserva
la URL fijada y el hash, sin almacenar el CSV. El contrato se ejecuta en
`src/data/dataset.py`, antes del split, y se prueba en `tests/unit/test_data.py`.

## Población, licencia y límites

2.000 registros de especificaciones de celulares, equilibrados por cuatro gamas.
No se conoce el procedimiento de muestreo, fechas, países ni fabricantes; no se
afirma que representen la oferta de celulares actuales. El balance artificial entre
clases puede diferir del de una fábrica. La licencia indicada por la ficha consultada
es desconocida; no se redistribuye el dataset ni se afirma autorización comercial.

## Nulos y calidad

En cada una de las 21 columnas se observaron cero nulos en la versión fijada por hash.
Por eso no se imputa ningún campo: si aparecen nulos nuevos, el contrato rechaza el
lote. No conocemos un mecanismo de ausencia documentado por el autor. Los ceros en
px_height y sc_w son valores cuestionables, no NaN: se conservan y se explican en EDA.

## Tres fuentes de fuga de información

1. **Objetivo:** price_range se elimina de X; no se crean características con etiquetas
   ni predicciones construidas a partir del test.
2. **Entre particiones/preprocesamiento:** filas duplicadas se rechazan antes del split;
   los índices quedan fijos y disjuntos. El escalador se ajusta dentro de cada fold.
3. **Temporal:** no existe eje temporal; se usa split estratificado aleatorio explícito,
   sin interpretar el resultado como pronóstico futuro. Si llegan datos con fechas,
   habrá que crear un protocolo temporal nuevo, no mezclar pasado y futuro.

La selección usa exclusivamente CV de entrenamiento. Reejecutar el test reservado
para comprobar reproducibilidad no crea evidencia independiente y no autoriza
ajustar hiperparámetros en función de sus errores. Monitoreo usa solo entrenamiento.
