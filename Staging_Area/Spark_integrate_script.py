import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    when,
    avg,
    round,
    current_timestamp,
    expr,
    monotonically_increasing_id,
)
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

temp_country_df = (
    spark.read.format("csv")
    .options(header="true", inferSchema=True, delimiter=",")
    .load(s3_process_uri)
)

# city-temperature table:
# city-temp table:
s3_prefix = "db_temperature_by_city"
s3_table = "temperature_table"
temp_city_df = (
    spark.read.format("csv")
    .options(header="true", inferSchema=True, delimiter=",")
    .load(s3_process_uri)
)

# city table:
s3_table = "city_table"
city_df = (
    spark.read.format("csv")
    .options(header="true", inferSchema=True, delimiter=",")
    .load(s3_process_uri)
)

# global temperature table:
s3_prefix = "db_temperature_global"
s3_table = "global_temperature_table"
global_temp_df = (
    spark.read.format("csv")
    .options(header="true", inferSchema=True, delimiter=",")
    .load(s3_process_uri)
)

# Structure the Country Dimension Table: country_df
country_temp_city_df = temp_city_df.select("country")
country_temp_country_df = temp_country_df.select("country")
try:
    country_dimension_log_df = (
        spark.read.format("csv")
        .options(header="true", inferSchema=True, delimiter=",")
        .load(s3_integrate_uri + "country_dimension_log")
    )
    last_id = country_dimension_log_df.tail(1)[0]["LastCountryId"]
except:
    last_id = 0
    log_schema = StructType(
        [
            StructField("CountryId", IntegerType()),
            StructField("data_process", TimestampType()),
        ]
    )
    country_dimension_log_df = spark.createDataFrame([], schema=log_schema)

country_df = (
    country_temp_city_df.union(country_temp_country_df)
    .dropDuplicates()
    .withColumn("CountryId", last_id + monotonically_increasing_id())
)
last_id = country_df.tail(1)[0]["CountryId"]
last_id_rdd = spark.createDataFrame(
    Row(LastCountryId=last_id + 1, date_process=current_timestamp())
)
country_dimension_log_df = country_dimension_log_df.union(last_id_rdd)
country_dimension_log_df.write.format("csv").options(header="true", delimiter=",").mode(
    "overwrite"
).save(s3_integrate_uri + "country_dimension_log")


# Structure Country Detail Dimension Table: country_detail_df
temp_country_df = temp_country_df.join(country_df, "country", "inner")
temp_country_df.drop("country")
try:
    country_detail_dimension_log_df = (
        spark.read.format("csv")
        .options(header="true", inferSchema=True, delimiter=",")
        .load(s3_integrate_uri + "country_detail_dimension_log")
    )
    last_id = country_detail_dimension_log_df.tail(1)[0][
        "Last_Country_Temperature_Detail_Id"
    ]
except:
    last_id = 0
    log_schema = StructType(
        [
            StructField("Last_Country_Temperature_Detail_Id", IntegerType()),
            StructField("data_process", TimestampType()),
        ]
    )
    country_detail_dimension_log_df = spark.createDataFrame([], schema=log_schema)

country_detail_df = temp_country_df.withColumn(
    "Country_Temperature_Detail_Id", last_id + monotonically_increasing_id()
)
last_id = country_detail_df.tail(1)[0]["Country_Temperature_Detail_Id"]
last_id_rdd = spark.createDataFrame(
    Row(
        Last_Country_Temperature_Detail_Id=last_id + 1, date_process=current_timestamp()
    )
)
country_detail_dimension_log_df = country_detail_dimension_log_df.union(last_id_rdd)
country_detail_dimension_log_df.write.format("csv").options(
    header="true", delimiter=","
).mode("overwrite").save(s3_integrate_uri + "country_detail_dimension_log")

# Structure City Detail Dimension Table: city_detail_df
temp_city_df = temp_city_df.join(country_df, "country", "inner")
temp_city_df.drop("country")
try:
    city_detail_dimension_log_df = (
        spark.read.format("csv")
        .options(header="true", inferSchema=True, delimiter=",")
        .load(s3_integrate_uri + "city_detail_dimension_log")
    )
    last_id = city_detail_dimension_log_df.tail(1)[0]["Last_City_Temperature_Detail_Id"]
except:
    last_id = 0
    log_schema = StructType(
        [
            StructField("Last_City_Temperature_Detail_Id", IntegerType()),
            StructField("data_process", TimestampType()),
        ]
    )
    city_detail_dimension_log_df = spark.createDataFrame([], schema=log_schema)

city_detail_df = temp_city_df.withColumn(
    "City_Temperature_Detail_Id", last_id + monotonically_increasing_id()
)
last_id = city_detail_df.tail(1)[0]["City_Temperature_Detail_Id"]
last_id_rdd = spark.createDataFrame(
    Row(Last_City_Temperature_Detail_Id=last_id + 1, date_process=current_timestamp())
)
city_detail_dimension_log_df = city_detail_dimension_log_df.union(last_id_rdd)
city_detail_dimension_log_df.write.format("csv").options(
    header="true", delimiter=","
).mode("overwrite").save(s3_integrate_uri + "city_detail_dimension_log")

# Construct Global Detail Dimension Table: global_detail_df
try:
    global_detail_dimension_log_df = (
        spark.read.format("csv")
        .options(header="true", inferSchema=True, delimiter=",")
        .load(s3_integrate_uri + "global_detail_dimension_log")
    )
    last_id = global_detail_dimension_log_df.tail(1)[0][
        "Last_Global_Temperature_Detail_Id"
    ]
except:
    last_id = 0
    log_schema = StructType(
        [
            StructField("Last_Global_Temperature_Detail_Id", IntegerType()),
            StructField("data_process", TimestampType()),
        ]
    )
    global_detail_dimension_log_df = spark.createDataFrame([], schema=log_schema)

global_detail_df = global_temp_df.withColumn(
    "Global_Temperature_Detail_Id", last_id + monotonically_increasing_id()
)
last_id = global_detail_df.tail(1)[0]["Global_Temperature_Detail_Id"]
last_id_rdd = spark.createDataFrame(
    Row(Last_Global_Temperature_Detail_Id=last_id + 1, date_process=current_timestamp())
)
global_detail_dimension_log_df = global_detail_dimension_log_df.union(last_id_rdd)
global_detail_dimension_log_df.write.format("csv").options(
    header="true", delimiter=","
).mode("overwrite").save(s3_integrate_uri + "global_detail_dimension_log")

# Construct Temperature Fact Table
# We construct the Fact Table by joining all the dimension tables above.
# This sounds to be not optimized at the first glance.
# However, it's good for the stakeholders since it is better for analytics.
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
temp_fact_df = temp_fact_df.join(
    city_detail_df, ["dt", "CountryId"], "fulloutter"
).drop("CountryId", "CityId", "AverageTemperature", "AverageTemperatureUncertainty")
