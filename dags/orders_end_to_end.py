from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "data-platform",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
    "email_on_failure": False,
}

with DAG(
    dag_id="orders_end_to_end",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["ETL", "ML", "VKR"],
    default_args=default_args,
    doc_md="""
    Полный пайплайн: генерация источников → парсинг → staging → DWH →
    контроль качества → обучение → предсказание.
    """,
) as dag:
    PROJECT_DIR = "/opt/airflow"
    ENV_PREFIX = (
        f"cd {PROJECT_DIR} && "
        f"export PYTHONPATH={PROJECT_DIR}:/home/airflow/.local/lib/python3.11/site-packages && "
    )

    generate = BashOperator(
        task_id="generate_sources",
        bash_command=ENV_PREFIX + "python src/generate_sources.py",
    )
    parse = BashOperator(
        task_id="web_parsing",
        bash_command=ENV_PREFIX + "python src/web_parser.py",
    )
    staging = BashOperator(
        task_id="load_staging",
        bash_command=ENV_PREFIX + "python src/load_staging.py",
    )
    dwh = BashOperator(
        task_id="build_dwh",
        bash_command=ENV_PREFIX + "python src/build_dwh.py",
    )
    dq = BashOperator(
        task_id="data_quality",
        bash_command=ENV_PREFIX + "python src/data_quality.py",
    )
    train = BashOperator(
        task_id="train_model",
        env={"PYTHONUNBUFFERED": "1"},
        append_env=True,
        bash_command=ENV_PREFIX + "python ml/train.py",
    )

    predict = BashOperator(
        task_id="predict",
        env={"PYTHONUNBUFFERED": "1"},
        append_env=True,
        bash_command=ENV_PREFIX + "python ml/predict.py",
    )

    generate >> parse >> staging >> dwh >> dq >> train >> predict