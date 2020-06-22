"""
Airflow scheduling script
"""
from datetime import timedelta

from airflow import DAG

from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago

default_args = {
    "task_id": "UpdateAllData",
    "owner": "Saveliy.Belkin",
    "email": ["saveliy.belkin@thedataproject.xyz"],
    "email_on_failure": True,
    "email_on_retry": False,
    "start_date": days_ago(2),
    "retries": 1,
    "retry_delay": timedelta(minutes=120),
    "depends_on_past": False,
}
dag = DAG(
    "UpdateBusinessData",
    default_args=default_args,
    description="Updates all data and saves in PostgreSQL",
    schedule_interval=timedelta(days=7),
)

# print the date time
task1 = BashOperator(
    task_id="print_data",
    bash_command="date; cd /home/ubuntu/YelpTime/src/AirFlow",
    dag=dag,
)

# run pyspark
update_stm = (
    "/usr/local/spark/bin/spark-submit "
    + "--packages com.amazonaws:aws-java-sdk:1.7.4,org.apache.hadoop:hadoop-aws:2.7.7 "
    + "--master spark://ec2-54-226-115-222.compute-1.amazonaws.com:7077 "
    + "--jars /home/ubuntu/postgresql-42.2.14.jar "
    + "/home/ubuntu/YelpTime/src/pyspark_clean_data.py"
)
task2 = BashOperator(
    task_id="update_data", bash_command=update_stm, retries=2, dag=dag,
)

# run sql statements
sql_stm = (
    "psql "
    + "--host=54.226.115.222 "
    + "--dbname=business "
    + "--username=saveliy "
    + "--file=/home/ubuntu/YelpTime/src/SQLScripts/create_index.sql"
)
task3 = BashOperator(task_id="index_sql", bash_command=sql_stm, dag=dag)

task1 >> task2 >> task3
