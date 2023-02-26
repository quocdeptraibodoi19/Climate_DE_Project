import pandas
from Database_env import city_engine, country_engine, global_engine

# This is to set up the external data sources for the data pipeline (used for the simulation)

# This is to read data from csv file into a dataframe
tempbycountry_dataframe = pandas.read_csv(
    filepath_or_buffer="./Data_Sources/GlobalLandTemperaturesByCountry.csv"
)
tempbycity_dataframe = pandas.read_csv(
    filepath_or_buffer="./Data_Sources/GlobalLandTemperaturesByMajorCity.csv"
)
globaltemp_dataframe = pandas.read_csv(
    filepath_or_buffer="./Data_Sources/GlobalTemperatures.csv"
)

# Denormalizing the GlobalTemperatureByMajorCity
city_table_df = tempbycity_dataframe[["City", "Country", "Latitude", "Longitude"]]
city_table_df.drop_duplicates(
    subset=["City", "Country"], inplace=True, ignore_index=True
)
city_table_df["CityId"] = city_table_df.index
temperature_df = pandas.merge(
    left=tempbycity_dataframe, right=city_table_df, on=["City", "Country"], how="inner"
)
temperature_df = temperature_df[
    ["dt", "AverageTemperature", "AverageTemperatureUncertainty", "CityId"]
]

city_table_df.to_sql(
    name="city_table", con=city_engine, if_exists="replace", index=False
)
temperature_df.to_sql(
    name="temperature_table", con=city_engine, if_exists="replace", index=True
)

tempbycountry_dataframe.to_sql(
    name="temperature_country_table",
    con=country_engine,
    if_exists="replace",
    index=True,
)

globaltemp_dataframe.to_sql(
    name="global_temperature_table", con=global_engine, if_exists="replace", index=False
)
