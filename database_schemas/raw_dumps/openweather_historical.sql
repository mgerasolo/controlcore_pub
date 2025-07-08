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
-- Name: celsius_to_fahrenheit(real); Type: FUNCTION; Schema: public; Owner: sauron
--

CREATE FUNCTION public.celsius_to_fahrenheit(temp real) RETURNS real
    LANGUAGE plpgsql IMMUTABLE
    AS $$
BEGIN
    RETURN (temp * 9/5) + 32;
END;
$$;


ALTER FUNCTION public.celsius_to_fahrenheit(temp real) OWNER TO sauron;

--
-- Name: extract_date(timestamp with time zone); Type: FUNCTION; Schema: public; Owner: sauron
--

CREATE FUNCTION public.extract_date(timestamp with time zone) RETURNS date
    LANGUAGE plpgsql IMMUTABLE
    AS $_$
BEGIN
    RETURN DATE_TRUNC('day', $1)::date;
END;
$_$;


ALTER FUNCTION public.extract_date(timestamp with time zone) OWNER TO sauron;

--
-- Name: insert_hourly_data(text); Type: FUNCTION; Schema: public; Owner: sauron
--

CREATE FUNCTION public.insert_hourly_data(destination_table text) RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
    cols TEXT;
    sql TEXT;
BEGIN
    SELECT string_agg(quote_ident(column_name), ', ')
    INTO cols
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'hourly_data'
      AND column_name <> 'id';

    sql := format(
        'INSERT INTO %I (%s)
         SELECT %s FROM hourly_data
         WHERE lat = 37.4908 AND lon = -79.8948
         ON CONFLICT (dt) DO NOTHING;',
        destination_table, cols, cols
    );

    EXECUTE sql;
END;
$$;


ALTER FUNCTION public.insert_hourly_data(destination_table text) OWNER TO sauron;

--
-- Name: unix_timestamp_to_timestamp_with_tz(integer, text, integer); Type: FUNCTION; Schema: public; Owner: sauron
--

CREATE FUNCTION public.unix_timestamp_to_timestamp_with_tz(unix_ts integer, tz text, tzoff integer) RETURNS timestamp with time zone
    LANGUAGE plpgsql IMMUTABLE
    AS $$
BEGIN
    RETURN (TO_TIMESTAMP(unix_ts) AT TIME ZONE 'UTC') + INTERVAL '1 second' * tzoff;
END;
$$;


ALTER FUNCTION public.unix_timestamp_to_timestamp_with_tz(unix_ts integer, tz text, tzoff integer) OWNER TO sauron;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: ar_internal_metadata; Type: TABLE; Schema: public; Owner: sauron
--

CREATE TABLE public.ar_internal_metadata (
    key character varying NOT NULL,
    value character varying,
    created_at timestamp(6) without time zone NOT NULL,
    updated_at timestamp(6) without time zone NOT NULL
);


ALTER TABLE public.ar_internal_metadata OWNER TO sauron;

--
-- Name: daily_summary_data; Type: TABLE; Schema: public; Owner: sauron
--

CREATE TABLE public.daily_summary_data (
    id integer NOT NULL,
    lat numeric(10,6),
    lon numeric(10,6),
    tzoff integer,
    date integer,
    units text,
    cloud_cover_afternoon integer,
    humidity_afternoon integer,
    precipitation_total real,
    temperature_min real,
    temperature_max real,
    temperature_afternoon real,
    temperature_night real,
    temperature_evening real,
    temperature_morning real,
    pressure_afternoon integer,
    wind_max_speed real,
    wind_max_direction integer,
    location_id integer
);


ALTER TABLE public.daily_summary_data OWNER TO sauron;

--
-- Name: daily_summary_data_id_seq; Type: SEQUENCE; Schema: public; Owner: sauron
--

CREATE SEQUENCE public.daily_summary_data_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.daily_summary_data_id_seq OWNER TO sauron;

--
-- Name: daily_summary_data_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sauron
--

