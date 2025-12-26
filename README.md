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

- Bucket gold (asumiendo compresión 5x y 10% de raw)
    - Costo total = ~1k

### SmallB

- Bucket bronze (raw sin comprimir)
    - Logs/día = 10.000 × 288 = 2.880.000 logs/día
    - Logs/mes = 2.880.000 × 30 = 86.400.000 logs/mes
    - Records/segundo = 10.000 / 300 = 33,33 records/s
    - GB/s = 33,33 × 3 / 1.048.576 = 0,00009537 GB/s
    - GB/mes = 0,00009537 × 2.592.000 = 247,6 GB/mes
    - (0 – 51.200 GB) = 247,6 GB × 0,023 = 5,69 USD
    - Costo total = ~5,7 USD/mes

- SQS
    - Mensajes/mes = 86,4M
    - Requests aprox 3 por mensaje (send/receive/delete) = 86,4M × 3 = 259,2M requests/mes
    - Requests cobrados ≈ 258,2M
    - Costo = 0,4 USD por 1M requests
    - Costo total = ~103,28 USD/mes

- ECS
    - Records/segundo = 33,33 records/s
    - 1 task es suficiente
    - Task 24/7 = 41,94 USD/mes
    - Costo total = ~42 USD/mes

- Kinesis Data Streams (~3 KB cada record)
    - Records/segundo = 33,33 records/s
    - GB/s = 33,33 × 3 / 1.048.576 = 0,00009537 GB/s
    - GB/mes = 0,00009537 × 2.592.000 = 247,6 GB/mes
    - Costo Data In = 247,6 × 0,032 = 7,92 USD
    - Costo Out = 247,6 × 0,016 = 3,96 USD
    - Costo total = ~11,9 USD/mes

- Amazon Managed Service for Apache Flink (~3 KB cada record)
    - Records/segundo = 33,33 records/s
    - KPUs = 33,33 / 1.000 → 1 KPU
    - Horas / mes = 720 h
    - Costo compute KPU = 1 × 720 × 0,11 = 79,2 USD
    - Running storage = 50 GB × 0,10 = 5,0 USD
    - 1 KPU adicional fijo = 1 × 720 × 0,11 = 79,2 USD
    - Costo total = ~163,4 USD/mes

- Bucket silver (Parquet, compresión 5×)
    - GB/mes = 247,6 / 5 = 49,5 GB
    - 49,5 GB × 0,023 = 1,14 USD
    - Costo total = ~1,1 USD/mes

- Bucket gold (Parquet, compresión 5× y 10% de raw)
    - GB/mes = (247,6 × 0,10) / 5 = 4,95 GB
    - 4,95 GB × 0,023 = 0,11 USD
    - Costo total = ~0,1 USD/mes

### SmallC

- Bucket bronze (raw sin comprimir)
    - Logs/día = 80.000 × 288 = 23.040.000 logs/día
    - Logs/mes = 23.040.000 × 30 = 691.200.000 logs/mes
    - Records/segundo = 80.000 / 300 = 266,67 records/s
    - GB/s = 266,67 × 3 / 1.048.576 = 0,00076294 GB/s
    - GB/mes = 0,00076294 × 2.592.000 = 1.977,54 GB/mes
    - (0 – 51.200 GB) = 1.977,54 GB × 0,023 = 45,48 USD
    - Costo total = ~45,5 USD/mes

- SQS
    - Mensajes/mes = 691,2M
    - Requests aprox 3 por mensaje (send/receive/delete) = 691,2M × 3 = 2.073,6M requests/mes
    - Requests cobrados ≈ 2.072,6M
    - Costo = 0,4 USD por 1M requests
    - Costo total = ~829,04 USD/mes

- ECS
    - Records/segundo = 266,67 records/s
    - 1 task es suficiente
    - Task 24/7 = 41,94 USD/mes
    - Costo total = ~42 USD/mes

- Kinesis Data Streams (~3 KB cada record)
    - Records/segundo = 266,67 records/s
    - GB/s = 266,67 × 3 / 1.048.576 = 0,00076294 GB/s
    - GB/mes = 0,00076294 × 2.592.000 = 1.977,54 GB/mes
    - Costo Data In = 1.977,54 × 0,032 = 63,28 USD
    - Costo Out = 1.977,54 × 0,016 = 31,64 USD
    - Costo total = ~94,9 USD/mes

- Amazon Managed Service for Apache Flink (~3 KB cada record)
    - Records/segundo = 266,67 records/s
    - KPUs = 266,67 / 1.000 → 1 KPU
    - Horas / mes = 720 h
    - Costo compute KPU = 1 × 720 × 0,11 = 79,2 USD
    - Running storage = 50 GB × 0,10 = 5,0 USD
    - 1 KPU adicional fijo = 1 × 720 × 0,11 = 79,2 USD
    - Costo total = ~163,4 USD/mes

- Bucket silver (Parquet, compresión 5×)
    - GB/mes = 1.977,54 / 5 = 395,51 GB
    - 395,51 GB × 0,023 = 9,10 USD
    - Costo total = ~9,1 USD/mes

- Bucket gold (Parquet, compresión 5× y 10% de raw)
    - GB/mes = (1.977,54 × 0,10) / 5 = 39,55 GB
    - 39,55 GB × 0,023 = 0,91 USD
    - Costo total = ~0,9 USD/mes


## Modelo de datos y consultas

### Silver (curada, por empresa)
- silver_biga_events
    - event_date (date)
    - event_ts (timestamp)
    - user_id (string)
    - service (string)
    - units (double)
    - cost_usd (double)
    - revenue_usd (double)
    - source (string)  -- opcional: bigA/smallB/smallC
    - (partition: event_date)

- silver_smallb_events
    - mismas columnas y partición

- silver_smallc_events
    - mismas columnas y partición

> Nota: Mantener el MISMO esquema en las 3 tablas es clave para poder unirlas luego.

### Gold (modelo para usuarios: dimensiones + fact + agregados)
- dim_company
    - company_id
    - company_name
    - acquisition_date
    - region
    - industry

- dim_user
    - user_id
    - company_id
    - user_type

- fact_consumption (unificada)
    - event_date
    - event_ts
    - company_id
    - user_id
    - service
    - units
    - cost_usd
    - revenue_usd
    - source

## Absorción arquitectura


# Analítica
