from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator
from airflow.operators.bash_operator import BashOperator
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
from airflow.models.baseoperator import chain
import os

# from task_function_dependencies import load_city_temperature, load_country_temperature, load_global_temperature
from Airflow_Custom_Operators import IncrementalLoadOperator

spark_con = os.environ.get("AIRFLOW_CONN_SPARK_CON")

default_args = {
    "owner": "Nguyen Dinh Quoc",
    "depends_on_past": False,
    "start_date": datetime(year=2023, month=1, day=21),
    "email": ["quocthogminhqtm@gmail.com"],
    "email_on_failure": True,
    "email_on_retry": True,
    "retries": 0,
    "retry_delay": timedelta(minutes=1),
}

dag = DAG(
    "s3_loading_dag",
    description="This is an Airflow Dag to load data from sources to Staging Area (S3 Bucket)",
    default_args=default_args,
    catchup=False,
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
    task_id="Complex_city_citytable_data_load_task",
    dag=dag,
    mysql_con_id="mysql_con_city",
    s3_con_id="s3_con",
    table="city_table",
    s3_bucket="temperature-project-bucket1",
    s3_prefix="db_temperature_by_city",
)

complex_city_tab2_load_task = IncrementalLoadOperator(
    task_id="Complex_city_temptable_load_task",
    dag=dag,
    mysql_con_id="mysql_con_city",
    s3_con_id="s3_con",
    table="temperature_table",
    s3_bucket="temperature-project-bucket1",
    s3_prefix="db_temperature_by_city",
)

complex_country_load_task = IncrementalLoadOperator(
    task_id="Complex_country_data_load_task",
    dag=dag,
    mysql_con_id="mysql_con_country",
    s3_con_id="s3_con",
    table="temperature_country_table",
    s3_bucket="temperature-project-bucket1",
    s3_prefix="db_temperature_by_country",
)

complex_global_load_task = IncrementalLoadOperator(
    task_id="Complex_global_data_load_task",
    dag=dag,
    mysql_con_id="mysql_con_global",
    s3_con_id="s3_con",
    table="global_temperature_table",
    s3_bucket="temperature-project-bucket1",
    s3_prefix="db_temperature_global",
)

"""
The reason why I can not use SparkSubmitOperator is that spark_con which is even set spark://abc:7077 
misses the prefix spark:// when SparkSubmitOperator performs tasks
You can try if you want to see how stupid it is :)
Note that: if you configure the connection on the airflow UI, this will work perfectly
however, if you specify the spark connection in environment variable,... this will be like this :)
"""

# complex_city_tab1_process_task = SparkSubmitOperator(
#     task_id="Complex_city_citytable_data_process_task",
#     dag=dag,
#     conn_id="spark_con",
#     application="./Spark_process_script.py",
#     application_args=[
#         "city_table",
#         "temperature-project-bucket1",
#         "db_temperature_by_city",
#     ],
#     conf={
#         "spark.executor.cores": 2,
#         "spark.executor.memory": "1g",
#         "spark.network.timeout": 10000000,
#     },
#     packages="com.amazonaws:aws-java-sdk-bundle:1.12.264,org.apache.hadoop:hadoop-aws:3.3.1",
# )

bash_command = f"spark-submit --master {spark_con}  --conf spark.executor.cores=2 --conf spark.executor.memory=1g --conf spark.network.timeout=10000000 --packages com.amazonaws:aws-java-sdk-bundle:1.12.264,org.apache.hadoop:hadoop-aws:3.3.1 --name arrow-spark /opt/airflow/dags/Spark_process_script.py city_table temperature-project-bucket1 db_temperature_by_city"

complex_city_tab1_process_task = BashOperator(
    task_id="Complex_city_citytable_data_process_task",
    dag=dag,
    bash_command=bash_command,
)

# complex_city_tab2_process_task = SparkSubmitOperator(
#     task_id="Complex_city_temptable_process_task",
#     dag=dag,
#     conn_id="spark_con",
#     application="./Spark_process_script.py",
#     application_args=[
#         "temperature_table",
#         "temperature-project-bucket1",
#         "db_temperature_by_city",
#     ],
#     conf={
#         "spark.executor.cores": 2,
#         "spark.executor.memory": "1g",
#         "spark.network.timeout": 10000000,
#     },
#     packages="com.amazonaws:aws-java-sdk-bundle:1.12.264,org.apache.hadoop:hadoop-aws:3.3.1",
# )