ALTER SEQUENCE public.daily_summary_data_id_seq OWNED BY public.daily_summary_data.id;


--
-- Name: fincastle_daily; Type: TABLE; Schema: public; Owner: sauron
--

CREATE TABLE public.fincastle_daily (
    id integer DEFAULT nextval('public.daily_summary_data_id_seq'::regclass) NOT NULL,
    lat numeric(10,6),
    lon numeric(10,6),
    tzoff integer,
    date integer,
    units text,
    cloud_cover_afternoon integer,
    humidity_afternoon integer,
    precipitation_total real,
    temperature_min real,
    temperature_max real,
    temperature_afternoon real,
    temperature_night real,
    temperature_evening real,
    temperature_morning real,
    pressure_afternoon integer,
    wind_max_speed real,
    wind_max_direction integer,
    location_id integer
);


ALTER TABLE public.fincastle_daily OWNER TO sauron;

--
-- Name: hourly_data; Type: TABLE; Schema: public; Owner: sauron
--

CREATE TABLE public.hourly_data (
    id integer NOT NULL,
    dt integer NOT NULL,
    lat numeric(10,6) NOT NULL,
    lon numeric(10,6) NOT NULL,
    tz text NOT NULL,
    tzoff integer NOT NULL,
    sunrise integer NOT NULL,
    sunset integer NOT NULL,
    temp real NOT NULL,
    feels_like real NOT NULL,
    pressure integer NOT NULL,
    humidity integer NOT NULL,
    dew_point real,
    vis real,
    description text NOT NULL,
    clouds integer,
    wind_speed real,
    wind_deg integer,
    location_id integer
);


ALTER TABLE public.hourly_data OWNER TO sauron;

--
-- Name: openweather_data_id_seq; Type: SEQUENCE; Schema: public; Owner: sauron
--

CREATE SEQUENCE public.openweather_data_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.openweather_data_id_seq OWNER TO sauron;

--
-- Name: openweather_data_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sauron
--

ALTER SEQUENCE public.openweather_data_id_seq OWNED BY public.hourly_data.id;


--
-- Name: fincastle_hourly; Type: TABLE; Schema: public; Owner: sauron
--

CREATE TABLE public.fincastle_hourly (
    id integer DEFAULT nextval('public.openweather_data_id_seq'::regclass) NOT NULL,
    dt integer NOT NULL,
    lat numeric(10,6) NOT NULL,
    lon numeric(10,6) NOT NULL,
    tz text NOT NULL,
    tzoff integer NOT NULL,
    sunrise integer NOT NULL,
    sunset integer NOT NULL,
    temp real NOT NULL,
    feels_like real NOT NULL,
    pressure integer NOT NULL,
    humidity integer NOT NULL,
    dew_point real,
    vis real,
    description text NOT NULL,
    clouds integer,
    wind_speed real,
    wind_deg integer,
    location_id integer
);


ALTER TABLE public.fincastle_hourly OWNER TO sauron;

--
-- Name: locations; Type: TABLE; Schema: public; Owner: sauron
--

CREATE TABLE public.locations (
    id integer NOT NULL,
    friendly_name text NOT NULL,
    official_station_name text,
    lat_detail double precision NOT NULL,
    lon_detail double precision NOT NULL,
    lat_rounded real,
    lon_rounded real,
    zip_code text,
    controlcore_location_id text
);


ALTER TABLE public.locations OWNER TO sauron;

--
-- Name: locations_id_seq; Type: SEQUENCE; Schema: public; Owner: sauron
--

CREATE SEQUENCE public.locations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.locations_id_seq OWNER TO sauron;

--
-- Name: locations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sauron
--

ALTER SEQUENCE public.locations_id_seq OWNED BY public.locations.id;


--
-- Name: rome_daily; Type: TABLE; Schema: public; Owner: sauron
--

