from airflow.models import BaseOperator
from airflow.hooks.mysql_hook import MySqlHook
from airflow.hooks.S3_hook import S3Hook
from airflow.utils.decorators import apply_defaults
from airflow.hooks.base import BaseHook
import pandas

class IncrementalLoadOperator(BaseOperator):
    @apply_defaults
    def __init__(self,
                mysql_con_id,
                s3_con_id,
                table,
                s3_bucket,
                s3_prefix,
                *args, **kwargs):
        super(IncrementalLoadOperator,self).__init__(*args,**kwargs)
        self.mysql_con_id = mysql_con_id
        self.s3_con_id = s3_con_id
        self.table = table
        self.s3_bucket = s3_bucket,
        self.s3_prefix = s3_prefix
    def execute(self, context):
        mysql_hook = MySqlHook(self.mysql_con_id)
        s3_hook = S3Hook(self.s3_con_id)
        obj = s3_hook.get_key(self.s3_bucket,self.s3_prefix + "/log.csv")
        if obj is None:
            query = f"select * from {self.table}"
            df = pandas.read_sql(query, mysql_hook.get_conn())
            csv_string = df.to_csv(index=False)
            s3_hook.load_string(string_data=csv_string, key= self.s3_prefix + "/" + self.table + ".csv", bucket_name= self.s3_bucket)
            if self.table == 'global_temperature_table':
                latest_load_index =  df.tail(1)['dt']
            else:
                latest_load_index = df.tail(1)['index']
            index_df = pandas.DataFrame({"index":[latest_load_index]},index=False)
            csv_string = index_df.to_csv(index=False)
            s3_hook.load_string(string_data=csv_string, key= self.s3_prefix + "/log.csv", bucket_name= self.s3_bucket)
        else:
            index_df = pandas.read_csv(obj.get())
            previous_loaded_index = index_df.tail(1)["index"]
            if self.table == 'global_temperature_table':
                query = f"select * from {self.table} where dt > {previous_loaded_index}"
            else:
                query = f"select * from {self.table} where index > {previous_loaded_index}"
            new_data = mysql_hook.get_record(query)
            if not new_data is None:
                query = f"select * from {self.table}"
                df = pandas.read_sql(query, mysql_hook.get_conn())
                csv_string = df.to_csv(index=False)
                s3_hook.load_string(string_data=csv_string, key= self.s3_prefix + "/" + self.table + ".csv", bucket_name= self.s3_bucket)
                if self.table == 'global_temperature_table':
                    latest_load_index =  df.tail(1)['dt']
                else:
                    latest_load_index = df.tail(1)['index']
                index_df = index_df.append({"index":[latest_load_index]},ignore_index=True)
                csv_string = index_df.to_csv(index=False)
                s3_hook.load_string(string_data=csv_string, key= self.s3_prefix + "/log.csv", bucket_name= self.s3_bucket)



