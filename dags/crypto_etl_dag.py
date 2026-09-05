"""Airflow orchestration for the existing crypto ETL pipeline."""

from datetime import timedelta
from pathlib import Path
import sys

from airflow import DAG
from airflow.operators.python import PythonOperator
from pendulum import datetime


# Let the scheduler import the project's existing ETL entry point.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from main import run_pipeline


with DAG(
    dag_id="crypto_etl_hourly",
    description="Run the CoinGecko to PostgreSQL ETL pipeline every hour.",
    start_date=datetime(2026, 9, 5, tz="UTC"),
    schedule="@hourly",
    catchup=False,
    default_args={
        "retries": 3,
        "retry_delay": timedelta(minutes=5),
    },
    tags=["crypto", "etl"],
) as dag:
    run_crypto_etl = PythonOperator(
        task_id="run_crypto_etl",
        python_callable=run_pipeline,
    )
