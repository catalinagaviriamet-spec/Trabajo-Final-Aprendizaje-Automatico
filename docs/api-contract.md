# Contrato de la API

Implementación: `src/api/main.py`; esquema interactivo: `/docs`; esquema JSON:
`/openapi.json`. `configs/prediction_example.json` es un ejemplo sintético, no una fila
original del dataset. Las unidades de entrada están en [dataset.md](dataset.md).

- `POST /predict`: exactamente los 20 predictores, sin price_range ni claves extra.
  Batería, RAM, peso y px_width positivos; otras magnitudes no negativas; n_cores
  entero entre 1 y 8; conectividad binaria 0/1. No admite infinitos ni valores ausentes.
- Respuesta 200: `price_range` (0–3) y `label`. No devuelve precios monetarios.
- Entrada inválida: 422; modelo ausente: 503 con mensaje de recuperación controlado.
- `GET /health`: estado, modelo cargado y `model_version` cuando hay metadatos del gate.
  Una exportación antigua sin metadatos devuelve versión nula; no se inventa una.
- La API se enlaza solo a 127.0.0.1 en el equipo anfitrión. No almacena solicitudes.

La API carga la exportación local aprobada por el gate. El gate sí carga `candidate`
desde MLflow por alias. La API no está conectada directamente al registry, por lo que
no se afirma cumplir ese punto específico del nivel 5 de Deployment.

## Comprobación desde Windows

El [protocolo de PowerShell](prueba-api-powershell.md) permite probar disponibilidad, predicción y rechazo HTTP 422 sin instalar Python.
