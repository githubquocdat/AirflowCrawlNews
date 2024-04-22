from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import sys
import os
sys.path.insert(0,os.path.abspath(os.path.dirname(__file__)))

from funcc import news

with DAG(
    dag_id="crawl",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False ) as dag:
    
    link = PythonOperator(
        task_id = 'link',
        python_callable = news
    )
    link