import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, monotonically_increasing_id
from pyspark.sql.types import (
    StructField,
    StructType,
    IntegerType,
    TimestampType,
    Row,
)
from pyspark import SparkConf, SparkContext

spark = SparkSession(SparkContext(conf=SparkConf()).getOrCreate())

s3_table = ""
s3_bucket = "temperature-project-bucket"
s3_prefix = ""

s3_process_uri = "s3a://" + s3_bucket + "/" + s3_prefix + "/" + "preprocess_" + s3_table
s3_integrate_uri = "s3a://" + s3_bucket + "/integrate/"
# This script is used to intergrate data into a single one.

# country table:
s3_prefix = "db_temperature_by_country"
s3_table = "temperature_country_table"
s3_process_uri = "s3a://" + s3_bucket + "/" + s3_prefix + "/" + "preprocess_" + s3_table
# Country index dt AverageTemperature AverageTemperatureUncertainty dated_ingest
temp_country_df = (
    spark.read.format("csv")
    .options(header="true", inferSchema=True, delimiter=",")
    .load(s3_process_uri)
)

# city-temperature table:
# city-temp table:
# CityId index dt AverageTemperature AverageTemperatureUncertainty dated_ingest
s3_prefix = "db_temperature_by_city"
s3_table = "temperature_table"
s3_process_uri = "s3a://" + s3_bucket + "/" + s3_prefix + "/" + "preprocess_" + s3_table

temp_city_df = (
    spark.read.format("csv")
    .options(header="true", inferSchema=True, delimiter=",")
    .load(s3_process_uri)
)

# city table:
# City Country Latitude Longitude CityId
s3_table = "city_table"
s3_process_uri = "s3a://" + s3_bucket + "/" + s3_prefix + "/" + "preprocess_" + s3_table

city_df = (
    spark.read.format("csv")
    .options(header="true", inferSchema=True, delimiter=",")
    .load(s3_process_uri)
)

# global temperature table:
# dt LandAverageTemperature LandMaxTemperature ... dated_ingest
s3_prefix = "db_temperature_global"
s3_table = "global_temperature_table"
s3_process_uri = "s3a://" + s3_bucket + "/" + s3_prefix + "/" + "preprocess_" + s3_table

global_temp_df = (
    spark.read.format("csv")
    .options(header="true", inferSchema=True, delimiter=",")
    .load(s3_process_uri)
)

# Structure the Country Dimension Table: country_df
country_temp_city_df = city_df.select("country")
country_temp_country_df = temp_country_df.select("country")
try:
    last_id = (
        spark.read.format("csv")
        .options(header="true", inferSchema=True, delimiter=",")
        .load(s3_integrate_uri + "country_dimension_log")
        .tail(1)[0]["LastCountryId"]
    )
except:
    last_id = 0
country_df = (
    country_temp_city_df.union(country_temp_country_df)
    .dropDuplicates()
    .withColumn("CountryId", last_id + monotonically_increasing_id())
)
if not country_df.isEmpty():
    log_schema = StructType(
        [
            StructField("LastCountryId", IntegerType()),
        ]
    )
    last_id = country_df.tail(1)[0]["CountryId"]
    country_dimension_log_df = spark.createDataFrame(
        [Row(LastCountryId=last_id + 1)],
        schema=log_schema,
    ).withColumn("date_process", current_timestamp())
    country_dimension_log_df.write.format("csv").options(
        header="true", delimiter=","
    ).mode("append").save(s3_integrate_uri + "country_dimension_log")

# Structure Country Detail Dimension Table: country_detail_df
country_detail_df = temp_country_df
country_detail_df = country_detail_df.join(country_df, "country", "inner")
country_detail_df = country_detail_df.drop("country", "dated_ingest").withColumnRenamed(
    "index", "Country_Temperature_Detail_Id"
)
# try:
#     country_detail_dimension_log_df = (
#         spark.read.format("csv")
#         .options(header="true", inferSchema=True, delimiter=",")
#         .load(s3_integrate_uri + "country_detail_dimension_log")
#     )
#     last_id = country_detail_dimension_log_df.tail(1)[0][
#         "Last_Country_Temperature_Detail_Id"
#     ]
# except:
#     last_id = 0
#     log_schema = StructType(
#         [
#             StructField("Last_Country_Temperature_Detail_Id", IntegerType()),
#             StructField("data_process", TimestampType()),
#         ]
#     )
#     country_detail_dimension_log_df = spark.createDataFrame([], schema=log_schema)

# country_detail_df = temp_country_df.withColumn(
#     "Country_Temperature_Detail_Id", last_id + monotonically_increasing_id()
# )
# last_id = country_detail_df.tail(1)[0]["Country_Temperature_Detail_Id"]
# schema = StructType(
#     [
#         StructField("Last_Country_Temperature_Detail_Id", IntegerType()),
#         StructField("date_process", TimestampType()),
#     ]
# )
# last_id_rdd = spark.createDataFrame(
#     Row(
#         Last_Country_Temperature_Detail_Id=lit(last_id + 1),
#         date_process=current_timestamp(),
#     ),
#     schema=schema,
# )
# country_detail_dimension_log_df = country_detail_dimension_log_df.union(last_id_rdd)
# country_detail_dimension_log_df.write.format("csv").options(
#     header="true", delimiter=","
# ).mode("overwrite").save(s3_integrate_uri + "country_detail_dimension_log")

