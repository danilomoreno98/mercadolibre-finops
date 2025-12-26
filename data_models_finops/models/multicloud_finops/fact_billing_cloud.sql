{{ config(
    materialized='incremental',
    table_type='iceberg',
    incremental_strategy='merge',
    on_schema_change='append_new_columns'
    unique_key=["usage_date", "provider", "billing_entity", "application", "region", "service_code", "usage_type", "usage_unit"],
    partitioned_by=[day(usage_date)],
    update_condition='src.upload_at > target.upload_at'
    format='parquet'
) }}


WITH 
aws_billing AS (
    SELECT  DATE(start_date) AS usage_date
        ,   'aws' AS provider
        ,   account_id AS billing_entity
        ,   COALESCE(NULLIF(tag_application,''), 'UNKNOWN') AS application
        ,   region
        ,   service_code
        ,   usage_type
        ,   pricing_unit AS usage_unit
        ,   CAST("$file_modified_time" AS TIMESTAMP(6)) AS upload_at
        ,   SUM(usage_amount) AS usage_amount
        ,   SUM(net_cost) AS cost_usd
    FROM mercadolibre_raw.data_aws
    WHERE   TRUE
            AND year='{{ var("YEAR") }}'
            AND month='{{ var("MONTH") }}'
            AND day='{{ var("DAY") }}'
    GROUP BY 1,2,3,4,5,6,7,8,9
),
gcp_billing AS (
    SELECT  DATE(usage_start_date) AS usage_date
        ,   'gcp' AS provider
        ,   project_id AS billing_entity
        ,   COALESCE(NULLIF(label_application,''), 'UNKNOWN') AS application
        ,   location_region AS region
        ,   service_description AS service_code
        ,   sku_description AS usage_type
        ,   usage_pricing_unit AS usage_unit
        ,   CAST("$file_modified_time" AS TIMESTAMP(6)) AS upload_at
        ,   sum(usage_amount_in_pricing_units) AS usage_amount
        ,   sum(cost) AS cost_usd
    FROM "mercadolibre_raw"."data_gcp"
    WHERE   TRUE
            AND year='{{ var("YEAR") }}'
            AND month='{{ var("MONTH") }}'
            AND day='{{ var("DAY") }}'
    GROUP BY 1,2,3,4,5,6,7,8,9
),
oci_billing AS (
    SELECT  DATE(intervalusagestart) AS usage_date
        ,   'oci' AS provider
        ,   tenant_id AS billing_entity
        ,   'UNKNOWN' AS application
        ,   product_region AS region
        ,   product_service AS service_code
        ,   product_description AS usage_type
        ,   CAST(NULL AS varchar) AS usage_unit
        ,   CAST(NULL AS double) AS usage_amount
        ,   CAST("$file_modified_time" AS TIMESTAMP(6)) AS upload_at
        ,   CAST(SUM(total_cost)/500.0 AS DOUBLE) AS cost_usd
    FROM "mercadolibre_raw"."data_oci"
    WHERE   TRUE
            AND year='{{ var("YEAR") }}'
            AND month='{{ var("MONTH") }}'
            AND day='{{ var("DAY") }}'
    GROUP BY 1,2,3,4,5,6,7,8,9
)    
SELECT * FROM aws_billing
UNION ALL
SELECT * FROM gcp_billing
UNION ALL
SELECT * FROM oci_billing