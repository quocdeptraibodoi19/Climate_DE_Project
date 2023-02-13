import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import when, avg, round, current_timestamp
from pyspark.sql.types import (
    StructField,
    StructType,
    IntegerType,
    TimestampType,
    DoubleType,
    StringType,
    Row,
)
from pyspark import SparkConf, SparkContext

s3_table = sys.argv[1]
s3_bucket = sys.argv[2]
s3_prefix = sys.argv[3]

# Declare the spark session
spark = SparkSession(SparkContext(conf=SparkConf()).getOrCreate())

# Read data from data landing zone
s3_uri = "s3a://" + s3_bucket + "/" + s3_prefix + "/" + s3_table + ".csv"
s3_process_uri = "s3a://" + s3_bucket + "/" + s3_prefix + "/" + "preprocess_" + s3_table
s3_log_uri = "s3a://" + s3_bucket + "/" + s3_prefix + "/" + "log.csv"

if s3_table == "temperature_country_table":
    # This is to handle the missing value of the columns
    schema = StructType(
        [
            StructField("index", IntegerType(), False),
            StructField("dt", TimestampType(), False),
            StructField("AverageTemperature", DoubleType(), True),
            StructField("AverageTemperatureUncertainty", DoubleType(), True),
            StructField("Country", StringType(), False),
            StructField("dated_ingest", TimestampType(), False),
        ]
    )
    log_schema = StructType([StructField("index", IntegerType(), False)])
    s3_sdf = (
        spark.read.format("csv")
        .options(header="true", mode="DROPMALFORMED", delimiter=",")
        .schema(schema)
        .load(s3_uri)
    )

    # Handle the preprocessing log for the incremental processing process
    log_sdf = (
        spark.read.format("csv")
        .options(header="true", delimiter=",")
        .schema(log_schema)
        .load(s3_log_uri)
    )
    process_index_arr = log_sdf.tail(2)
    if len(process_index_arr) == 2:
        process_index = process_index_arr[0]["index"]
        s3_sdf = s3_sdf.filter(s3_sdf["index"] >= process_index)
        
    s3_sdf = s3_sdf.fillna(0, ["AverageTemperatureUncertainty"])
    mean_sdf = s3_sdf.groupBy("Country").agg(
        avg("AverageTemperature").alias("meanTempbyCountry")
    )
    joined_sdf = s3_sdf.join(mean_sdf, ["Country"], "inner")
    filled_sdf = joined_sdf.withColumn(
        "AverageTemperature",
        when(
            joined_sdf["AverageTemperature"].isNull(), joined_sdf["meanTempbyCountry"]
        ).otherwise(joined_sdf["AverageTemperature"]),
    )
    filled_sdf = filled_sdf.drop("meanTempbyCountry")
    filled_sdf = filled_sdf.withColumn(
        "AverageTemperature", round("AverageTemperature", 3)
    )
    filled_sdf = filled_sdf.withColumn(
        "AverageTemperatureUncertainty", round("AverageTemperatureUncertainty", 3)
    )
    filled_sdf.write.format("csv").options(header="true", delimiter=",").mode(
        "overwrite"
    ).save(s3_process_uri)

elif s3_table == "temperature_table":
    # This is to handle the missing value of the columns
    schema = StructType(
        [
            StructField("index", IntegerType(), False),
            StructField("dt", TimestampType(), False),
            StructField("AverageTemperature", DoubleType(), True),
            StructField("AverageTemperatureUncertainty", DoubleType(), True),
            StructField("CityId", IntegerType(), False),
            StructField("dated_ingest", TimestampType(), False),
        ]
    )
    log_schema = StructType([StructField("index", IntegerType(), False)])
    s3_sdf = (
        spark.read.format("csv")
        .options(header="true", mode="DROPMALFORMED", delimiter=",")
        .schema(schema)
        .load(s3_uri)
    )

    log_sdf = (
        spark.read.format("csv")
        .options(header="true", delimiter=",")
        .schema(log_schema)
        .load(s3_log_uri)
    )
    process_index_arr = log_sdf.tail(2)
    if len(process_index_arr) == 2:
        process_index = process_index_arr[0]["index"]
        s3_sdf = s3_sdf.filter(s3_sdf["index"] >= process_index)

    s3_sdf = s3_sdf.fillna(0, ["AverageTemperatureUncertainty"])
    mean_sdf = s3_sdf.groupBy("CityId").agg(
        avg("AverageTemperature").alias("meanTempbyCity")
    )
    joined_sdf = s3_sdf.join(mean_sdf, ["CityId"], "inner")
    filled_sdf = joined_sdf.withColumn(
        "AverageTemperature",
        when(
            joined_sdf["AverageTemperature"].isNull(), joined_sdf["meanTempbyCity"]
        ).otherwise(joined_sdf["AverageTemperature"]),
    )
    filled_sdf = filled_sdf.drop("meanTempbyCity")
    filled_sdf = filled_sdf.withColumn(
        "AverageTemperature", round("AverageTemperature", 3)
    )
    filled_sdf = filled_sdf.withColumn(
        "AverageTemperatureUncertainty", round("AverageTemperatureUncertainty", 3)
    )
    filled_sdf.write.format("csv").options(header="true", delimiter=",").mode(
        "overwrite"
    ).save(s3_process_uri)