CREATE TABLE public.rome_daily (
    id integer DEFAULT nextval('public.daily_summary_data_id_seq'::regclass) NOT NULL,
    lat numeric(10,6),
    lon numeric(10,6),
    tzoff integer,
    date integer,
    units text,
    cloud_cover_afternoon integer,
    humidity_afternoon integer,
    precipitation_total real,
    temperature_min real,
    temperature_max real,
    temperature_afternoon real,
    temperature_night real,
    temperature_evening real,
    temperature_morning real,
    pressure_afternoon integer,
    wind_max_speed real,
    wind_max_direction integer,
    location_id integer
);


ALTER TABLE public.rome_daily OWNER TO sauron;

--
-- Name: rome_hourly; Type: TABLE; Schema: public; Owner: sauron
--

CREATE TABLE public.rome_hourly (
    id integer DEFAULT nextval('public.openweather_data_id_seq'::regclass) NOT NULL,
    dt integer NOT NULL,
    lat numeric(10,6) NOT NULL,
    lon numeric(10,6) NOT NULL,
    tz text NOT NULL,
    tzoff integer NOT NULL,
    sunrise integer NOT NULL,
    sunset integer NOT NULL,
    temp real NOT NULL,
    feels_like real NOT NULL,
    pressure integer NOT NULL,
    humidity integer NOT NULL,
    dew_point real,
    vis real,
    description text NOT NULL,
    clouds integer,
    wind_speed real,
    wind_deg integer,
    location_id integer
);


ALTER TABLE public.rome_hourly OWNER TO sauron;

--
-- Name: schema_migrations; Type: TABLE; Schema: public; Owner: sauron
--

CREATE TABLE public.schema_migrations (
    version character varying NOT NULL
);


ALTER TABLE public.schema_migrations OWNER TO sauron;

--
-- Name: daily_summary_data id; Type: DEFAULT; Schema: public; Owner: sauron
--

ALTER TABLE ONLY public.daily_summary_data ALTER COLUMN id SET DEFAULT nextval('public.daily_summary_data_id_seq'::regclass);


--
-- Name: hourly_data id; Type: DEFAULT; Schema: public; Owner: sauron
--

ALTER TABLE ONLY public.hourly_data ALTER COLUMN id SET DEFAULT nextval('public.openweather_data_id_seq'::regclass);


--
-- Name: locations id; Type: DEFAULT; Schema: public; Owner: sauron
--

ALTER TABLE ONLY public.locations ALTER COLUMN id SET DEFAULT nextval('public.locations_id_seq'::regclass);


--
-- Name: ar_internal_metadata ar_internal_metadata_pkey; Type: CONSTRAINT; Schema: public; Owner: sauron
--

ALTER TABLE ONLY public.ar_internal_metadata
    ADD CONSTRAINT ar_internal_metadata_pkey PRIMARY KEY (key);


--
-- Name: daily_summary_data daily_summary_data_lat_lon_date_key; Type: CONSTRAINT; Schema: public; Owner: sauron
--

ALTER TABLE ONLY public.daily_summary_data
    ADD CONSTRAINT daily_summary_data_lat_lon_date_key UNIQUE (lat, lon, date);


--
-- Name: daily_summary_data daily_summary_data_pkey; Type: CONSTRAINT; Schema: public; Owner: sauron
--

ALTER TABLE ONLY public.daily_summary_data
    ADD CONSTRAINT daily_summary_data_pkey PRIMARY KEY (id);


--
-- Name: fincastle_daily fincastle_daily_lat_lon_date_key; Type: CONSTRAINT; Schema: public; Owner: sauron
--

ALTER TABLE ONLY public.fincastle_daily
    ADD CONSTRAINT fincastle_daily_lat_lon_date_key UNIQUE (lat, lon, date);


--
-- Name: fincastle_daily fincastle_daily_pkey; Type: CONSTRAINT; Schema: public; Owner: sauron
--

ALTER TABLE ONLY public.fincastle_daily
    ADD CONSTRAINT fincastle_daily_pkey PRIMARY KEY (id);


