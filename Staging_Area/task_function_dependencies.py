from Data_Sources.Database_env import city_engine,country_engine,global_engine
import pandas

def load_city_temperature():
    temperature_df = pandas.read_sql(sql="select * from city_table",con=city_engine)
    city_df = pandas.read_sql(sql="select * from temperature_table", con=city_engine)
    temperature_df.to_csv("s3://temperature-project-bucket/city_temp/temperature_city.csv",index=False)
    city_df.to_csv("s3://temperature-project-bucket/city_temp/city.csv",index=False)

def load_country_temperature():
    country_temp_df = pandas.read_sql(sql="select * from temperature_country_table",con= country_engine)
    country_temp_df.to_csv("s3://temperature-project-bucket/country_temp/temperature_country.csv",index= False)

def load_global_temperature():
    global_temp_df = pandas.read_sql(sql="select * from global_temperature_table",con=global_engine)
    global_temp_df.to_csv("s3://temperature-project-bucket/global_temp/global_temperature.csv",index=False)