# Protocolo de prueba de la API en PowerShell

Requisito: haber completado el entrenamiento y tener la API encendida con Docker.
Ejecute desde la raíz del proyecto. No necesita Python instalado en Windows.
El ejemplo utilizado es sintético y no contiene registros del dataset.

## 1. Verificar disponibilidad

```powershell
$apiBase = 'http://127.0.0.1:8000'
Invoke-RestMethod "$apiBase/health"
```

Resultado esperado: `status` igual a `ok`, `model_loaded` igual a `True` y la versión
del modelo aprobado. El número de versión puede variar entre instalaciones.
Si configuró otro puerto, cambie únicamente `$apiBase`.

## 2. Enviar las 20 especificaciones

```powershell
$phoneExample = Get-Content -Raw ./configs/prediction_example.json | ConvertFrom-Json
$originalPrediction = Invoke-RestMethod -Method Post -Uri "$apiBase/predict" -ContentType 'application/json' -Body ($phoneExample | ConvertTo-Json)
$originalPrediction
```

Debe devolver `price_range` entre 0 y 3 y una etiqueta: precio bajo, medio, alto o
muy alto. No devuelve un valor en pesos ni una probabilidad de acierto.

## 3. Cambiar una sola característica

```powershell
$phoneExample.ram = 1000
$modifiedPrediction = Invoke-RestMethod -Method Post -Uri "$apiBase/predict" -ContentType 'application/json' -Body ($phoneExample | ConvertTo-Json)
$modifiedPrediction
```

La RAM se expresa en MB. Las demás variables permanecen iguales y el archivo
original no se modifica. Registre ambos resultados; no exija que cambie la categoría:
el modelo considera todas las especificaciones y un cambio puede quedar dentro de
la misma gama. Este ejercicio tampoco demuestra una relación causal.

## 4. Comprobar rechazo de una entrada incompleta

```powershell
try {
    Invoke-RestMethod -Method Post -Uri "$apiBase/predict" -ContentType 'application/json' -Body '{}' -ErrorAction Stop
    throw 'Fallo de la prueba: la API aceptó una entrada incompleta.'
} catch {
    if ($null -eq $_.Exception.Response) { throw }
    $httpStatus = [int]$_.Exception.Response.StatusCode
    if ($httpStatus -ne 422) { throw }
    Write-Output 'Correcto: la API rechazó la entrada incompleta con HTTP 422.'
}
```

Solo HTTP 422 cuenta como resultado esperado. Un error de conexión o HTTP 503
requiere diagnóstico; no debe presentarse como una validación exitosa.

## Registro de la prueba

Anote equipo, fecha, versión reportada, respuesta original, respuesta con RAM 1000
y rechazo 422. Estas comprobaciones verifican disponibilidad y contrato de la API;
la calidad predictiva se evalúa por separado con el conjunto de prueba reservado.

Puede realizar las mismas solicitudes visualmente en <http://127.0.0.1:8000/docs>.
