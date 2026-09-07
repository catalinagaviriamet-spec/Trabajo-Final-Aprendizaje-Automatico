# Plan del proyecto

## Problema de negocio

Una fábrica hipotética necesita apoyar la asignación de una gama de precio a un celular
a partir de sus especificaciones. El resultado es una sugerencia de categoría para revisión
humana. El conjunto de datos no contiene importes monetarios, márgenes, demanda ni costos:
el modelo no calcula un precio de venta ni demuestra rentabilidad.

Clases: 0 = bajo, 1 = medio, 2 = alto, 3 = muy alto. Los nombres comerciales
«entrada», «media-baja», «media-alta» y «premium» son interpretaciones del equipo;
no corresponden a umbrales monetarios comprobados ni a gamas actuales del mercado.

## Integrantes

- [Carolina Tirado Osorio](https://github.com/Caro-Tirado).
- [Yerlith Zabala](https://github.com/Yerlith).
- [Ana Catalina Gaviria](https://github.com/catalinagaviriamet-spec).

Las tres integrantes participan conjuntamente en el diseño y las decisiones del proyecto.
El grupo discute el problema, los datos y la metodología, y comparte la responsabilidad
de comprender el flujo completo. El desarrollo y la revisión de las fases pendientes
se harán en conjunto. Cada integrante debe aportar commits propios, según el profesor.
Entrega: sábado 12 de septiembre de 2026. Cronograma intensivo propuesto del 6 al 12.
La fecha está confirmada por el equipo. El cronograma describe actividades previstas;
no acredita por sí mismo su ejecución. Véase la [guía de colaboración](colaboracion.md).

| Día | Entregable | Responsables | Revisión |
|---|---|---|---|
| Domingo 6 | Revisar problema, diccionario, EDA y baseline preparados | Las tres integrantes | Revisión conjunta |
| Lunes 7 | Revisar experimentos, resultados, MLflow y modelo registrado | Las tres integrantes | Revisión conjunta |
| Martes 8 | Revisar y demostrar el flow Prefect y su programación ya implementados | Las tres integrantes | Revisión conjunta |
| Miércoles 9 | Revisar y demostrar API FastAPI, validación y Docker implementados | Las tres integrantes | Revisión conjunta |
| Jueves 10 | Revisar reporte de drift de particiones reales y diseño de monitoreo implementados | Las tres integrantes | Revisión conjunta |
| Viernes 11 | Reproducción desde cero, pruebas y ensayo de demostración | Las tres integrantes | Revisión conjunta |
| Sábado 12 | Verificación final y entrega; sin nuevas funcionalidades | Las tres integrantes | Revisión conjunta |

Prioridad: despliegue local completo, no cloud. Si hay retrasos, omitir nube,
reentrenamiento automático y optimizaciones opcionales. Mantener tracking, orquestación,
despliegue local, reporte de drift, pruebas y documentación solicitados por el profesor.

## Métricas y criterio de éxito propuesto

- Principal: F1 macro, que da el mismo peso a cada clase.
- Meta académica inicial: F1 macro de test >= 0.90 y recall de cada clase >= 0.85.
- Complementarias: accuracy, matriz de confusión, MAE entre códigos de gama,
  kappa cuadrático y proporción de errores de dos o más gamas.
- MAE de códigos no significa error en pesos. Los intervalos de precio no están disponibles.
- Estas metas son propuestas del equipo, no requisitos numéricos del profesor.

## Evaluación sin fuga de información

Se fija una partición estratificada 80/20 con semilla 42: 1.600 filas de entrenamiento
y 400 de test. La exploración de relaciones con el objetivo usa solo entrenamiento.
Se prueban 12 configuraciones en 5 folds estratificados del entrenamiento, con las
mismas particiones para todos los candidatos. Escalado dentro del pipeline.
La combinación con mayor F1 macro medio gana. El test se consulta después de seleccionar.
El promedio CV del ganador puede ser optimista por la selección; el test es la
evaluación final. No se reajusta el modelo en función de sus errores de test.

## Modelos sugeridos e implementados

| Modelo | Motivo | Búsqueda |
|---|---|---|
| DummyClassifier | Referencia que ignora las especificaciones | Clase más frecuente |
| Regresión logística | Clasificación multiclase simple y reproducible | C: 0.1, 1, 10 |
| SVM RBF | Alternativa con fronteras no lineales | C: 1, 10; gamma: scale |
| Random Forest | Recomendado por el profesor; combina árboles | Profundidad libre o 12 |
| XGBoost | Recomendado por el profesor; árboles secuenciales | Profundidad 3/5; tasa 0.05/0.1 |

Todos usan las 20 variables. No se seleccionan características mirando test.
La correlación de RAM es una asociación, no un efecto causal ni prueba de que otras
características aumenten directamente los costos. La importancia predictiva se puede
investigar después con permutación en validación, sin reutilizar el test para decisiones.

## Alcance y siguientes fases

Esta entrega implementa la lectura remota sin persistir datos, EDA, comparación de modelos, tracking,
registro con alias champion condicionado a las metas, pruebas y CI. También se implementó
el [pipeline de Prefect](pipeline.md), con programación local configurable y sin persistir el dataset.

También están implementados API FastAPI con validación, Docker y el reporte de drift
simulado. Pendientes de cierre: revisión conjunta de documentación, rúbrica,
contribuciones individuales y ensayo de la demostración completa. Nube opcional.
No se han contratado recursos cloud.

## Diseño de monitoreo

El diseño completo con umbrales, frecuencias, acciones y límites de la demostración
está en [monitoreo.md](monitoreo.md). El reporte usa referencia de entrenamiento y
un lote de registros reales seleccionados, sin consultar el test ni conservar datos originales. El umbral
calibrado es aproximadamente 0,115; la selección con mayor RAM alerta por RAM, sin modificar los valores.
La operación continua y la evaluación con etiquetas nuevas se describen como diseño
propuesto; no se afirma que haya drift real o pérdida de rendimiento en producción.

## Fuentes técnicas

- [Evaluación y pipelines en scikit-learn](https://scikit-learn.org/stable/modules/cross_validation.html)
- [Tracking MLflow](https://mlflow.org/docs/latest/ml/tracking/quickstart/)
- [API de XGBoost](https://xgboost.readthedocs.io/en/stable/python/python_api.html)
- [Instrucciones del profesor](../README.profe)