--
-- Name: fincastle_hourly fincastle_hourly_pkey; Type: CONSTRAINT; Schema: public; Owner: sauron
--

ALTER TABLE ONLY public.fincastle_hourly
    ADD CONSTRAINT fincastle_hourly_pkey PRIMARY KEY (id);


--
-- Name: locations locations_pkey; Type: CONSTRAINT; Schema: public; Owner: sauron
--

ALTER TABLE ONLY public.locations
    ADD CONSTRAINT locations_pkey PRIMARY KEY (id);


--
-- Name: hourly_data openweather_data_pkey; Type: CONSTRAINT; Schema: public; Owner: sauron
--

ALTER TABLE ONLY public.hourly_data
    ADD CONSTRAINT openweather_data_pkey PRIMARY KEY (id);


--
-- Name: rome_daily rome_daily_lat_lon_date_key; Type: CONSTRAINT; Schema: public; Owner: sauron
--

ALTER TABLE ONLY public.rome_daily
    ADD CONSTRAINT rome_daily_lat_lon_date_key UNIQUE (lat, lon, date);


--
-- Name: rome_daily rome_daily_pkey; Type: CONSTRAINT; Schema: public; Owner: sauron
--

ALTER TABLE ONLY public.rome_daily
    ADD CONSTRAINT rome_daily_pkey PRIMARY KEY (id);


--
-- Name: rome_hourly rome_hourly_pkey; Type: CONSTRAINT; Schema: public; Owner: sauron
--

ALTER TABLE ONLY public.rome_hourly
    ADD CONSTRAINT rome_hourly_pkey PRIMARY KEY (id);


--
-- Name: schema_migrations schema_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: sauron
--

ALTER TABLE ONLY public.schema_migrations
    ADD CONSTRAINT schema_migrations_pkey PRIMARY KEY (version);


--
-- Name: fincastle_daily_date_idx; Type: INDEX; Schema: public; Owner: sauron
--

CREATE INDEX fincastle_daily_date_idx ON public.fincastle_daily USING btree (date);


--
-- Name: fincastle_hourly_dt_idx; Type: INDEX; Schema: public; Owner: sauron
--

CREATE UNIQUE INDEX fincastle_hourly_dt_idx ON public.fincastle_hourly USING btree (dt);


--
-- Name: fincastle_hourly_lat_lon_dt_idx; Type: INDEX; Schema: public; Owner: sauron
--

CREATE INDEX fincastle_hourly_lat_lon_dt_idx ON public.fincastle_hourly USING btree (lat, lon, dt);


--
-- Name: idx_lat_lon_dt; Type: INDEX; Schema: public; Owner: sauron
--

CREATE INDEX idx_lat_lon_dt ON public.hourly_data USING btree (lat, lon, dt);


--
-- Name: idx_openweather_date; Type: INDEX; Schema: public; Owner: sauron
--

CREATE INDEX idx_openweather_date ON public.daily_summary_data USING btree (date);


--
-- Name: idx_unique_dt; Type: INDEX; Schema: public; Owner: sauron
--

CREATE UNIQUE INDEX idx_unique_dt ON public.hourly_data USING btree (dt);


--
-- Name: rome_daily_date_idx; Type: INDEX; Schema: public; Owner: sauron
--

CREATE INDEX rome_daily_date_idx ON public.rome_daily USING btree (date);


--
-- Name: rome_hourly_dt_idx; Type: INDEX; Schema: public; Owner: sauron
--

CREATE UNIQUE INDEX rome_hourly_dt_idx ON public.rome_hourly USING btree (dt);


--
-- Name: rome_hourly_lat_lon_dt_idx; Type: INDEX; Schema: public; Owner: sauron
--

CREATE INDEX rome_hourly_lat_lon_dt_idx ON public.rome_hourly USING btree (lat, lon, dt);


--
-- Name: daily_summary_data daily_summary_data_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sauron
--

