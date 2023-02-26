from sqlalchemy import create_engine
import pymysql
import sys

username = sys.argv[1]
password = sys.argv[2]
city_host = sys.argv[3][0:-5]
country_host = sys.argv[4][0:-5]
global_host = sys.argv[5][0:-5]

# This is all revoked before I push it into my Github

# The meta data for Major City Table:
city_config = {
    "host": city_host,
    "user": username,
    "password": password,
    "port": 3306,
    "charset": "utf8mb4",
    "use_unicode": False,
}
conn = pymysql.connect(**city_config)
with conn.cursor() as cursor:
    cursor.execute("show databases like 'db_temperature_by_city';")
    if not cursor.fetchone():
        cursor.execute("create database db_temperature_by_city;")
conn.close()
city_engine = create_engine(
    "mysql+pymysql://{}:{}@{}:3306/{}?charset=utf8mb4".format(
        city_config["user"],
        city_config["password"],
        city_config["host"],
        "db_temperature_by_city",
    )
)
# The meta data for Country Table:
country_config = {
    "host": country_host,
    "user": username,
    "password": password,
    "port": 3306,
    "charset": "utf8mb4",
    "use_unicode": False,
}
conn = pymysql.connect(**country_config)
with conn.cursor() as cursor:
    cursor.execute("show databases like 'db_temperature_by_country';")
    if not cursor.fetchone():
        cursor.execute("create database db_temperature_by_country;")
conn.close()
country_engine = create_engine(
    "mysql+pymysql://{}:{}@{}/{}?charset=utf8mb4".format(
        country_config["user"],
        country_config["password"],
        country_config["host"],
        "db_temperature_by_country",
    )
)

# The metat data for Global Table:
global_config = {
    "host": global_host,
    "user": username,
    "password": password,
    "port": 3306,
    "charset": "utf8mb4",
    "use_unicode": False,
}
conn = pymysql.connect(**global_config)
with conn.cursor() as cursor:
    cursor.execute("show databases like 'db_temperature_global';")
    if not cursor.fetchone():
        cursor.execute("create database db_temperature_global;")
conn.close()
global_engine = create_engine(
    "mysql+pymysql://{}:{}@{}/{}?charset=utf8mb4".format(
        global_config["user"],
        global_config["password"],
        global_config["host"],
        "db_temperature_global",
    )
)
