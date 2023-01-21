from sqlalchemy import create_engine
import pymysql

# This is all revoked before I push it into my Github

# The meta data for Major City Table:
city_config = {
    "host": "db-temperature-by-city.ca0hkxtpao0l.ap-northeast-1.rds.amazonaws.com",
    "user": "admin",
    "password": "12345678",
    "port": 3306,
    "charset": "utf8mb4",
    "use_unicode": False
}
conn = pymysql.connect(**city_config)
with conn.cursor() as cursor:
    cursor.execute("show databases like 'db_temperature_by_city';")
    if not cursor.fetchone():
        cursor.execute("create database db_temperature_by_city;")
conn.close()
city_engine = create_engine("mysql+pymysql://{}:{}@{}:3306/{}?charset=utf8mb4"
            .format(city_config["user"],city_config["password"],city_config["host"],"db_temperature_by_city"))
# The meta data for Country Table:
country_config = {
    "host": "db-temperature-by-country.ca0hkxtpao0l.ap-northeast-1.rds.amazonaws.com",
    "user": "admin",
    "password": "12345678",
    "port": 3306,
    "charset": "utf8mb4",
    "use_unicode": False
}
conn = pymysql.connect(**country_config)
with conn.cursor() as cursor:
    cursor.execute("show databases like 'db_temperature_by_country';")
    if not cursor.fetchone():   
        cursor.execute("create database db_temperature_by_country;")
conn.close()
country_engine = create_engine("mysql+pymysql://{}:{}@{}/{}?charset=utf8mb4"
            .format(country_config["user"],country_config["password"],country_config["host"],"db_temperature_by_country"))

# The metat data for Global Table:
global_config ={
    "host": "db-temperature-global.ca0hkxtpao0l.ap-northeast-1.rds.amazonaws.com",
    "user": "admin",
    "password": "12345678",
    "port": 3306,
    "charset": "utf8mb4",
    "use_unicode": False
}
conn = pymysql.connect(**global_config)
with conn.cursor() as cursor:
    cursor.execute("show databases like 'db_temperature_global';")
    if not cursor.fetchone():
        cursor.execute("create database db_temperature_global;")
conn.close()
global_engine = create_engine("mysql+pymysql://{}:{}@{}/{}?charset=utf8mb4"
            .format(global_config["user"],global_config["password"],global_config["host"],"db_temperature_global"))