# Structure City Detail Dimension Table: city_detail_df
# CityId index dt AverageTemperature AverageTemperatureUncertainty dated_ingest
# City Country Latitude Longitude CityId
city_detail_df = temp_city_df
city_detail_df = (
    city_detail_df.join(city_df, "CityId", "inner")
    .drop("city", "longitude", "latitude", "dated_ingest")
    .join(country_df, "country", "inner")
    .drop("country")
    .withColumnRenamed("index", "City_Temperature_Detail_Id")
)
# temp_city_df.drop("country")
# try:
#     city_detail_dimension_log_df = (
#         spark.read.format("csv")
#         .options(header="true", inferSchema=True, delimiter=",")
#         .load(s3_integrate_uri + "city_detail_dimension_log")
#     )
#     last_id = city_detail_dimension_log_df.tail(1)[0]["Last_City_Temperature_Detail_Id"]
# except:
#     last_id = 0
#     log_schema = StructType(
#         [
#             StructField("Last_City_Temperature_Detail_Id", IntegerType()),
#             StructField("data_process", TimestampType()),
#         ]
#     )
#     city_detail_dimension_log_df = spark.createDataFrame([], schema=log_schema)

# city_detail_df = temp_city_df.withColumn(
#     "City_Temperature_Detail_Id", last_id + monotonically_increasing_id()
# )
# last_id = city_detail_df.tail(1)[0]["City_Temperature_Detail_Id"]
# schema = StructType(
#     [
#         StructField("Last_City_Temperature_Detail_Id", IntegerType()),
#         StructField("date_process", TimestampType()),
#     ]
# )
# last_id_rdd = spark.createDataFrame(
#     Row(
#         Last_City_Temperature_Detail_Id=lit(last_id + 1),
#         date_process=current_timestamp(),
#     ),
#     schema=schema,
# )
# city_detail_dimension_log_df = city_detail_dimension_log_df.union(last_id_rdd)
# city_detail_dimension_log_df.write.format("csv").options(
#     header="true", delimiter=","
# ).mode("overwrite").save(s3_integrate_uri + "city_detail_dimension_log")

# Structure City Dimension Table: city_df
city_df = city_df.drop("country")

# Construct Global Detail Dimension Table: global_detail_df
try:
    last_id = (
        spark.read.format("csv")
        .options(header="true", inferSchema=True, delimiter=",")
        .load(s3_integrate_uri + "global_detail_dimension_log")
        .tail(1)[0]["Last_Global_Temperature_Detail_Id"]
    )
except:
    last_id = 0
global_detail_df = global_temp_df.withColumn(
    "Global_Temperature_Detail_Id", last_id + monotonically_increasing_id()
).drop("dated_ingest")
if not global_detail_df.isEmpty():
    log_schema = StructType(
        [
            StructField("Last_Global_Temperature_Detail_Id", IntegerType()),
        ]
    )
    last_id = global_detail_df.tail(1)[0]["Global_Temperature_Detail_Id"]
    global_detail_dimension_log_df = spark.createDataFrame(
        [
            Row(
                Last_Global_Temperature_Detail_Id=last_id + 1,
            )
        ],
        schema=log_schema,
    ).withColumn("date_process", current_timestamp())
    global_detail_dimension_log_df.write.format("csv").options(
        header="true", delimiter=","
    ).mode("append").save(s3_integrate_uri + "global_detail_dimension_log")

# Construct Temperature Fact Table
# We construct the Fact Table by joining all the dimension tables above.
# This sounds to be not optimized at the first glance.
# However, it's good for the stakeholders since it is better for analytics.
# Why I don't specify the temp_id here, because I have gone for the option requiring the redshift to 
# automatically incrementally update the id when inserting new row
# Why the above I don't do that (after the construction of a particular table, we can write it to redshift 
# and then we can read it out from redshift as we need) ?
# The awnser is that I don't like this way so I didn't do like that :))
# Cause with this way of implementation, I can study a lot since it gives me more opportunity to get my hands dirty
# in the process of directing the data flow like how to temporarily cache the data in the file log in the s3 or stuff like that
# and then I will end up being much better.
temp_fact_df = (
    country_detail_df.drop("AverageTemperature", "AverageTemperatureUncertainty")
    .join(global_detail_df, "dt", "fullouter")
    .drop(
        "LandAverageTemperature",
        "LandAverageTemperatureUncertainty",
        "LandMaxTemperature",
        "LandMaxTemperatureUncertainty",
        "LandMinTemperature",
        "LandMinTemperatureUncertainty",
        "LandAndOceanAverageTemperature",
        "LandAndOceanAverageTemperatureUncertainty",
    )
)
temp_fact_df = temp_fact_df.join(city_detail_df, ["dt", "CountryId"], "fullouter").drop(
    "CountryId", "CityId", "AverageTemperature", "AverageTemperatureUncertainty"
)
# Load data into the data warehouse (AWS RedShift)
jdbcUrl = "jdbc:redshift://redshift-cluster-climate.c7e35csdqriw.ap-northeast-1.redshift.amazonaws.com:5439/climate-temperature-db"
connection_properties = {
    "user": os.getenv("AWS_REDSHIFT_USER"),
    "password": os.getenv("AWS_REDSHIFT_PASS"),
    "driver": "com.amazon.redshift.jdbc42.Driver",
}
schema = "climate_etl_schema"
country_df.write.jdbc(
    url=jdbcUrl,
    table=schema + ".country_dimension_table",
    mode="append",
    properties=connection_properties,
)
city_df.write.jdbc(
    url=jdbcUrl,
    table=schema + ".city_dimension_table",
    mode="append",    
    properties=connection_properties,
)

city_detail_df.write.jdbc(
    url=jdbcUrl,
    table=schema + ".city_detail_dimension_table",
    mode="append",
    properties=connection_properties,
)

global_detail_df.write.jdbc(
    url=jdbcUrl,
    table=schema + ".global_detail_dimension_table",
    mode="append",
    properties=connection_properties,
)
temp_fact_df.write.jdbc(
    url=jdbcUrl,
    table=schema + ".temperature_fact_table",
    mode="append",
    properties=connection_properties,
)