bash_command = f"spark-submit --master {spark_con} --conf spark.executor.cores=2 --conf spark.executor.memory=1g --conf spark.network.timeout=10000000 --packages com.amazonaws:aws-java-sdk-bundle:1.12.264,org.apache.hadoop:hadoop-aws:3.3.1 --name arrow-spark /opt/airflow/dags/Spark_process_script.py temperature_table temperature-project-bucket1 db_temperature_by_city"

complex_city_tab2_process_task = BashOperator(
    task_id="Complex_city_temptable_process_task", dag=dag, bash_command=bash_command
)

# complex_country_process_task = SparkSubmitOperator(
#     task_id="Complex_country_data_process_task",
#     dag=dag,
#     conn_id="spark_con",
#     application="./Spark_process_script.py",
#     application_args=[
#         "temperature_country_table",
#         "temperature-project-bucket1",
#         "db_temperature_by_country",
#     ],
#     conf={
#         "spark.executor.cores": 2,
#         "spark.executor.memory": "1g",
#         "spark.network.timeout": 10000000,
#     },
#     packages="com.amazonaws:aws-java-sdk-bundle:1.12.264,org.apache.hadoop:hadoop-aws:3.3.1",
# )

bash_command = f"spark-submit --master {spark_con} --conf spark.executor.cores=2 --conf spark.executor.memory=1g --conf spark.network.timeout=10000000 --packages com.amazonaws:aws-java-sdk-bundle:1.12.264,org.apache.hadoop:hadoop-aws:3.3.1 --name arrow-spark /opt/airflow/dags/Spark_process_script.py temperature_country_table temperature-project-bucket1 db_temperature_by_country"

complex_country_process_task = BashOperator(
    task_id="Complex_country_data_process_task", dag=dag, bash_command=bash_command
)


# complex_global_process_task = SparkSubmitOperator(
#     task_id="Complex_global_data_process_task",
#     dag=dag,
#     conn_id="spark_con",
#     application="./Spark_process_script.py",
#     application_args=[
#         "global_temperature_table",
#         "temperature-project-bucket1",
#         "db_temperature_global",
#     ],
#     conf={
#         "spark.executor.cores": 2,
#         "spark.executor.memory": "1g",
#         "spark.network.timeout": 10000000,
#     },
#     packages="com.amazonaws:aws-java-sdk-bundle:1.12.264,org.apache.hadoop:hadoop-aws:3.3.1",
# )

bash_command = f"spark-submit --master {spark_con} --conf spark.executor.cores=2 --conf spark.executor.memory=1g --conf spark.network.timeout=10000000 --packages com.amazonaws:aws-java-sdk-bundle:1.12.264,org.apache.hadoop:hadoop-aws:3.3.1 --name arrow-spark /opt/airflow/dags/Spark_process_script.py global_temperature_table temperature-project-bucket1 db_temperature_global"

complex_global_process_task = BashOperator(
    task_id="Complex_global_data_process_task", dag=dag, bash_command=bash_command
)

complex_data_transform_task = SparkSubmitOperator(
    task_id="Complex_data_transform_process_task",
    dag=dag,
    conn_id="spark_con",
    application="./Spark_integrate_script.py",
    conf={
        "spark.executor.cores": 2,
        "spark.executor.memory": "1g",
        "spark.network.timeout": 10000000,
    },
    packages="com.amazonaws:aws-java-sdk-bundle:1.12.264,org.apache.hadoop:hadoop-aws:3.3.1",
)

complex_load_data_country_dimension_table = S3ToRedshiftOperator(
    task_id="Complex_load_data_country_dimension_table",
    dag=dag,
    schema="climate_etl_schema",
    table="country_dimension_table",
    s3_bucket="temperature-project-bucket1",
    s3_key="integrate/data/country_dimension_table",
    redshift_conn_id="redshift_con_id",
    aws_conn_id="s3_con",
    method="APPEND",
    copy_options=["IGNOREHEADER 1", "DELIMITER ','", "CSV"],
    column_list=["country", "CountryId", "Country_Format_Holistics"],
)

