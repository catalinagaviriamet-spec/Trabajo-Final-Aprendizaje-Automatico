# ADR 001 — despliegue local y datos exclusivamente en memoria

## Contexto

El equipo está aprendiendo MLOps; el profesor permite despliegue local y prohíbe
almacenar el dataset en el proyecto. La rúbrica premia evidencias, no herramientas.

## Decisión

Usar Docker, MLflow y Prefect locales, fuente pública fijada por hash, gate separado
y reportes agregados. No persistir resultados que contengan dataframes en Prefect.

## Alternativas

Cloud administrada exigiría cuentas y operación adicional. Cachear lotes en disco
aceleraría repeticiones pero incumpliría la restricción explícita sobre datos.

## Consecuencias

La reproducción no requiere contraseñas ni CSV manual. La primera construcción requiere
Internet. No reclamamos caching medido de datos ni monitoreo continuo de producción.
El artefacto aprobado se exporta para la API local; integrar directamente el registry
con el servicio queda fuera de este ajuste acotado.
