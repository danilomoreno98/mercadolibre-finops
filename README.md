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

- Bucket bronze
    - GB/mes =0,828 x 2.592.000 = 2.145.767 GB/mes
    - (0 – 51.200 GB) = 51.200 GB × 0,023 = 1,177.60
    - (51.200 – 512.000 GB) = 460.800 GB × 0,022 = 10.137,60
    - (2.145.767 − 512.000) GB × 0,021 = 34.309,11
    - Costo total = ~45k

- SQS:
    - Archivos/mes: 400.000 × 30 = 12M
    - Requests aprox 3 por archivo (send/receive/delete) = 12M x 3 = 36M requests/mes
    - Costo en region us-east-1 (From 1 Million to 100 Billion Requests/Month) = 0,4 USD
    - Costo total = ~ $14,4/mes

- ECS:
    - Archivos/día = 400.000 / 86.400 = ~5 files/s
    - Task 24/7 = $41,94 / mes
    - Tiempo por archivo = ~10s
    - Tareas concurrentes = 5 x 10 = 50
    - Costo total = 50 x 41,94 = ~2k USD

- Kinesis Data Streams (~3Kb cada record)
    - Records/segundo = 25B/86400 = 289.352 records/s
    - GB/s = 389.352 x 3 / 1048576 = 0,828 GB/s
    - GB/mes =0,828 x 2.592.000 = 2.145.767 GB/mes
    - Costo Data In = 2.145.767 x 0.032 = 68.664,54 USD
    - Costo Out = 2.145.767 x 0,016 = 34.332,27 USD
    - Costo total = 103k USD aprox

- Amazon Managed Service for Apache Flink (~3Kb cada record)
    - Records/segundo = 25B/86400 = 289.352 records/s
    - KPUs = 289.352 / 10000 = 290 KPU
    - Horas / mes = 730 h
    - Costo compute KPU = 290 x 720 x 0,11 = 22968 USD
    - 1 KPU adicional fijo = 1 x 720 x 0,11 = 79,2 USD
    - Costo total = ~24,5k USD

- Bucket silver (asumiendo compresión 5x)
    - Costo total = ~9k

- Bucket gold (asumiendo compresión 5 y 10% de raw)
    - Costo total = ~1k

## Modelo de datos y consultas

## Absorción arquitectura


# Analítica