complex_load_data_country_detail_dimension_table = S3ToRedshiftOperator(
    task_id="Complex_load_data_country_detail_dimension_table",
    dag=dag,
    schema="climate_etl_schema",
    table="country_detail_dimension_table",
    s3_bucket="temperature-project-bucket1",
    s3_key="integrate/data/country_detail_dimension_table",
    redshift_conn_id="redshift_con_id",
    aws_conn_id="s3_con",
    method="APPEND",
    copy_options=["IGNOREHEADER 1", "DELIMITER ','", "CSV"],
    column_list=[
        "country_temperature_detail_id",
        "averagetemperature",
        "averagetemperatureuncertainty",
        "countryid",
    ],
)

complex_load_data_city_dimension_table = S3ToRedshiftOperator(
    task_id="Complex_load_data_city_dimension_table",
    dag=dag,
    schema="climate_etl_schema",
    table="city_dimension_table",
    s3_bucket="temperature-project-bucket1",
    s3_key="integrate/data/city_dimension_table",
    redshift_conn_id="redshift_con_id",
    aws_conn_id="s3_con",
    method="APPEND",
    copy_options=["IGNOREHEADER 1", "DELIMITER ','", "CSV"],
    column_list=["city", "latitude", "longitude", "cityid"],
)

complex_load_data_city_detail_dimension_table = S3ToRedshiftOperator(
    task_id="Complex_load_data_city_detail_dimension_table",
    dag=dag,
    schema="climate_etl_schema",
    table="city_detail_dimension_table",
    s3_bucket="temperature-project-bucket1",
    s3_key="integrate/data/city_detail_dimension_table",
    redshift_conn_id="redshift_con_id",
    aws_conn_id="s3_con",
    method="APPEND",
    copy_options=["IGNOREHEADER 1", "DELIMITER ','", "CSV"],
    column_list=[
        "CityId",
        "City_Temperature_Detail_Id",
        "AverageTemperature",
        "AverageTemperatureUncertainty",
        "CountryId",
    ],
)

complex_load_data_global_detail_dimension_table = S3ToRedshiftOperator(
    task_id="Complex_load_data_global_detail_dimension_table",
    dag=dag,
    schema="climate_etl_schema",
    table="global_detail_dimension_table",
    s3_bucket="temperature-project-bucket1",
    s3_key="integrate/data/global_detail_dimension_table",
    redshift_conn_id="redshift_con_id",
    aws_conn_id="s3_con",
    method="APPEND",
    copy_options=["IGNOREHEADER 1", "DELIMITER ','", "CSV", "ACCEPTINVCHARS AS '?'"],
    column_list=[
        "LandAverageTemperature",
        "LandAverageTemperatureUncertainty",
        "LandMaxTemperature",
        "LandMaxTemperatureUncertainty",
        "LandMinTemperature",
        "LandMinTemperatureUncertainty",
        "LandAndOceanAverageTemperature",
        "LandAndOceanAverageTemperatureUncertainty",
        "global_temperature_detail_id",
    ],
)

complex_load_data_temperature_fact_table = S3ToRedshiftOperator(
    task_id="Complex_load_data_temperature_fact_table",
    dag=dag,
    schema="climate_etl_schema",
    table="temperature_fact_table",
    s3_bucket="temperature-project-bucket1",
    s3_key="integrate/data/temperature_fact_table",
    redshift_conn_id="redshift_con_id",
    aws_conn_id="s3_con",
    method="APPEND",
    copy_options=["IGNOREHEADER 1", "DELIMITER ','", "CSV"],
    column_list=[
        "dt",
        "Country_Temperature_Detail_Id",
        "Global_Temperature_Detail_Id",
        "City_Temperature_Detail_Id",
    ],
)

chain(
    [
        complex_city_tab1_load_task,
        complex_city_tab2_load_task,
        complex_country_load_task,
        complex_global_load_task,
    ],
    [
        complex_city_tab1_process_task,
        complex_city_tab2_process_task,
        complex_country_process_task,
        complex_global_process_task,
    ],
    complex_data_transform_task,
    [
        complex_load_data_country_dimension_table,
        complex_load_data_country_detail_dimension_table,
        complex_load_data_city_dimension_table,
        complex_load_data_city_detail_dimension_table,
        complex_load_data_global_detail_dimension_table,
        complex_load_data_temperature_fact_table,
    ],
)