ALTER TABLE ONLY public.daily_summary_data
    ADD CONSTRAINT daily_summary_data_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.locations(id);


--
-- Name: fincastle_hourly fincastle_fk; Type: FK CONSTRAINT; Schema: public; Owner: sauron
--

ALTER TABLE ONLY public.fincastle_hourly
    ADD CONSTRAINT fincastle_fk FOREIGN KEY (location_id) REFERENCES public.locations(id);


--
-- Name: fincastle_daily fincastle_fk; Type: FK CONSTRAINT; Schema: public; Owner: sauron
--

ALTER TABLE ONLY public.fincastle_daily
    ADD CONSTRAINT fincastle_fk FOREIGN KEY (location_id) REFERENCES public.locations(id);


--
-- Name: hourly_data hourly_data_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sauron
--

ALTER TABLE ONLY public.hourly_data
    ADD CONSTRAINT hourly_data_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.locations(id);


--
-- Name: rome_hourly rome_fk; Type: FK CONSTRAINT; Schema: public; Owner: sauron
--

ALTER TABLE ONLY public.rome_hourly
    ADD CONSTRAINT rome_fk FOREIGN KEY (location_id) REFERENCES public.locations(id);


--
-- Name: rome_daily rome_fk; Type: FK CONSTRAINT; Schema: public; Owner: sauron
--

ALTER TABLE ONLY public.rome_daily
    ADD CONSTRAINT rome_fk FOREIGN KEY (location_id) REFERENCES public.locations(id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT USAGE ON SCHEMA public TO controlcore_user;


--
-- Name: TABLE ar_internal_metadata; Type: ACL; Schema: public; Owner: sauron
--

GRANT SELECT ON TABLE public.ar_internal_metadata TO grafana_user;
GRANT SELECT ON TABLE public.ar_internal_metadata TO controlcore_user;


--
-- Name: TABLE daily_summary_data; Type: ACL; Schema: public; Owner: sauron
--

GRANT SELECT ON TABLE public.daily_summary_data TO grafana_user;
GRANT SELECT ON TABLE public.daily_summary_data TO controlcore_user;


--
-- Name: TABLE fincastle_daily; Type: ACL; Schema: public; Owner: sauron
--

GRANT SELECT ON TABLE public.fincastle_daily TO grafana_user;
GRANT SELECT ON TABLE public.fincastle_daily TO controlcore_user;


--
-- Name: TABLE hourly_data; Type: ACL; Schema: public; Owner: sauron
--

GRANT SELECT ON TABLE public.hourly_data TO grafana_user;
GRANT SELECT ON TABLE public.hourly_data TO controlcore_user;


--
-- Name: TABLE fincastle_hourly; Type: ACL; Schema: public; Owner: sauron
--

GRANT SELECT ON TABLE public.fincastle_hourly TO grafana_user;
GRANT SELECT ON TABLE public.fincastle_hourly TO controlcore_user;


--
-- Name: TABLE locations; Type: ACL; Schema: public; Owner: sauron
--

GRANT SELECT ON TABLE public.locations TO grafana_user;
GRANT SELECT ON TABLE public.locations TO controlcore_user;


--
-- Name: TABLE rome_daily; Type: ACL; Schema: public; Owner: sauron
--

GRANT SELECT ON TABLE public.rome_daily TO grafana_user;
GRANT SELECT ON TABLE public.rome_daily TO controlcore_user;


--
-- Name: TABLE rome_hourly; Type: ACL; Schema: public; Owner: sauron
--

GRANT SELECT ON TABLE public.rome_hourly TO grafana_user;
GRANT SELECT ON TABLE public.rome_hourly TO controlcore_user;


--
-- Name: TABLE schema_migrations; Type: ACL; Schema: public; Owner: sauron
--

GRANT SELECT ON TABLE public.schema_migrations TO grafana_user;
GRANT SELECT ON TABLE public.schema_migrations TO controlcore_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT ON TABLES TO controlcore_user;


--
-- PostgreSQL database dump complete
--

