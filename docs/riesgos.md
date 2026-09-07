# Riesgos y respuesta

Responsables de revisión: las tres integrantes. Son riesgos del prototipo, no incidentes observados.

| Riesgo | Detección | Acción |
|---|---|---|
| Fuente remota caída o modificada | Smoke, fallo de conexión o SHA-256 | Revisar proveedor; no ignorar checksum ni reemplazar fuente silenciosamente |
| Unidades equivocadas o valores inválidos | Contrato y 422 en la API | Rechazar y corregir el origen; documentar MB/mAh/GB |
| Celulares distintos a los de entrenamiento | Distancia de distribución y revisión de cobertura | Investigar y obtener etiquetas antes de reentrenar |
| Sobreajuste al test o fuga entre particiones | Índices fijos, tests y revisión del protocolo | No afinar con test; crear evaluación nueva al cambiar protocolo |
| Modelo no representativo del mercado actual | Dataset sin fecha/fabricante; validación externa ausente | Limitar a demostración académica; no fijar precios comerciales |
| Modelo desplegado sin validación | Gate separado y metadatos de versión | Rechazar candidato y conservar campeón; revisar antes de promover |
| Pérdida del volumen Docker o del registry | /health y disponibilidad de artefactos | Reconstruir entrenamiento; conservar copia autorizada de métricas/configuración |

Las alertas se dirigen al equipo con la acción indicada. No hay notificaciones
automáticas ni Prometheus desplegado en esta versión; el diseño completo de señales
y destinatarios se explica en monitoreo.md.