elif s3_table == "global_temperature_table":
    # This is to handle the missing value of the columns
    schema = StructType(
        [
            StructField("dt", TimestampType(), False),
            StructField("LandAverageTemperature", DoubleType(), True),
            StructField("LandAverageTemperatureUncertainty", DoubleType(), True),
            StructField("LandMaxTemperature", DoubleType(), True),
            StructField("LandMaxTemperatureUncertainty", DoubleType(), True),
            StructField("LandMinTemperature", DoubleType(), True),
            StructField("LandMinTemperatureUncertainty", DoubleType(), True),
            StructField("LandAndOceanAverageTemperature", DoubleType(), True),
            StructField(
                "LandAndOceanAverageTemperatureUncertainty", DoubleType(), True
            ),
            StructField("dated_ingest", TimestampType(), True),
        ]
    )
    log_schema = StructType([StructField("index", TimestampType(), False)])
    s3_sdf = (
        spark.read.format("csv")
        .options(header="true", mode="DROPMALFORMED", delimiter=",")
        .schema(schema)
        .load(s3_uri)
    )

    log_sdf = (
        spark.read.format("csv")
        .options(header="true", delimiter=",")
        .schema(log_schema)
        .load(s3_log_uri)
    )
    process_index_arr = log_sdf.tail(2)
    if len(process_index_arr) == 2:
        process_index = process_index_arr[0]["index"]
        s3_sdf = s3_sdf.filter(s3_sdf["dt"] >= process_index)

    s3_sdf = s3_sdf.fillna(
        0,
        [
            "LandMaxTemperatureUncertainty",
            "LandMinTemperatureUncertainty",
            "LandAndOceanAverageTemperatureUncertainty",
            "LandAverageTemperatureUncertainty",
        ],
    )
    from pyspark.ml.feature import Imputer

    imputer = Imputer(
        inputCols=[
            "LandAverageTemperature",
            "LandMaxTemperature",
            "LandMinTemperature",
            "LandAndOceanAverageTemperature",
        ],
        outputCols=[
            "LandAverageTemperature",
            "LandMaxTemperature",
            "LandMinTemperature",
            "LandAndOceanAverageTemperature",
        ],
    ).setStrategy("mean")
    filled_sdf = imputer.fit(s3_sdf).transform(s3_sdf)
    filled_sdf = filled_sdf.withColumn(
        "LandAverageTemperature", round("LandAverageTemperature", 3)
    )
    filled_sdf = filled_sdf.withColumn(
        "LandAverageTemperatureUncertainty",
        round("LandAverageTemperatureUncertainty", 3),
    )
    filled_sdf = filled_sdf.withColumn(
        "LandMaxTemperature", round("LandMaxTemperature", 3)
    )
    filled_sdf = filled_sdf.withColumn(
        "LandMaxTemperatureUncertainty", round("LandMaxTemperatureUncertainty", 3)
    )
    filled_sdf = filled_sdf.withColumn(
        "LandMinTemperature", round("LandMinTemperature", 3)
    )
    filled_sdf = filled_sdf.withColumn(
        "LandMinTemperatureUncertainty", round("LandMinTemperatureUncertainty", 3)
    )
    filled_sdf = filled_sdf.withColumn(
        "LandAndOceanAverageTemperature", round("LandAndOceanAverageTemperature", 3)
    )
    filled_sdf = filled_sdf.withColumn(
        "LandAndOceanAverageTemperatureUncertainty",
        round("LandAndOceanAverageTemperatureUncertainty", 3),
    )
    filled_sdf.write.format("csv").options(header="true", delimiter=",").mode(
        "overwrite"
    ).save(s3_process_uri)

elif s3_table == "city_table":
    # This is to validate data to make sure for the integrity
    schema = StructType(
        [
            StructField("City", StringType(), False),
            StructField("Country", StringType(), False),
            StructField("Latitude", StringType(), False),
            StructField("Longitude", StringType(), False),
            StructField("CityId", IntegerType(), False),
        ]
    )
    s3_sdf = (
        spark.read.format("csv")
        .options(header="true", mode="DROPMALFORMED", delimiter=",")
        .schema(schema)
        .load(s3_uri)
    )
    s3_sdf.write.format("csv").options(header="true", delimiter=",").mode(
        "overwrite"
    ).save(s3_process_uri)
