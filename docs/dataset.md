# Dataset y diccionario

Fuente utilizada: [CSV compartido por Yerlith](https://github.com/Yerlith/Aprendizaje-automatico/blob/25f42d01c0f239d5b5daf51cb48b4370404a3ffb/data/mobile_prices.csv).
Commit fijado: `25f42d01c0f239d5b5daf51cb48b4370404a3ffb`.
SHA-256: `f9e8cd3154b8684a1be0ff401b1fba7750710af6bd076a399c6ce7ceb979c624`.

La [ficha de Kaggle de Abhishek Sharma](https://www.kaggle.com/datasets/iabhishekofficial/mobile-price-classification)
describe el problema de clasificación de rangos, no precios exactos. El CSV de trabajo
es el espejo indicado por el equipo; no se verificó identidad binaria con el archivo
de Kaggle. La ficha consultada indica licencia desconocida. Se conserva la atribución
y se distribuye un lector por URL en memoria, sin guardar el CSV en el proyecto.

Auditoría del archivo: 2.000 filas, 21 columnas, 20 predictores numéricos, 500 filas
por clase, cero nulos y cero filas duplicadas. No hay fechas, identificadores de
fabricante, moneda ni precios reales. No permite estimar vigencia comercial actual.

## Diccionario de trabajo

Las unidades corresponden a la descripción habitual de este dataset; el CSV no
incorpora metadatos de unidades. Deben conservarse iguales en entrenamiento e inferencia.

| Campo | Significado / unidad de trabajo |
|---|---|
| battery_power | Capacidad de batería, mAh |
| blue | Bluetooth, 0/1 |
| clock_speed | Frecuencia del procesador, GHz |
| dual_sim | Soporte de dos SIM, 0/1 |
| fc | Cámara frontal, megapíxeles |
| four_g | Soporte 4G, 0/1 |
| int_memory | Memoria interna, GB |
| m_dep | Grosor, cm |
| mobile_wt | Peso, g |
| n_cores | Número de núcleos |
| pc | Cámara principal, megapíxeles |
| px_height | Alto de resolución, píxeles |
| px_width | Ancho de resolución, píxeles |
| ram | Memoria RAM, MB |
| sc_h | Alto de pantalla, cm |
| sc_w | Ancho de pantalla, cm |
| talk_time | Duración de conversación, horas |
| three_g | Soporte 3G, 0/1 |
| touch_screen | Pantalla táctil, 0/1 |
| wifi | Wi-Fi, 0/1 |
| price_range | Objetivo: 0 bajo, 1 medio, 2 alto, 3 muy alto |

## Calidad y decisiones

`px_height` y `sc_w` contienen ceros físicamente cuestionables. Se reportan en EDA;
se conservan en el experimento inicial para no inventar valores ni alterar el origen.
Una comparación futura podría tratarlos como ausentes e imputarlos dentro de cada fold,
pero requeriría un nuevo protocolo si ya se examinó el test final.
No se usa SMOTE: las clases están equilibradas. No se necesita codificación one-hot
porque los predictores ya son numéricos y los indicadores binarios tienen códigos 0/1.
No se interpreta la correlación como causalidad ni como importancia del modelo.
