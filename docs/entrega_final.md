# Guía de presentación final

## 1. Problema

El proyecto aborda la clasificación de la gama de precio de celulares a partir de 20 especificaciones técnicas. La variable objetivo es `price_range`, con cuatro clases: bajo, medio, alto y muy alto.

## 2. Objetivo

Construir un pipeline reproducible para seleccionar el modelo más adecuado, evaluar su capacidad predictiva y dejar trazabilidad del experimento con MLflow.

## 3. Metodología

- validación del dataset y de la integridad del esquema,
- partición estratificada train/test con semilla fija,
- comparación de modelos con validación cruzada,
- selección por F1 macro promedio,
- evaluación final en test reservado,
- registro del mejor pipeline en MLflow.

## 4. Resultados

El modelo ganador fue la regresión logística. Sus métricas principales fueron:

- Accuracy: 97.5%
- F1 macro: 0.9750
- Recall por clase: 0.98 / 0.96 / 0.98 / 0.98
- Error severo: 0

Esto indica un desempeño muy sólido para una clasificación multiclase con 4 categorías.

## 5. MLflow y trazabilidad

MLflow se usó para rastrear:

- parámetros, hiperparámetros y semilla,
- métricas por modelo,
- artefactos como CSVs y matriz de confusión,
- versión del modelo registrada,
- alias `champion` para la versión validada.

El alias `champion` representa la versión que cumple las metas de calidad del proyecto.

## 6. Conclusiones

El proyecto es reproducible, validado y bien documentado. La regresión logística ofrece un equilibrio entre rendimiento, simplicidad y explicabilidad. La trazabilidad con MLflow refuerza la credibilidad del proceso experimental y deja una base clara para una futura etapa de despliegue.

