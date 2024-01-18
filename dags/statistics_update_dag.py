import datetime

from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator
from hydra import compose, initialize


initialize(version_base=None, config_path="../../soccer_api/conf")
cfg = compose(config_name="configs.yaml")

ARGS = dict(cfg["airflow"]["dag_args"])

with DAG(
    dag_id="statistics_update",
    schedule="@daily",
    start_date=datetime.datetime(2024, 1, 5, 9, 45),
    catchup=False,
    tags=["soccer"],
    default_args=ARGS,
) as dag:
    task_update_statistics = BashOperator(
        task_id="daily_statistics_update",
        bash_command="./statistics_update_run.sh",
        dag=dag,
    )

    task_update_aggregations = BashOperator(
        task_id="daily_aggregations_update",
        bash_command="./aggregations_update_run.sh",
        dag=dag,
    )

    task_update_statistics >> task_update_aggregations
