# Contraste con la rúbrica recibida

Referencia preservada: [rubrica-instructor.md](../rubrica-instructor.md).
Este documento es una revisión del equipo, no una calificación otorgada por el profesor.
Las anclas 1/3/5 representan niveles de evidencia; tener la funcionalidad no implica 5.

| Dimensión | Evidencia disponible y ajustes | Límites frente al nivel 5 |
|---|---|---|
| Reproducibilidad | Lockfile, .python-version, make setup/smoke/train, diagnóstico real y tolerancia 0,005 documentada | Verificar también recorrido por una integrante en otro equipo |
| Datos | Contrato, fixtures rechazados, diccionario, dataset-card y metadata.json con hash sin datos | No hay contratos distintos crudo/procesado ni relación entre columnas validada; no afirmar nivel 5 |
| Tracking/registry | Experimentos, alias candidate/champion, signature, ejemplo sintético, gate que carga por alias y ficha generada | Hay 12 configuraciones en 5 runs de algoritmos; no 20 trials anidados ni estudio demográfico |
| Pipeline | Prefect, tareas, reintentos 5/10 segundos, reporte adjunto al candidato, promoción separada | No caching cronometrado; se evita persistir datos por instrucción del equipo/profesor |
| Deployment | Docker y API probados, validación, tests HTTP, versión en /health | Contenedor aún root; API carga exportación aprobada, no registry directo; no pipeline de tipos |
| Monitoreo | HTML de particiones reales, umbral calibrado, códigos 0/2, artifact, política y riesgos | Sin Prometheus ni dashboard JSON desplegado; no vigilancia automática de producción |
| Ingeniería/documentación | Ruff, tests, control de outputs en CI/pre-commit, fichas y ADR | Sin mypy, gitleaks ni nbstripout instalado; la limpieza usa script propio. No afirmar auditoría completa del historial |

## Penalizaciones atendidas

- Notebooks de entrega sin outputs ni execution_count; CI falla si reaparecen.
- El entrenamiento ya no modifica champion: promoción separada con controles y rechazo probado.
- El reporte principal compara registros reales, sin sumar RAM ni fabricar valores.
- No se añade dataset, modelo ni base de datos a Git; metadata.json contiene solo metadatos.

Las salidas ya publicadas en commits históricos no se reescriben; la versión de entrega
queda limpia. No se altera la autoría histórica. La revisión de secretos en todo el
historial con gitleaks sigue pendiente; no se afirma que esa auditoría esté hecha.

## Autoría de los ajustes

Los ajustes se trabajan conjuntamente en el mismo computador con Carolina, según
lo comunicado por el equipo, y se registran con coautoría de Carolina Tirado Osorio.
El tráiler Co-authored-by no requiere compartir contraseñas. GitHub lo vincula a su
cuenta si el correo está asociado; confirmar la interpretación de «commits propios»
con el profesor si exige además commits con ella como autora principal.
