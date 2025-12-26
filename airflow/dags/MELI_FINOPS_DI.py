from datetime import datetime
from typing import List

from airflow.decorators import dag
from airflow.utils.task_group import TaskGroup

from airflow.providers.amazon.aws.operators.datasync import DataSyncOperator
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.providers.amazon.aws.operators.ecs import EcsRunTaskOperator
from airflow.operators.empty import EmptyOperator


# Vars data_interval_start
YEAR = "{{ data_interval_start.year }}"
MONTH = "{{ '%02d' | format(data_interval_start.month) }}"
DAY = "{{ '%02d' | format(data_interval_start.day) }}"

S3_BUCKET_NAME = "mi-bucket-finops"

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



@dag(
    dag_id="MELI_FINOPS_DI",
    start_date=datetime(2024, 1, 1),
    schedule="0 13 * * *",
    catchup=False,
    description="DAG diario que orquesta la ingesta de datos FinOps desde AWS DataSync hacia S3 y ejecuta el datamodel (DBT) de FinOps en ECS Fargate YEAR/MONTH/DAY.",
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
        ingest_datasync >> sensor_raw_files_finops

    
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
