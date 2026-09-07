# Política de reentrenamiento y promoción

**Trigger:** una alerta de drift investigada y persistente en un siguiente lote,
o F1 macro < 0,90 / recall de una clase < 0,85 con al menos 400 etiquetas reales y
50 por clase. Fallos de disponibilidad o errores de unidades se corrigen primero;
no se solucionan automáticamente reentrenando. El reporte didáctico no es un trigger real.

**Datos:** lotes autorizados con etiquetas verificadas, contrato e identificación por
hash. Procesamiento en memoria; no se almacenan filas ni en Git ni en artefactos.
Para datos nuevos se define otra evaluación independiente antes de experimentar.

**Aprobación:** Carolina Tirado Osorio, Yerlith Zabala y Ana Catalina Gaviria revisan
conjuntamente las alertas y resultados. Una integrante designada ejecuta el gate y
registra la decisión del equipo; no se sustituyen revisiones humanas por un score.

**Mecanismo actual:** `make train` registra `candidate` con validation_status=pending_gate.
`make promote` carga ese alias, comprueba las metas, el hash y la reproducción de F1
(tolerancia absoluta 0,005), y solo entonces actualiza `champion` y su exportación.
En la demostración Docker los dos comandos se ejecutan secuencialmente para que una
máquina limpia quede preparada. El flow por sí solo nunca promueve modelos.
Los tests prueban que un F1 bajo o un recall insuficiente rechazan el gate.

**Rollback:** antes de aprobar se registra previous_champion en logs/promotion.json.
Ante un problema, la integrante designada devuelve el alias a esa versión con
`MlflowClient.set_registered_model_alias`, carga esa versión, regenera su exportación
y reinicia la API. Se conservarán versiones y evidencias; no se borran artefactos.
Este procedimiento está diseñado, no automatizado ni ensayado como failover.

**Registro:** MLflow conserva versión, parámetros, métricas y validation_status;
logs/promotion.json registra candidato, versión previa, resultado y fecha del gate.
La decisión humana y su motivo se registrarán en una issue/PR del equipo. Un rechazo
no reemplaza champion. Los logs y modelos quedan locales, excluidos de Git.
