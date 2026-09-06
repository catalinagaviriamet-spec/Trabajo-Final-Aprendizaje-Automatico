# Proyecto final — Aprendizaje automático en la nube

Especialización en Ciencia de Datos e IA — Universidad de Medellín.

## Estado actual

Estructura inicial creada siguiendo el documento del profesor, conservado íntegramente en [README.profe](README.profe). El problema, el dataset, los integrantes y las herramientas están pendientes de definición. Todavía no hay modelos, API ni pipelines implementados.

El directorio proyecto-mlops/ del ejemplo del profesor corresponde a la raíz de este repositorio.

## Estructura y propósito

| Ruta | Propósito |
|---|---|
| README.profe | Instrucciones originales del profesor; referencia para todo el proyecto. |
| pyproject.toml | Configuración del proyecto Python; dependencias pendientes. |
| .pre-commit-config.yaml | Plantilla para verificaciones antes de los commits. |
| .github/workflows/ci.yml | Plantilla de integración continua. |
| .github/workflows/deploy.yml | Plantilla de despliegue. |
| src/data/ | Carga, limpieza y validación de datos. |
| src/features/ | Construcción de variables para el modelo. |
| src/models/ | Entrenamiento y evaluación. |
| src/api/ | Servicio de predicción, si se elige una API. |
| src/monitoring/ | Monitoreo y detección de cambios en los datos. |
| notebooks/01_eda.ipynb | Exploración de los datos. |
| notebooks/02_baseline.ipynb | Primer modelo de referencia. |
| notebooks/03_experiments.ipynb | Comparación de experimentos. |
| tests/unit/ | Pruebas unitarias. |
| configs/ | Configuración de los procesos. |
| data/ | Datos locales. |
| models/ | Modelos guardados localmente. |
| logs/ | Registros locales de ejecución. |
| docs/ | Decisiones, planificación y guías. |

Los archivos .gitkeep permiten guardar carpetas vacías en Git. Los workflows solo se ejecutan manualmente y únicamente indican que la implementación está pendiente.

## Desarrollo por etapas

1. Planificación: definir problema, dataset, métricas, alcance, integrantes y cronograma con responsables.
2. Exploración de datos y modelo de referencia.
3. Tracking de experimentos y registro de modelos.
4. Pipeline de entrenamiento.
5. Despliegue.
6. Monitoreo, pruebas y documentación.

Cada integrante debe aportar commits propios, según las instrucciones del profesor. El despliegue en la nube es deseable, pero el profesor también acepta un despliegue local bien realizado.

## Material del curso pendiente

El documento original enlaza archivos que no se recibieron: datasets-curados.md, rubrica-instructor.md, mvp-minimo-aprobable.md, peer-review-template.md y starter-template/. Sus enlaces relativos en README.profe no funcionarán hasta disponer de ese material.

## Ejecución

Esta entrega contiene únicamente la estructura. Las instrucciones de instalación, entrenamiento y ejecución se agregarán cuando se implementen esas fases.