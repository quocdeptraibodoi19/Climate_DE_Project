import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import when, avg, round, current_timestamp
from pyspark.sql.types import StructField, StructType, IntegerType, TimestampType, DoubleType, StringType
from pyspark import SparkConf, SparkContext

spark = SparkSession(SparkContext(conf=SparkConf()).getOrCreate())

s3_table = ""
s3_bucket = "temperature-project-bucket"
s3_prefix = ""

s3_process_uri = "s3a://" + s3_bucket + "/" + s3_prefix + "/" + "preprocess_"+ s3_table

# This script is used to intergrate data into a single one.

# country table:
s3_prefix = "db_temperature_by_country"
s3_table = "temperature_country_table"

temp_country_df = spark.read.format('csv').options(header="true",inferSchema=True,delimiter=',').load(s3_process_uri)


# city-temperature table:
# city-temp table:
s3_prefix = "db_temperature_by_city"
s3_table = "temperature_table"
temp_city_df = spark.read.format('csv').options(header="true",inferSchema=True,delimiter=',').load(s3_process_uri)

# city table:
s3_table = "city_table"
city_df = spark.read.format('csv').options(header="true",inferSchema=True,delimiter=',').load(s3_process_uri)

# global temperature table:
s3_prefix = "db_temperature_global"
s3_table = "global_temperature_table"
global_temp_df = spark.read.format('csv').options(header="true",inferSchema=True,delimiter=',').load(s3_process_uri)
