from airflow.models import BaseOperator
from airflow.hooks.mysql_hook import MySqlHook
from airflow.hooks.S3_hook import S3Hook
from airflow.utils.decorators import apply_defaults
from airflow.hooks.base import BaseHook
import pandas
from datetime import datetime

"""
Permissions for 'airflow_etl_key.pem' are too open.
It is required that your private key files are NOT accessible by others.
This private key will be ignored.
How to fix?
=> icacls airflow_etl_key.pem /inheritance:r /grant %username%:F
"""
class IncrementalLoadOperator(BaseOperator):
    @apply_defaults
    def __init__(self,
                mysql_con_id: str,
                s3_con_id: str,
                table: str,
                s3_bucket: str,
                s3_prefix: str,
                *args, **kwargs):
        super(IncrementalLoadOperator,self).__init__(*args,**kwargs)
        self.mysql_con_id = mysql_con_id
        self.s3_con_id = s3_con_id
        self.table = table
        self.s3_bucket = s3_bucket
        self.s3_prefix = s3_prefix
    def execute(self, context):
        mysql_hook = MySqlHook(self.mysql_con_id)
        s3_hook = S3Hook(self.s3_con_id)
        log_key = '/log.csv'
        if self.s3_prefix == 'db_temperature_by_city':
            log_key = '/temp_table_log.csv'
        if not s3_hook.check_for_key(bucket_name = self.s3_bucket, key= self.s3_prefix + log_key):
            query = f"select * from {self.table}"
            df = pandas.read_sql(query, mysql_hook.get_conn())
            if not self.table == 'city_table':
                df['dated_ingest'] = datetime.utcnow()
                csv_string = df.to_csv(index=False)
                s3_hook.load_string(string_data=csv_string, key= self.s3_prefix + "/" + self.table + ".csv", replace = True, bucket_name= self.s3_bucket)
                if self.table == 'global_temperature_table':
                    latest_load_index =  df.tail(1).loc[:,'dt'].values[0]
                else:
                    latest_load_index = df.tail(1).loc[:,'index'].values[0]
                index_df = pandas.DataFrame({"index":[latest_load_index]})
                csv_string = index_df.to_csv(index=False)
                s3_hook.load_string(string_data=csv_string, key= self.s3_prefix + log_key,replace = True ,bucket_name= self.s3_bucket)
            else:
                csv_string = df.to_csv(index=False)
                s3_hook.load_string(string_data=csv_string, key= self.s3_prefix + "/" + self.table + ".csv", replace = True, bucket_name= self.s3_bucket)
        else:
            if not self.table == 'city_table':
                obj = s3_hook.get_key(bucket_name=self.s3_bucket,key = self.s3_prefix + log_key)
                index_df = pandas.read_csv(obj.get()['Body'])
                previous_loaded_index = index_df.tail(1).loc[:,'index'].values[0]
                if self.table == 'global_temperature_table':
                    query = f"select * from {self.table} where dt > {previous_loaded_index[1:-1]};"
                else:
                    query = f"select * from {self.table} where {self.table}.index > {int(previous_loaded_index)};"
                new_data = pandas.read_sql(query,mysql_hook.get_conn())
                if not new_data.empty:
                    new_data['dated_ingest'] = datetime.utcnow()
                    obj = s3_hook.get_key(bucket_name=self.s3_bucket, key= self.s3_prefix + "/" + self.table + ".csv")
                    old_data = pandas.read_csv(obj.get()['Body'])
                    df = pandas.concat([old_data,new_data],ignore_index=True)
                    csv_string = df.to_csv(index=False)
                    s3_hook.load_string(string_data=csv_string, key= self.s3_prefix + "/" + self.table + ".csv",replace = True, bucket_name= self.s3_bucket)
                    if self.table == 'global_temperature_table':
                        latest_load_index =  df.tail(1).loc[:,'dt'].values[0]
                    else:
                        latest_load_index = df.tail(1).loc[:,'index'].values[0]
                    index_df = index_df.append({"index":latest_load_index},ignore_index=True)
                    csv_string = index_df.to_csv(index=False)
                    s3_hook.load_string(string_data=csv_string, key= self.s3_prefix + log_key,replace = True, bucket_name= self.s3_bucket)
            else:
                query = f"select * from {self.table};"
                df = pandas.read_sql(query, mysql_hook.get_conn())
                csv_string = df.to_csv(index=False)
                s3_hook.load_string(string_data=csv_string, key= self.s3_prefix + "/" + self.table + ".csv",replace = True, bucket_name= self.s3_bucket)


