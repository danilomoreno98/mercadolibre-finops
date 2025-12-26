# Arquitectura

## Diseño arquitectura


### 1.1. Arquitectura patrón de ingesta en bulk para los datos históricos

Diseñar una arquitectura de datos donde se visualice qué tecnologías o herramientas se deben articular para que los logs de SmallB y SmallC se logren integrar con el sistema de datos de BigA. **Utilizando un patrón de ingesta en bulk para los datos históricos.**

![Arquitectura histórica](https://github.com/danilomoreno98/mercadolibre-finops/blob/main/media/Arq_historico.png?raw=true)

### 1.2. Arquitectura patrón de ingesta en streaming
Diseñar una arquitectura de datos donde se visualice qué tecnologías o herramientas se deben articular para que los logs de SmallB y SmallC se logren integrar con el sistema de datos de BigA. **Utilizando un patrón de ingesta en streaming para los datos en tiempo real que se irán generando en el futuro.**

![Arquitectura streaming](https://github.com/danilomoreno98/mercadolibre-finops/blob/main/media/Arq_streaming.png?raw=true)

## Análisis costos

### BigA
- SQS:
    - Costo region us-east-1, $0,4 (From 1 Million to 100 Billion Requests/Month)
    - Archivos/mes: 400.000 × 30 = 12.000.000
    - Requests aprox: 3 por archivo (send/receive/delete) ⇒ 36.000.000 requests/mes
    - Costo SQS ≈ $14,4/mes

## Modelo de datos y consultas

## Absorción arquitectura


# Analítica
