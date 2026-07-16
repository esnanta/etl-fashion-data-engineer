from __future__ import annotations
from datetime import datetime
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

from airflow.dags.tasks.transform import transform_task
from airflow.dags.tasks.validate import validate_task
from tasks.extract import extract_task


with DAG(
    dag_id="fashion_etl",
    description="Fashion ETL Pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags={"fashion", "etl", "learning"},
) as dag:

    extract = PythonOperator(
        task_id="extract",
        python_callable=extract_task,
    )

    validate = PythonOperator(
        task_id="validate",
        python_callable=validate_task,
    )

    transform = PythonOperator(
        task_id="transform",
        python_callable=transform_task,
    )

    extract >> validate >> transform