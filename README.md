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

## Silver — mínimo necesario (1 tabla por empresa, partición por hora)

> Partición recomendada: Hidden partition Iceberg hour(event_timestamp)

### silver.biga_energy_readings
| Columna | Tipo |
|--------|------|
| event_timestamp | timestamp |
| event_date | date |
| customer_id | string |
| consumption_kwh | double |
| revenue_usd | double |
| cost_usd | double |

### silver.smallb_energy_readings
| Columna | Tipo |
|--------|------|
| event_timestamp | timestamp |
| event_date | date |
| customer_id | string |
| consumption_kwh | double |
| revenue_usd | double |
| cost_usd | double |

### silver.smallc_energy_readings
| Columna | Tipo |
|--------|------|
| event_timestamp | timestamp |
| event_date | date |
| customer_id | string |
| consumption_kwh | double |
| revenue_usd | double |
| cost_usd | double |

---

## Gold — mínimo necesario (conformado para analítica)

> Partición recomendada: Hidden partition Iceberg hour(event_timestamp)

### gold.fact_energy_consumption
| Columna | Tipo |
|--------|------|
| event_timestamp | timestamp |
| event_date | date |
| company_id | string |
| customer_id | string |
| consumption_kwh | double |
| revenue_usd | double |
| cost_usd | double |

### gold.dim_company
| Columna | Tipo |
|--------|------|
| company_id | string |
| company_name | string |


### Query 1 — Tercer mayor consumo en cada empresa

```sql
WITH customer_consumption AS (
  SELECT
    company_id,
    customer_id,
    SUM(consumption_kwh) AS total_consumption_kwh
  FROM gold.fact_energy_consumption
  GROUP BY company_id, customer_id
),
ranked AS (
  SELECT
    company_id,
    customer_id,
    total_consumption_kwh,
    ROW_NUMBER() OVER (
      PARTITION BY company_id
      ORDER BY total_consumption_kwh DESC
    ) AS rn
  FROM customer_consumption
)
SELECT
  company_id,
  customer_id,
  total_consumption_kwh AS third_highest_consumption_kwh
FROM ranked
WHERE rn = 3;
```

### Query — Empresa adquirida más rentable

```sql
SELECT
  company_id,
  SUM(revenue_usd) AS total_revenue_usd,
  SUM(cost_usd) AS total_cost_usd,
  SUM(revenue_usd) - SUM(cost_usd) AS profit_usd
FROM gold.fact_energy_consumption
WHERE company_id IN ('SmallB', 'SmallC')
GROUP BY company_id
ORDER BY profit_usd DESC
LIMIT 1;
```

# Analítica

## Arquitectura

![Arquitectura analitica](https://github.com/danilomoreno98/mercadolibre-finops/blob/main/media/Arq_analitica.png?raw=true)

## Pipeline (DAG Airflow)

El código del DAG se encuentra en: [`airflow/dags/MELI_FINOPS_DI.py`](airflow/dags/MELI_FINOPS_DI.py)

El DAG diario orquesta la ingesta de datos FinOps desde AWS DataSync hacia S3 y ejecuta el datamodel (DBT) de FinOps en ECS Fargate con particionamiento hidden a nivel de día.

**Características principales:**

- **Diseño dinámico**: El DAG está diseñado con variables (`DATASYNC_TASK_ARNS`, `S3_FINOPS_PREFIXS`) que pueden ser configuradas como variables de Airflow, fortaleciendo la reutilización y facilitando añadir o quitar fuentes de datos sin modificar el código del DAG.

- **Actualización incremental con Iceberg**: Gracias al uso de Apache Iceberg con la estrategia merge, llave única y condición de actualización (`update_condition='src.upload_at > target.upload_at'`), se asegura reflejar siempre los datos más recientes. Esto es especialmente importante considerando que los registros de un mes pueden cambiar durante los primeros 15 días del mes siguiente (ej: datos de enero pueden actualizarse hasta el 15 de febrero), garantizando que las consultas siempre reflejen la información más actualizada.

![DAG analitica](https://github.com/danilomoreno98/mercadolibre-finops/blob/main/media/DAG_analitica.png?raw=true)

## Tablero Tableau

- ¿Cómo ha evolucionado el costo total mes a mes?
- ¿Cuáles son los servicios con mayor crecimiento en los últimos 7 días?
- ¿Qué tres servicios en la nube tienen los mayores costos por proveedor?

![Tableau_1](https://github.com/danilomoreno98/mercadolibre-finops/blob/main/media/Tableau_1.png?raw=true)


- ¿Puedes agrupar servicios para mostrar la evolución de categorías similares entre proveedores? (Por ejemplo, evolución de servicios de almacenamiento, cómputo y red). 

Para llevar a cabo este análisis, se creó una semilla (`dim_services`) con la dimensión de categoría de servicios que mapea códigos de servicios de nube (AWS, GCP, OCI) a sus categorías correspondientes. La semilla se encuentra en [`data_models_finops/seeds/dim_services.csv`](data_models_finops/seeds/dim_services.csv) y permite enriquecer la tabla de facturación para realizar análisis agrupados por categoría.

![Tableau_2](https://github.com/danilomoreno98/mercadolibre-finops/blob/main/media/Tableau_2.png?raw=true)

- Si tuvieras que formular una estrategia para reducir costos en uno o más servicios, ¿cuál sería?

Basándome en los datos disponibles en `fact_billing_cloud` y las categorías de servicios en `dim_services`, una estrategia efectiva de reducción de costos seguiría este enfoque:

### 1. Identificación y priorización (Quick Wins)
- **Análisis de Pareto**: Identificar el 20% de servicios que representan el 80% de los costos totales usando `fact_billing_cloud`
- **Servicios huérfanos**: Detectar servicios con costos pero sin uso reciente (comparando `usage_amount` vs `cost_usd`)
- **Crecimiento anómalo**: Identificar servicios con mayor crecimiento porcentual en los últimos 7-30 días

### 2. Optimización por categoría

**Cómputo (Cloud Run, EC2, Compute Engine)**:
- Right-sizing: Analizar métricas de uso (`usage_amount`) vs costo para identificar instancias sobre-dimensionadas
- Reservas/Committed Use Discounts: Para cargas de trabajo predecibles
- Spot/Preemptible instances: Para cargas tolerantes a interrupciones
- Consolidación: Identificar aplicaciones con bajo uso que pueden compartir recursos

**Almacenamiento (Glacier, Cloud Storage)**:
- Lifecycle policies: Mover datos antiguos a tiers más económicos automáticamente
- Compresión y deduplicación: Reducir el volumen de datos almacenados
- Eliminación de datos obsoletos: Identificar buckets/tablas sin acceso reciente

**Base de datos y Analítica**:
- Query optimization: Identificar queries costosas mediante análisis de uso
- Retención de datos: Reducir períodos de retención donde sea posible
- Compresión de datos: Implementar compresión.

### 3. Comparación multi-proveedor
- **Benchmarking**: Comparar costos por categoría entre AWS, GCP y OCI usando `provider` y `service_code`
- **Migration opportunities**: Identificar servicios donde cambiar de proveedor pueda generar ahorros significativos

### 4. Monitoreo y gobernanza continua
- **Alertas de costo**: Configurar alertas cuando servicios excedan umbrales definidos
- **Tagging y accountability**: Asegurar que todas las aplicaciones (`application`) estén correctamente etiquetadas para atribución de costos
- **Dashboards**: Crear vistas agregadas por `billing_entity`, `application` y `categoria` para facilitar la toma de decisiones.