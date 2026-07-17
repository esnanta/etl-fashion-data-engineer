from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.providers.standard.operators.python import (
    PythonOperator,
)

from airflow.dags.tasks.task_export_csv import (
    export_csv_task,
)
from airflow.dags.tasks.task_extract import (
    extract_task,
)
from airflow.dags.tasks.task_transform import (
    transform_task,
)
from airflow.dags.tasks.task_upload_google_sheets import (
    upload_google_sheets_task,
)
from airflow.dags.tasks.task_validate import (
    validate_task,
)


with DAG(
    dag_id="fashion_etl",
    description="Fashion ETL Pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags={"fashion", "etl", "learning"},
) as dag:

    extract_task_instance = PythonOperator(
        task_id="extract",
        python_callable=extract_task,
    )

    validate_task_instance = PythonOperator(
        task_id="validate",
        python_callable=validate_task,
        op_args=[
            extract_task_instance.output,
        ],
    )

    transform_task_instance = PythonOperator(
        task_id="transform",
        python_callable=transform_task,
        op_args=[
            validate_task_instance.output,
        ],
    )

    export_csv_task_instance = PythonOperator(
        task_id="export_csv",
        python_callable=export_csv_task,
        op_args=[
            transform_task_instance.output,
        ],
    )

    upload_google_sheets_task_instance = PythonOperator(
        task_id="upload_google_sheets",
        python_callable=upload_google_sheets_task,
        op_args=[
            transform_task_instance.output,
        ],
    )

    (
        extract_task_instance
        >> validate_task_instance
        >> transform_task_instance
    )

    (
        transform_task_instance
        >> export_csv_task_instance
    )

    (
        transform_task_instance
        >> upload_google_sheets_task_instance
    )