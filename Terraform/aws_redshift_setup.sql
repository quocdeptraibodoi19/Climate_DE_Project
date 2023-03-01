CREATE SCHEMA climate_etl_schema;

CREATE TABLE climate_etl_schema.city_detail_dimension_table (
    city_temperature_detail_id integer NOT NULL ENCODE az64
    distkey
,
        countryid integer ENCODE az64,
        cityid integer ENCODE az64,
        averagetemperature real ENCODE raw,
        averagetemperatureuncertainty real ENCODE raw,
        PRIMARY KEY (city_temperature_detail_id)
) DISTSTYLE AUTO;

CREATE TABLE climate_etl_schema.city_dimension_table (
    cityid integer ENCODE az64,
    city character varying(256) ENCODE lzo,
    latitude character varying(100) ENCODE lzo,
    longitude character varying(100) ENCODE lzo
) DISTSTYLE AUTO;

CREATE TABLE climate_etl_schema.country_detail_dimension_table (
    country_temperature_detail_id integer NOT NULL ENCODE raw
    distkey
,
        countryid integer ENCODE az64,
        averagetemperature real ENCODE raw,
        averagetemperatureuncertainty real ENCODE raw,
        PRIMARY KEY (country_temperature_detail_id)
) DISTSTYLE AUTO
SORTKEY
    (country_temperature_detail_id);

CREATE TABLE climate_etl_schema.country_dimension_table (
    countryid integer NOT NULL ENCODE az64,
    country character varying(256) ENCODE lzo,
    country_format_holistics character varying(256) ENCODE lzo,
    PRIMARY KEY (countryid)
) DISTSTYLE AUTO;

CREATE TABLE climate_etl_schema.global_detail_dimension_table (
    global_temperature_detail_id integer NOT NULL ENCODE az64,
    landaveragetemperature real ENCODE raw,
    landaveragetemperatureuncertainty real ENCODE raw,
    landmaxtemperature real ENCODE raw,
    landmaxtemperatureuncertainty real ENCODE raw,
    landmintemperature real ENCODE raw,
    landmintemperatureuncertainty real ENCODE raw,
    landandoceanaveragetemperature real ENCODE raw,
    landandoceanaveragetemperatureuncertainty real ENCODE raw,
    PRIMARY KEY (global_temperature_detail_id)
) DISTSTYLE AUTO;

CREATE TABLE climate_etl_schema.temperature_fact_table (
    temp_id integer NOT NULL identity(1, 1) ENCODE az64
    distkey
,
        dt timestamp without time zone NOT NULL ENCODE az64,
        country_temperature_detail_id integer ENCODE az64,
        city_temperature_detail_id integer ENCODE az64,
        global_temperature_detail_id integer ENCODE az64,
        PRIMARY KEY (temp_id)
) DISTSTYLE AUTO;