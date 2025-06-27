--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5 (Ubuntu 17.5-1.pgdg24.04+1)
-- Dumped by pg_dump version 17.5 (Ubuntu 17.5-1.pgdg24.04+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: update_timestamp(); Type: FUNCTION; Schema: public; Owner: sauron
--

CREATE FUNCTION public.update_timestamp() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.last_updated = NOW();
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_timestamp() OWNER TO sauron;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: openweather_forecast; Type: TABLE; Schema: public; Owner: sauron
--

CREATE TABLE public.openweather_forecast (
    id integer NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    lat double precision NOT NULL,
    lon double precision NOT NULL,
    day_1_dt timestamp with time zone,
    day_1_temp double precision,
    day_1_feels_like double precision,
    day_1_pressure integer,
    day_1_humidity integer,
    day_1_dew_point double precision,
    day_1_uvi double precision,
    day_1_clouds integer,
    day_1_vis double precision,
    day_1_wind_speed double precision,
    day_1_wind_deg integer,
    day_1_wind_gust double precision,
    day_1_main text,
    day_1_description text,
    day_2_dt timestamp with time zone,
    day_2_temp double precision,
    day_2_feels_like double precision,
    day_2_pressure integer,
    day_2_humidity integer,
    day_2_dew_point double precision,
    day_2_uvi double precision,
    day_2_clouds integer,
    day_2_vis double precision,
    day_2_wind_speed double precision,
    day_2_wind_deg integer,
    day_2_wind_gust double precision,
    day_2_main text,
    day_2_description text,
    day_3_dt timestamp with time zone,
    day_3_temp double precision,
    day_3_feels_like double precision,
    day_3_pressure integer,
    day_3_humidity integer,
    day_3_dew_point double precision,
    day_3_uvi double precision,
    day_3_clouds integer,
    day_3_vis double precision,
    day_3_wind_speed double precision,
    day_3_wind_deg integer,
    day_3_wind_gust double precision,
    day_3_main text,
    day_3_description text,
    day_4_dt timestamp with time zone,
    day_4_temp double precision,
    day_4_feels_like double precision,
    day_4_pressure integer,
    day_4_humidity integer,
    day_4_dew_point double precision,
    day_4_uvi double precision,
    day_4_clouds integer,
    day_4_vis double precision,
    day_4_wind_speed double precision,
    day_4_wind_deg integer,
    day_4_wind_gust double precision,
    day_4_main text,
    day_4_description text
);


ALTER TABLE public.openweather_forecast OWNER TO sauron;

--
-- Name: openweather_forecast_detail; Type: TABLE; Schema: public; Owner: sauron
--

CREATE TABLE public.openweather_forecast_detail (
    id integer NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    lat double precision NOT NULL,
    lon double precision NOT NULL,
    timezone text,
    timezone_offset integer,
    sunrise timestamp with time zone,
    sunset timestamp with time zone,
    current_temp double precision,
    current_feels_like double precision,
    current_pressure integer,
    current_humidity integer,
    current_dew_point double precision,
    current_uvi double precision,
    current_clouds integer,
    current_visibility integer,
    current_wind_speed double precision,
    current_wind_deg integer,
    current_wind_gust double precision,
    current_weather_main text,
    current_weather_description text,
    hourly_projected_precipitation double precision,
    hour_0_timestamptz timestamp with time zone,
    hour_0_temp double precision,
    hour_0_feels_like double precision,
    hour_0_pressure integer,
    hour_0_humidity integer,
    hour_0_dew_point double precision,
    hour_0_clouds integer,
    hour_0_visibility integer,
    hour_0_wind_speed double precision,
    hour_0_wind_deg integer,
    hour_0_wind_gust double precision,
    hour_0_weather_main text,
    hour_0_weather_description text,
    hour_0_pop double precision,
    hour_1_timestamptz timestamp with time zone,
    hour_1_temp double precision,
    hour_1_feels_like double precision,
    hour_1_pressure integer,
    hour_1_humidity integer,
    hour_1_dew_point double precision,
    hour_1_clouds integer,
    hour_1_visibility integer,
    hour_1_wind_speed double precision,
    hour_1_wind_deg integer,
    hour_1_wind_gust double precision,
    hour_1_weather_main text,
    hour_1_weather_description text,
    hour_1_pop double precision,
    hour_2_timestamptz timestamp with time zone,
    hour_2_temp double precision,
    hour_2_feels_like double precision,
    hour_2_pressure integer,
    hour_2_humidity integer,
    hour_2_dew_point double precision,
    hour_2_clouds integer,
    hour_2_visibility integer,
    hour_2_wind_speed double precision,
    hour_2_wind_deg integer,
    hour_2_wind_gust double precision,
    hour_2_weather_main text,
    hour_2_weather_description text,
    hour_2_pop double precision,
    hour_3_timestamptz timestamp with time zone,
    hour_3_temp double precision,
    hour_3_feels_like double precision,
    hour_3_pressure integer,
    hour_3_humidity integer,
    hour_3_dew_point double precision,
    hour_3_clouds integer,
    hour_3_visibility integer,
    hour_3_wind_speed double precision,
    hour_3_wind_deg integer,
    hour_3_wind_gust double precision,
    hour_3_weather_main text,
    hour_3_weather_description text,
    hour_3_pop double precision,
    hour_4_timestamptz timestamp with time zone,
    hour_4_temp double precision,
    hour_4_feels_like double precision,
    hour_4_pressure integer,
    hour_4_humidity integer,
    hour_4_dew_point double precision,
    hour_4_clouds integer,
    hour_4_visibility integer,
    hour_4_wind_speed double precision,
    hour_4_wind_deg integer,
    hour_4_wind_gust double precision,
    hour_4_weather_main text,
    hour_4_weather_description text,
    hour_4_pop double precision,
    hour_5_timestamptz timestamp with time zone,
    hour_5_temp double precision,
    hour_5_feels_like double precision,
    hour_5_pressure integer,
    hour_5_humidity integer,
    hour_5_dew_point double precision,
    hour_5_clouds integer,
    hour_5_visibility integer,
    hour_5_wind_speed double precision,
    hour_5_wind_deg integer,
    hour_5_wind_gust double precision,
    hour_5_weather_main text,
    hour_5_weather_description text,
    hour_5_pop double precision,
    hour_6_timestamptz timestamp with time zone,
    hour_6_temp double precision,
    hour_6_feels_like double precision,
    hour_6_pressure integer,
    hour_6_humidity integer,
    hour_6_dew_point double precision,
    hour_6_clouds integer,
    hour_6_visibility integer,
    hour_6_wind_speed double precision,
    hour_6_wind_deg integer,
    hour_6_wind_gust double precision,
    hour_6_weather_main text,
    hour_6_weather_description text,
    hour_6_pop double precision,
    hour_7_timestamptz timestamp with time zone,
    hour_7_temp double precision,
    hour_7_feels_like double precision,
    hour_7_pressure integer,
    hour_7_humidity integer,
    hour_7_dew_point double precision,
    hour_7_clouds integer,
    hour_7_visibility integer,
    hour_7_wind_speed double precision,
    hour_7_wind_deg integer,
    hour_7_wind_gust double precision,
    hour_7_weather_main text,
    hour_7_weather_description text,
    hour_7_pop double precision,
    hour_8_timestamptz timestamp with time zone,
    hour_8_temp double precision,
    hour_8_feels_like double precision,
    hour_8_pressure integer,
    hour_8_humidity integer,
    hour_8_dew_point double precision,
    hour_8_clouds integer,
    hour_8_visibility integer,
    hour_8_wind_speed double precision,
    hour_8_wind_deg integer,
    hour_8_wind_gust double precision,
    hour_8_weather_main text,
    hour_8_weather_description text,
    hour_8_pop double precision,
    hour_9_timestamptz timestamp with time zone,
    hour_9_temp double precision,
    hour_9_feels_like double precision,
    hour_9_pressure integer,
    hour_9_humidity integer,
    hour_9_dew_point double precision,
    hour_9_clouds integer,
    hour_9_visibility integer,
    hour_9_wind_speed double precision,
    hour_9_wind_deg integer,
    hour_9_wind_gust double precision,
    hour_9_weather_main text,
    hour_9_weather_description text,
    hour_9_pop double precision,
    hour_10_timestamptz timestamp with time zone,
    hour_10_temp double precision,
    hour_10_feels_like double precision,
    hour_10_pressure integer,
    hour_10_humidity integer,
    hour_10_dew_point double precision,
    hour_10_clouds integer,
    hour_10_visibility integer,
    hour_10_wind_speed double precision,
    hour_10_wind_deg integer,
    hour_10_wind_gust double precision,
    hour_10_weather_main text,
    hour_10_weather_description text,
    hour_10_pop double precision,
    hour_11_timestamptz timestamp with time zone,
    hour_11_temp double precision,
    hour_11_feels_like double precision,
    hour_11_pressure integer,
    hour_11_humidity integer,
    hour_11_dew_point double precision,
    hour_11_clouds integer,
    hour_11_visibility integer,
    hour_11_wind_speed double precision,
    hour_11_wind_deg integer,
    hour_11_wind_gust double precision,
    hour_11_weather_main text,
    hour_11_weather_description text,
    hour_11_pop double precision,
    hour_12_timestamptz timestamp with time zone,
    hour_12_temp double precision,
    hour_12_feels_like double precision,
    hour_12_pressure integer,
    hour_12_humidity integer,
    hour_12_dew_point double precision,
    hour_12_clouds integer,
    hour_12_visibility integer,
    hour_12_wind_speed double precision,
    hour_12_wind_deg integer,
    hour_12_wind_gust double precision,
    hour_12_weather_main text,
    hour_12_weather_description text,
    hour_12_pop double precision,
    hour_13_timestamptz timestamp with time zone,
    hour_13_temp double precision,
    hour_13_feels_like double precision,
    hour_13_pressure integer,
    hour_13_humidity integer,
    hour_13_dew_point double precision,
    hour_13_clouds integer,
    hour_13_visibility integer,
    hour_13_wind_speed double precision,
    hour_13_wind_deg integer,
    hour_13_wind_gust double precision,
    hour_13_weather_main text,
    hour_13_weather_description text,
    hour_13_pop double precision,
    hour_14_timestamptz timestamp with time zone,
    hour_14_temp double precision,
    hour_14_feels_like double precision,
    hour_14_pressure integer,
    hour_14_humidity integer,
    hour_14_dew_point double precision,
    hour_14_clouds integer,
    hour_14_visibility integer,
    hour_14_wind_speed double precision,
    hour_14_wind_deg integer,
    hour_14_wind_gust double precision,
    hour_14_weather_main text,
    hour_14_weather_description text,
    hour_14_pop double precision,
    hour_15_timestamptz timestamp with time zone,
    hour_15_temp double precision,
    hour_15_feels_like double precision,
    hour_15_pressure integer,
    hour_15_humidity integer,
    hour_15_dew_point double precision,
    hour_15_clouds integer,
    hour_15_visibility integer,
    hour_15_wind_speed double precision,
    hour_15_wind_deg integer,
    hour_15_wind_gust double precision,
    hour_15_weather_main text,
    hour_15_weather_description text,
    hour_15_pop double precision,
    hour_16_timestamptz timestamp with time zone,
    hour_16_temp double precision,
    hour_16_feels_like double precision,
    hour_16_pressure integer,
    hour_16_humidity integer,
    hour_16_dew_point double precision,
    hour_16_clouds integer,
    hour_16_visibility integer,
    hour_16_wind_speed double precision,
    hour_16_wind_deg integer,
    hour_16_wind_gust double precision,
    hour_16_weather_main text,
    hour_16_weather_description text,
    hour_16_pop double precision,
    hour_17_timestamptz timestamp with time zone,
    hour_17_temp double precision,
    hour_17_feels_like double precision,
    hour_17_pressure integer,
    hour_17_humidity integer,
    hour_17_dew_point double precision,
    hour_17_clouds integer,
    hour_17_visibility integer,
    hour_17_wind_speed double precision,
    hour_17_wind_deg integer,
    hour_17_wind_gust double precision,
    hour_17_weather_main text,
    hour_17_weather_description text,
    hour_17_pop double precision,
    hour_18_timestamptz timestamp with time zone,
    hour_18_temp double precision,
    hour_18_feels_like double precision,
    hour_18_pressure integer,
    hour_18_humidity integer,
    hour_18_dew_point double precision,
    hour_18_clouds integer,
    hour_18_visibility integer,
    hour_18_wind_speed double precision,
    hour_18_wind_deg integer,
    hour_18_wind_gust double precision,
    hour_18_weather_main text,
    hour_18_weather_description text,
    hour_18_pop double precision,
    hour_19_timestamptz timestamp with time zone,
    hour_19_temp double precision,
    hour_19_feels_like double precision,
    hour_19_pressure integer,
    hour_19_humidity integer,
    hour_19_dew_point double precision,
    hour_19_clouds integer,
    hour_19_visibility integer,
    hour_19_wind_speed double precision,
    hour_19_wind_deg integer,
    hour_19_wind_gust double precision,
    hour_19_weather_main text,
    hour_19_weather_description text,
    hour_19_pop double precision,
    hour_20_timestamptz timestamp with time zone,
    hour_20_temp double precision,
    hour_20_feels_like double precision,
    hour_20_pressure integer,
    hour_20_humidity integer,
    hour_20_dew_point double precision,
    hour_20_clouds integer,
    hour_20_visibility integer,
    hour_20_wind_speed double precision,
    hour_20_wind_deg integer,
    hour_20_wind_gust double precision,
    hour_20_weather_main text,
    hour_20_weather_description text,
    hour_20_pop double precision,
    hour_21_timestamptz timestamp with time zone,
    hour_21_temp double precision,
    hour_21_feels_like double precision,
    hour_21_pressure integer,
    hour_21_humidity integer,
    hour_21_dew_point double precision,
    hour_21_clouds integer,
    hour_21_visibility integer,
    hour_21_wind_speed double precision,
    hour_21_wind_deg integer,
    hour_21_wind_gust double precision,
    hour_21_weather_main text,
    hour_21_weather_description text,
    hour_21_pop double precision,
    hour_22_timestamptz timestamp with time zone,
    hour_22_temp double precision,
    hour_22_feels_like double precision,
    hour_22_pressure integer,
    hour_22_humidity integer,
    hour_22_dew_point double precision,
    hour_22_clouds integer,
    hour_22_visibility integer,
    hour_22_wind_speed double precision,
    hour_22_wind_deg integer,
    hour_22_wind_gust double precision,
    hour_22_weather_main text,
    hour_22_weather_description text,
    hour_22_pop double precision,
    hour_23_timestamptz timestamp with time zone,
    hour_23_temp double precision,
    hour_23_feels_like double precision,
    hour_23_pressure integer,
    hour_23_humidity integer,
    hour_23_dew_point double precision,
    hour_23_clouds integer,
    hour_23_visibility integer,
    hour_23_wind_speed double precision,
    hour_23_wind_deg integer,
    hour_23_wind_gust double precision,
    hour_23_weather_main text,
    hour_23_weather_description text,
    hour_23_pop double precision,
    day_0_timestamptz timestamp with time zone,
    day_0_summary text,
    day_0_temp_day double precision,
    day_0_temp_min double precision,
    day_0_temp_max double precision,
    day_0_temp_night double precision,
    day_0_temp_eve double precision,
    day_0_temp_morn double precision,
    day_0_feels_like_day double precision,
    day_0_feels_like_night double precision,
    day_0_feels_like_eve double precision,
    day_0_feels_like_morn double precision,
    day_0_pressure integer,
    day_0_humidity integer,
    day_0_dew_point double precision,
    day_0_wind_speed double precision,
    day_0_wind_deg integer,
    day_0_wind_gust double precision,
    day_0_weather_main text,
    day_0_weather_description text,
    day_0_clouds integer,
    day_0_pop double precision,
    day_0_uvi double precision,
    day_1_timestamptz timestamp with time zone,
    day_1_summary text,
    day_1_temp_day double precision,
    day_1_temp_min double precision,
    day_1_temp_max double precision,
    day_1_temp_night double precision,
    day_1_temp_eve double precision,
    day_1_temp_morn double precision,
    day_1_feels_like_day double precision,
    day_1_feels_like_night double precision,
    day_1_feels_like_eve double precision,
    day_1_feels_like_morn double precision,
    day_1_pressure integer,
    day_1_humidity integer,
    day_1_dew_point double precision,
    day_1_wind_speed double precision,
    day_1_wind_deg integer,
    day_1_wind_gust double precision,
    day_1_weather_main text,
    day_1_weather_description text,
    day_1_clouds integer,
    day_1_pop double precision,
    day_1_uvi double precision,
    day_2_timestamptz timestamp with time zone,
    day_2_summary text,
    day_2_temp_day double precision,
    day_2_temp_min double precision,
    day_2_temp_max double precision,
    day_2_temp_night double precision,
    day_2_temp_eve double precision,
    day_2_temp_morn double precision,
    day_2_feels_like_day double precision,
    day_2_feels_like_night double precision,
    day_2_feels_like_eve double precision,
    day_2_feels_like_morn double precision,
    day_2_pressure integer,
    day_2_humidity integer,
    day_2_dew_point double precision,
    day_2_wind_speed double precision,
    day_2_wind_deg integer,
    day_2_wind_gust double precision,
    day_2_weather_main text,
    day_2_weather_description text,
    day_2_clouds integer,
    day_2_pop double precision,
    day_2_uvi double precision,
    day_3_timestamptz timestamp with time zone,
    day_3_summary text,
    day_3_temp_day double precision,
    day_3_temp_min double precision,
    day_3_temp_max double precision,
    day_3_temp_night double precision,
    day_3_temp_eve double precision,
    day_3_temp_morn double precision,
    day_3_feels_like_day double precision,
    day_3_feels_like_night double precision,
    day_3_feels_like_eve double precision,
    day_3_feels_like_morn double precision,
    day_3_pressure integer,
    day_3_humidity integer,
    day_3_dew_point double precision,
    day_3_wind_speed double precision,
    day_3_wind_deg integer,
    day_3_wind_gust double precision,
    day_3_weather_main text,
    day_3_weather_description text,
    day_3_clouds integer,
    day_3_pop double precision,
    day_3_uvi double precision,
    day_4_timestamptz timestamp with time zone,
    day_4_summary text,
    day_4_temp_day double precision,
    day_4_temp_min double precision,
    day_4_temp_max double precision,
    day_4_temp_night double precision,
    day_4_temp_eve double precision,
    day_4_temp_morn double precision,
    day_4_feels_like_day double precision,
    day_4_feels_like_night double precision,
    day_4_feels_like_eve double precision,
    day_4_feels_like_morn double precision,
    day_4_pressure integer,
    day_4_humidity integer,
    day_4_dew_point double precision,
    day_4_wind_speed double precision,
    day_4_wind_deg integer,
    day_4_wind_gust double precision,
    day_4_weather_main text,
    day_4_weather_description text,
    day_4_clouds integer,
    day_4_pop double precision,
    day_4_uvi double precision,
    day_5_timestamptz timestamp with time zone,
    day_5_summary text,
    day_5_temp_day double precision,
    day_5_temp_min double precision,
    day_5_temp_max double precision,
    day_5_temp_night double precision,
    day_5_temp_eve double precision,
    day_5_temp_morn double precision,
    day_5_feels_like_day double precision,
    day_5_feels_like_night double precision,
    day_5_feels_like_eve double precision,
    day_5_feels_like_morn double precision,
    day_5_pressure integer,
    day_5_humidity integer,
    day_5_dew_point double precision,
    day_5_wind_speed double precision,
    day_5_wind_deg integer,
    day_5_wind_gust double precision,
    day_5_weather_main text,
    day_5_weather_description text,
    day_5_clouds integer,
    day_5_pop double precision,
    day_5_uvi double precision,
    day_6_timestamptz timestamp with time zone,
    day_6_summary text,
    day_6_temp_day double precision,
    day_6_temp_min double precision,
    day_6_temp_max double precision,
    day_6_temp_night double precision,
    day_6_temp_eve double precision,
    day_6_temp_morn double precision,
    day_6_feels_like_day double precision,
    day_6_feels_like_night double precision,
    day_6_feels_like_eve double precision,
    day_6_feels_like_morn double precision,
    day_6_pressure integer,
    day_6_humidity integer,
    day_6_dew_point double precision,
    day_6_wind_speed double precision,
    day_6_wind_deg integer,
    day_6_wind_gust double precision,
    day_6_weather_main text,
    day_6_weather_description text,
    day_6_clouds integer,
    day_6_pop double precision,
    day_6_uvi double precision,
    day_7_timestamptz timestamp with time zone,
    day_7_summary text,
    day_7_temp_day double precision,
    day_7_temp_min double precision,
    day_7_temp_max double precision,
    day_7_temp_night double precision,
    day_7_temp_eve double precision,
    day_7_temp_morn double precision,
    day_7_feels_like_day double precision,
    day_7_feels_like_night double precision,
    day_7_feels_like_eve double precision,
    day_7_feels_like_morn double precision,
    day_7_pressure integer,
    day_7_humidity integer,
    day_7_dew_point double precision,
    day_7_wind_speed double precision,
    day_7_wind_deg integer,
    day_7_wind_gust double precision,
    day_7_weather_main text,
    day_7_weather_description text,
    day_7_clouds integer,
    day_7_pop double precision,
    day_7_uvi double precision,
    last_updated timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.openweather_forecast_detail OWNER TO sauron;

--
-- Name: openweather_forecast_detail_id_seq; Type: SEQUENCE; Schema: public; Owner: sauron
--

CREATE SEQUENCE public.openweather_forecast_detail_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.openweather_forecast_detail_id_seq OWNER TO sauron;

--
-- Name: openweather_forecast_detail_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sauron
--

ALTER SEQUENCE public.openweather_forecast_detail_id_seq OWNED BY public.openweather_forecast_detail.id;


--
-- Name: openweather_forecast_id_seq; Type: SEQUENCE; Schema: public; Owner: sauron
--

CREATE SEQUENCE public.openweather_forecast_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.openweather_forecast_id_seq OWNER TO sauron;

--
-- Name: openweather_forecast_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sauron
--

ALTER SEQUENCE public.openweather_forecast_id_seq OWNED BY public.openweather_forecast.id;


--
-- Name: overview_data; Type: TABLE; Schema: public; Owner: sauron
--

CREATE TABLE public.overview_data (
    id integer NOT NULL,
    date date,
    lat double precision,
    lon double precision,
    timezone text,
    weather_overview text,
    api_call_id integer,
    last_updated timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    day integer
);


ALTER TABLE public.overview_data OWNER TO sauron;

--
-- Name: overview_data_id_seq; Type: SEQUENCE; Schema: public; Owner: sauron
--

CREATE SEQUENCE public.overview_data_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.overview_data_id_seq OWNER TO sauron;

--
-- Name: overview_data_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sauron
--

ALTER SEQUENCE public.overview_data_id_seq OWNED BY public.overview_data.id;


--
-- Name: openweather_forecast id; Type: DEFAULT; Schema: public; Owner: sauron
--

ALTER TABLE ONLY public.openweather_forecast ALTER COLUMN id SET DEFAULT nextval('public.openweather_forecast_id_seq'::regclass);


--
-- Name: openweather_forecast_detail id; Type: DEFAULT; Schema: public; Owner: sauron
--

ALTER TABLE ONLY public.openweather_forecast_detail ALTER COLUMN id SET DEFAULT nextval('public.openweather_forecast_detail_id_seq'::regclass);


--
-- Name: overview_data id; Type: DEFAULT; Schema: public; Owner: sauron
--

ALTER TABLE ONLY public.overview_data ALTER COLUMN id SET DEFAULT nextval('public.overview_data_id_seq'::regclass);


--
-- Name: openweather_forecast_detail openweather_forecast_detail_pkey; Type: CONSTRAINT; Schema: public; Owner: sauron
--

ALTER TABLE ONLY public.openweather_forecast_detail
    ADD CONSTRAINT openweather_forecast_detail_pkey PRIMARY KEY (id);


--
-- Name: openweather_forecast_detail openweather_forecast_detail_timestamp_lat_lon_key; Type: CONSTRAINT; Schema: public; Owner: sauron
--

ALTER TABLE ONLY public.openweather_forecast_detail
    ADD CONSTRAINT openweather_forecast_detail_timestamp_lat_lon_key UNIQUE ("timestamp", lat, lon);


--
-- Name: openweather_forecast openweather_forecast_pkey; Type: CONSTRAINT; Schema: public; Owner: sauron
--

ALTER TABLE ONLY public.openweather_forecast
    ADD CONSTRAINT openweather_forecast_pkey PRIMARY KEY (id);


--
-- Name: openweather_forecast openweather_forecast_timestamp_lat_lon_key; Type: CONSTRAINT; Schema: public; Owner: sauron
--

ALTER TABLE ONLY public.openweather_forecast
    ADD CONSTRAINT openweather_forecast_timestamp_lat_lon_key UNIQUE ("timestamp", lat, lon);


--
-- Name: overview_data overview_data_pkey; Type: CONSTRAINT; Schema: public; Owner: sauron
--

ALTER TABLE ONLY public.overview_data
    ADD CONSTRAINT overview_data_pkey PRIMARY KEY (id);


--
-- Name: overview_data set_timestamp; Type: TRIGGER; Schema: public; Owner: sauron
--

CREATE TRIGGER set_timestamp BEFORE UPDATE ON public.overview_data FOR EACH ROW EXECUTE FUNCTION public.update_timestamp();


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT USAGE ON SCHEMA public TO sauron;
GRANT USAGE ON SCHEMA public TO controlcore_user;
GRANT USAGE ON SCHEMA public TO grafana_user;


--
-- Name: TABLE openweather_forecast; Type: ACL; Schema: public; Owner: sauron
--

GRANT SELECT ON TABLE public.openweather_forecast TO controlcore_user;
GRANT SELECT ON TABLE public.openweather_forecast TO grafana_user;


--
-- Name: TABLE openweather_forecast_detail; Type: ACL; Schema: public; Owner: sauron
--

GRANT SELECT ON TABLE public.openweather_forecast_detail TO controlcore_user;
GRANT SELECT ON TABLE public.openweather_forecast_detail TO grafana_user;


--
-- Name: TABLE overview_data; Type: ACL; Schema: public; Owner: sauron
--

GRANT SELECT ON TABLE public.overview_data TO controlcore_user;
GRANT SELECT ON TABLE public.overview_data TO grafana_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT ON TABLES TO controlcore_user;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT ON TABLES TO grafana_user;


--
-- PostgreSQL database dump complete
--

