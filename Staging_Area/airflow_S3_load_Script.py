from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
# from task_function_dependencies import load_city_temperature, load_country_temperature, load_global_temperature
from Airflow_Custom_Operators import IncrementalLoadOperator

default_args = {
    "owner": "Nguyen Dinh Quoc",
    "depends_on_past": False,
    "start_date": datetime(year=2023,month=1,day=21),
    "email": ["quocthogminhqtm@gmail.com"],
    "email_on_failure": True,
    "email_on_retry": True,
    "retries": 1,
    "retry_delay": timedelta(minutes=3)
}

dag = DAG(
    "s3_loading_dag",
    description= "This is an Airflow Dag to load data from sources to Staging Area (S3 Bucket)",
    default_args=default_args
)

"""
# This is a simple way to do so
country_load_task = PythonOperator(
    task_id = "country_data_load_task",
    dag=dag,
    python_callable= load_country_temperature
)
city_load_task = PythonOperator(
    task_id = "city_data_load_task",
    dag=dag,
    python_callable= load_city_temperature
)
global_load_task = PythonOperator(
    task_id = "global_data_load_task", 
    dag=dag,
    python_callable= load_global_temperature
)
"""

# This is a more complicated way to do so
complex_city_tab1_load_task = IncrementalLoadOperator(
    task_id = "Complex_city_citytable_data_load_task",
    dag=dag,
    mysql_con_id="MySQL_Con_City",
    s3_con_id="S3_Con",
    table="city_table",
    s3_bucket= "temperature-project-bucket",
    s3_prefix= "db_temperature_by_city"
)

complex_city_tab2_load_task = IncrementalLoadOperator(
    task_id = "Complex_city_temptable_load_task",
    dag=dag,
    mysql_con_id="MySQL_Con_City",
    s3_con_id="S3_Con",
    table="temperature_table",
    s3_bucket= "temperature-project-bucket",
    s3_prefix= "db_temperature_by_city"
)

complex_country_load_task = IncrementalLoadOperator(
    task_id = "Complex_country_data_load_task",
    dag=dag,
    mysql_con_id="MySQL_Con_Country",
    s3_con_id="S3_Con",
    table="temperature_country_table",
    s3_bucket= "temperature-project-bucket",
    s3_prefix= "db_temperature_by_country"
)

complex_global_load_task = IncrementalLoadOperator(
    task_id = "Complex_global_data_load_task",
    dag=dag,
    mysql_con_id="MySQL_Con_Global",
    s3_con_id="S3_Con",
    table="global_temperature_table",
    s3_bucket= "temperature-project-bucket",
    s3_prefix= "db_temperature_global"
)