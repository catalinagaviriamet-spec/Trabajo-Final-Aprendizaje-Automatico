# Guion de demostración y evidencias

Duración sugerida: 10 minutos. El equipo puede distribuir las intervenciones sin
atribuir módulos exclusivos a una integrante. Ensayar con Docker abierto y el
modelo entrenado; el arranque completo se explica con sus comandos y registros.

| Tiempo | Acción | Evidencia y explicación |
|---|---|---|
| 0–1 min | Presentar el problema | Clasificar cuatro gamas relativas con 20 especificaciones; no calcular un precio monetario. |
| 1–2 min | Mostrar `configs/training.json` y `data/raw/metadata.json` | URL pública, hash y semilla. El CSV se procesa en memoria y no se publica en el proyecto. |
| 2–4 min | Abrir `docs/results/leaderboard.csv` y `confusion_matrix.png` | Selección por F1 macro de validación cruzada; evaluación posterior en prueba reservada. Explicar aciertos y confusiones entre gamas. |
| 4–5 min | Mostrar los logs del entrenamiento | Prefect coordina tareas, MLflow registra experimentos y el gate comprueba el candidato antes de aprobarlo. |
| 5–7 min | Abrir `/docs` y ejecutar `/predict` | Enviar el ejemplo, cambiar solo RAM y probar una entrada incompleta. Resultado válido 200; entrada incompleta 422. |
| 7–9 min | Abrir `docs/results/monitoring/drift.html` | Control sin alerta y selección de registros con mayor RAM con alerta. Son particiones reales, no vigilancia temporal de producción. |
| 9–10 min | Mostrar `docs/revision-rubrica.md` | Resumir evidencias disponibles y límites. La reproducción en otro PC no garantiza cualquier sistema operativo o condición de red. |

## Preparación

1. Seguir [la guía Docker](docker.md) si es la primera ejecución.
2. Iniciar la API: `docker compose up -d --wait api`.
3. Generar el reporte: `docker compose run --rm monitor`.
4. Comprobar las solicitudes con el [protocolo de PowerShell](prueba-api-powershell.md).
5. Tener los archivos y pestañas abiertos. Si falla algo, usar
   [el diagnóstico](solucion-arranque.md) y explicar el error observado.

## Preguntas que debemos poder responder

**¿Por qué regresión logística?** Obtuvo el mejor F1 macro promedio en la comparación
de validación cruzada realizada. El resultado se limita a este dataset y al espacio
de configuraciones explorado; no significa que siempre sea el mejor algoritmo.

**¿Qué significa accuracy 97,5 %?** En los 400 registros de prueba se clasificaron
correctamente 390. No garantiza ese porcentaje para cualquier celular nuevo.

**¿Por qué F1 macro?** Calcula F1 por clase y promedia dando el mismo peso a cada
gama. Se complementa con recall por clase y matriz de confusión.

**¿Qué diferencia hay entre Docker, Prefect y MLflow?** Docker empaqueta el entorno;
Prefect coordina las tareas; MLflow conserva parámetros, métricas y versiones.

**¿Una alerta de drift significa que el modelo está equivocado?** No. Detecta un
cambio de distribución. Para medir pérdida de calidad hacen falta etiquetas reales.

**¿Por qué no está el CSV?** Es una restricción del proyecto. Una URL pública y una
huella verificada permiten reproducir la lectura sin credenciales de Kaggle.

## Registro de reproducción externa

El equipo informó que Yerlith ejecutó el proyecto en su PC correctamente. Esta
declaración no sustituye capturas o registros técnicos. Para la entrega, adjuntar
si están disponibles fecha, sistema operativo, versiones de Docker, commit probado,
resultado del entrenamiento, respuesta de la API y reporte de monitoreo. No inventar
los detalles del equipo ni dar por comprobada una versión que no se haya registrado.
