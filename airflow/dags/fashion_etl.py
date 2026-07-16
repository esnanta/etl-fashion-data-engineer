from __future__ import annotations
from datetime import datetime
from airflow import DAG

with DAG(
    dag_id="fashion_etl",
    description="Fashion ETL Pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags={"fashion", "etl", "learning"},
):
    pass