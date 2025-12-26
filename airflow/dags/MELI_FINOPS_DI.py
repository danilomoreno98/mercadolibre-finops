from datetime import datetime
from typing import List

from airflow.decorators import dag
from airflow.utils.task_group import TaskGroup

from airflow.providers.amazon.aws.operators.datasync import DataSyncOperator
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.providers.amazon.aws.operators.ecs import EcsRunTaskOperator
from airflow.providers.amazon.aws.operators.glue_crawler import GlueCrawlerOperator
from airflow.operators.empty import EmptyOperator


# Vars data_interval_start
YEAR = "{{ data_interval_start.year }}"
MONTH = "{{ '%02d' | format(data_interval_start.month) }}"
DAY = "{{ '%02d' | format(data_interval_start.day) }}"

S3_BUCKET_NAME = "bucket_bronze"

# Vars Datasync
DATASYNC_TASK_ARNS: List[str] = [
    "arn:aws:datasync:us-east-1:123456789012:task/task-smallB",
    "arn:aws:datasync:us-east-1:123456789012:task/task-smallC"
]

# Vars s3 sensor
S3_FINOPS_PREFIXS: List[str] = [
    f"finops/smallB/year={YEAR}/month={MONTH}/day={DAY}/*.csv",
    f"finops/smallC/year={YEAR}/month={MONTH}/day={DAY}/*.csv",
]

# Vars Glue Crawler
GLUE_CRAWLER_NAME = "finops-crawler"
GLUE_CRAWLER_ROLE = "arn:aws:iam::123456789012:role/AWSGlueServiceRole"
GLUE_DATABASE_NAME = "finops_db"



@dag(
    dag_id="MELI_FINOPS_DI",
    start_date=datetime(2024, 1, 1),
    schedule="0 13 * * *",
    catchup=False,
    description="""
    DAG diario que orquesta la ingesta de datos FinOps desde AWS DataSync hacia S3 y ejecuta el datamodel (DBT) de FinOps en ECS Fargate YEAR/MONTH/DAY.
    
    Características principales:
    - Diseño dinámico: El DAG está diseñado con variables (DATASYNC_TASK_ARNS, S3_FINOPS_PREFIXS) que pueden ser configuradas como variables de Airflow, fortaleciendo la reutilización y facilitando añadir o quitar fuentes de datos sin modificar el código del DAG.
    - Actualización incremental con Iceberg: Gracias al uso de Apache Iceberg con la estrategia merge, llave única (unique_key) y condición de actualización (update_condition='src.upload_at > target.upload_at'), se asegura reflejar siempre los datos más recientes. Esto es especialmente importante considerando que los registros de un mes pueden cambiar durante los primeros 15 días del mes siguiente (ej: datos de enero pueden actualizarse hasta el 15 de febrero), garantizando que las consultas siempre reflejen la información más actualizada.
    """,
    tags=["meli", "finops", "daily"],
)
def workflow():

    start = EmptyOperator(task_id="start")
    end = EmptyOperator(task_id="end")

    with TaskGroup(group_id="ingest_g_tasks") as ingest_g_tasks:

        ingest_datasync = (
            DataSyncOperator.partial(
                task_id="ingest_datasync",
                aws_conn_id="aws_default",
                region_name="us-east-1",
                wait_for_completion=True,
                wait_interval_seconds=30,
                max_iterations=60,
            )
            .expand(task_arn=DATASYNC_TASK_ARNS)
        )

        sensor_raw_files_finops = (
            S3KeySensor.partial(
                task_id="sensor_raw_files_finops",
                aws_conn_id="aws_default",
                bucket_name=S3_BUCKET_NAME,
                poke_interval=30,
                timeout=60 * 60, 
                soft_fail=False,
            )
            .expand(bucket_key=S3_FINOPS_PREFIXS)
        )
        
        glue_crawler = GlueCrawlerOperator(
            task_id="glue_crawler",
            aws_conn_id="aws_default",
            config={
                "Name": GLUE_CRAWLER_NAME,
                "Role": GLUE_CRAWLER_ROLE,
                "DatabaseName": GLUE_DATABASE_NAME,
                "Targets": {
                    "S3Targets": [
                        {"Path": f"s3://{S3_BUCKET_NAME}/finops/smallB/"},
                        {"Path": f"s3://{S3_BUCKET_NAME}/finops/smallC/"},
                    ]
                },
            },
            region_name="us-east-1",
            wait_for_completion=True,
        )
        
        ingest_datasync >> sensor_raw_files_finops >> glue_crawler

    
    with TaskGroup(group_id="datamodel_g_tasks") as datamodel_g_tasks:
        dbt_finops_model = EcsRunTaskOperator(
        task_id="dbt_finops_model",
        aws_conn_id="aws_default",
        region_name="us-east-1",
        cluster="my-ecs-cluster",
        task_definition="my-task-definition:1",
        launch_type="FARGATE",
        # Para Fargate necesitas network_configuration:
        network_configuration={
            "awsvpcConfiguration": {
                "subnets": ["subnet-abc123", "subnet-def456"],
                "securityGroups": ["sg-0123456789abcdef0"],
                "assignPublicIp": "DISABLED",
            }
        },
        overrides={
            "containerOverrides": [
                {
                    "name": "my-container",
                    "environment": [
                        {"name": "YEAR", "value": YEAR},
                        {"name": "MONTH", "value": MONTH},
                        {"name": "DAY", "value": DAY},
                    ],
                }
            ]
        },
        wait_for_completion=True,
    )

    start >> ingest_g_tasks >> datamodel_g_tasks >> end


dag = workflow()
