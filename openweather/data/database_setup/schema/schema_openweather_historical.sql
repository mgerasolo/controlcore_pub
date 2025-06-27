--
-- PostgreSQL database dump
--

-- Dumped from database version 16.9 (Ubuntu 16.9-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.9 (Ubuntu 16.9-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: celsius_to_fahrenheit(real); Type: FUNCTION; Schema: public; Owner: overseer
--

CREATE FUNCTION public.celsius_to_fahrenheit(temp real) RETURNS real
    LANGUAGE plpgsql IMMUTABLE
    AS $$
BEGIN
    RETURN (temp * 9/5) + 32;
END;
$$;


ALTER FUNCTION public.celsius_to_fahrenheit(temp real) OWNER TO overseer;

--
-- Name: extract_date(timestamp with time zone); Type: FUNCTION; Schema: public; Owner: overseer
--

CREATE FUNCTION public.extract_date(timestamp with time zone) RETURNS date
    LANGUAGE plpgsql IMMUTABLE
    AS $_$
BEGIN
    RETURN DATE_TRUNC('day', $1)::date;
END;
$_$;


ALTER FUNCTION public.extract_date(timestamp with time zone) OWNER TO overseer;

--
-- Name: insert_hourly_data(text); Type: FUNCTION; Schema: public; Owner: overseer
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


ALTER FUNCTION public.insert_hourly_data(destination_table text) OWNER TO overseer;

--
-- Name: unix_timestamp_to_timestamp_with_tz(integer, text, integer); Type: FUNCTION; Schema: public; Owner: overseer
--

CREATE FUNCTION public.unix_timestamp_to_timestamp_with_tz(unix_ts integer, tz text, tzoff integer) RETURNS timestamp with time zone
    LANGUAGE plpgsql IMMUTABLE
    AS $$
BEGIN
    RETURN (TO_TIMESTAMP(unix_ts) AT TIME ZONE 'UTC') + INTERVAL '1 second' * tzoff;
END;
$$;


ALTER FUNCTION public.unix_timestamp_to_timestamp_with_tz(unix_ts integer, tz text, tzoff integer) OWNER TO overseer;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: ar_internal_metadata; Type: TABLE; Schema: public; Owner: overseer
--

CREATE TABLE public.ar_internal_metadata (
    key character varying NOT NULL,
    value character varying,
    created_at timestamp(6) without time zone NOT NULL,
    updated_at timestamp(6) without time zone NOT NULL
);


ALTER TABLE public.ar_internal_metadata OWNER TO overseer;

--
-- Name: daily_summary_data; Type: TABLE; Schema: public; Owner: overseer
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


ALTER TABLE public.daily_summary_data OWNER TO overseer;

--
-- Name: daily_summary_data_id_seq; Type: SEQUENCE; Schema: public; Owner: overseer
--

CREATE SEQUENCE public.daily_summary_data_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.daily_summary_data_id_seq OWNER TO overseer;

--
-- Name: daily_summary_data_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: overseer
--

ALTER SEQUENCE public.daily_summary_data_id_seq OWNED BY public.daily_summary_data.id;


--
-- Name: fincastle_daily; Type: TABLE; Schema: public; Owner: overseer
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


ALTER TABLE public.fincastle_daily OWNER TO overseer;

--
-- Name: hourly_data; Type: TABLE; Schema: public; Owner: overseer
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


ALTER TABLE public.hourly_data OWNER TO overseer;

--
-- Name: openweather_data_id_seq; Type: SEQUENCE; Schema: public; Owner: overseer
--

CREATE SEQUENCE public.openweather_data_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.openweather_data_id_seq OWNER TO overseer;

--
-- Name: openweather_data_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: overseer
--

ALTER SEQUENCE public.openweather_data_id_seq OWNED BY public.hourly_data.id;


--
-- Name: fincastle_hourly; Type: TABLE; Schema: public; Owner: overseer
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


ALTER TABLE public.fincastle_hourly OWNER TO overseer;

--
-- Name: locations; Type: TABLE; Schema: public; Owner: overseer
--

CREATE TABLE public.locations (
    id integer NOT NULL,
    friendly_name text NOT NULL,
    official_station_name text,
    lat_detail double precision NOT NULL,
    lon_detail double precision NOT NULL,
    lat_rounded real,
    lon_rounded real,
    zip_code text
);


ALTER TABLE public.locations OWNER TO overseer;

--
-- Name: locations_id_seq; Type: SEQUENCE; Schema: public; Owner: overseer
--

CREATE SEQUENCE public.locations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.locations_id_seq OWNER TO overseer;

--
-- Name: locations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: overseer
--

ALTER SEQUENCE public.locations_id_seq OWNED BY public.locations.id;


--
-- Name: rome_daily; Type: TABLE; Schema: public; Owner: overseer
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


ALTER TABLE public.rome_daily OWNER TO overseer;

--
-- Name: rome_hourly; Type: TABLE; Schema: public; Owner: overseer
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


ALTER TABLE public.rome_hourly OWNER TO overseer;

--
-- Name: schema_migrations; Type: TABLE; Schema: public; Owner: overseer
--

CREATE TABLE public.schema_migrations (
    version character varying NOT NULL
);


ALTER TABLE public.schema_migrations OWNER TO overseer;

--
-- Name: daily_summary_data id; Type: DEFAULT; Schema: public; Owner: overseer
--

ALTER TABLE ONLY public.daily_summary_data ALTER COLUMN id SET DEFAULT nextval('public.daily_summary_data_id_seq'::regclass);


--
-- Name: hourly_data id; Type: DEFAULT; Schema: public; Owner: overseer
--

ALTER TABLE ONLY public.hourly_data ALTER COLUMN id SET DEFAULT nextval('public.openweather_data_id_seq'::regclass);


--
-- Name: locations id; Type: DEFAULT; Schema: public; Owner: overseer
--

ALTER TABLE ONLY public.locations ALTER COLUMN id SET DEFAULT nextval('public.locations_id_seq'::regclass);


--
-- Name: ar_internal_metadata ar_internal_metadata_pkey; Type: CONSTRAINT; Schema: public; Owner: overseer
--

ALTER TABLE ONLY public.ar_internal_metadata
    ADD CONSTRAINT ar_internal_metadata_pkey PRIMARY KEY (key);


--
-- Name: daily_summary_data daily_summary_data_lat_lon_date_key; Type: CONSTRAINT; Schema: public; Owner: overseer
--

ALTER TABLE ONLY public.daily_summary_data
    ADD CONSTRAINT daily_summary_data_lat_lon_date_key UNIQUE (lat, lon, date);


--
-- Name: daily_summary_data daily_summary_data_pkey; Type: CONSTRAINT; Schema: public; Owner: overseer
--

ALTER TABLE ONLY public.daily_summary_data
    ADD CONSTRAINT daily_summary_data_pkey PRIMARY KEY (id);


--
-- Name: fincastle_daily fincastle_daily_lat_lon_date_key; Type: CONSTRAINT; Schema: public; Owner: overseer
--

ALTER TABLE ONLY public.fincastle_daily
    ADD CONSTRAINT fincastle_daily_lat_lon_date_key UNIQUE (lat, lon, date);


--
-- Name: fincastle_daily fincastle_daily_pkey; Type: CONSTRAINT; Schema: public; Owner: overseer
--

ALTER TABLE ONLY public.fincastle_daily
    ADD CONSTRAINT fincastle_daily_pkey PRIMARY KEY (id);


--
-- Name: fincastle_hourly fincastle_hourly_pkey; Type: CONSTRAINT; Schema: public; Owner: overseer
--

ALTER TABLE ONLY public.fincastle_hourly
    ADD CONSTRAINT fincastle_hourly_pkey PRIMARY KEY (id);


--
-- Name: locations locations_pkey; Type: CONSTRAINT; Schema: public; Owner: overseer
--

ALTER TABLE ONLY public.locations
    ADD CONSTRAINT locations_pkey PRIMARY KEY (id);


--
-- Name: hourly_data openweather_data_pkey; Type: CONSTRAINT; Schema: public; Owner: overseer
--

ALTER TABLE ONLY public.hourly_data
    ADD CONSTRAINT openweather_data_pkey PRIMARY KEY (id);


--
-- Name: rome_daily rome_daily_lat_lon_date_key; Type: CONSTRAINT; Schema: public; Owner: overseer
--

ALTER TABLE ONLY public.rome_daily
    ADD CONSTRAINT rome_daily_lat_lon_date_key UNIQUE (lat, lon, date);


--
-- Name: rome_daily rome_daily_pkey; Type: CONSTRAINT; Schema: public; Owner: overseer
--

ALTER TABLE ONLY public.rome_daily
    ADD CONSTRAINT rome_daily_pkey PRIMARY KEY (id);


--
-- Name: rome_hourly rome_hourly_pkey; Type: CONSTRAINT; Schema: public; Owner: overseer
--

ALTER TABLE ONLY public.rome_hourly
    ADD CONSTRAINT rome_hourly_pkey PRIMARY KEY (id);


--
-- Name: schema_migrations schema_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: overseer
--

ALTER TABLE ONLY public.schema_migrations
    ADD CONSTRAINT schema_migrations_pkey PRIMARY KEY (version);


--
-- Name: fincastle_daily_date_idx; Type: INDEX; Schema: public; Owner: overseer
--

CREATE INDEX fincastle_daily_date_idx ON public.fincastle_daily USING btree (date);


--
-- Name: fincastle_hourly_dt_idx; Type: INDEX; Schema: public; Owner: overseer
--

CREATE UNIQUE INDEX fincastle_hourly_dt_idx ON public.fincastle_hourly USING btree (dt);


--
-- Name: fincastle_hourly_lat_lon_dt_idx; Type: INDEX; Schema: public; Owner: overseer
--

CREATE INDEX fincastle_hourly_lat_lon_dt_idx ON public.fincastle_hourly USING btree (lat, lon, dt);


--
-- Name: idx_lat_lon_dt; Type: INDEX; Schema: public; Owner: overseer
--

CREATE INDEX idx_lat_lon_dt ON public.hourly_data USING btree (lat, lon, dt);


--
-- Name: idx_openweather_date; Type: INDEX; Schema: public; Owner: overseer
--

CREATE INDEX idx_openweather_date ON public.daily_summary_data USING btree (date);


--
-- Name: idx_unique_dt; Type: INDEX; Schema: public; Owner: overseer
--

CREATE UNIQUE INDEX idx_unique_dt ON public.hourly_data USING btree (dt);


--
-- Name: rome_daily_date_idx; Type: INDEX; Schema: public; Owner: overseer
--

CREATE INDEX rome_daily_date_idx ON public.rome_daily USING btree (date);


--
-- Name: rome_hourly_dt_idx; Type: INDEX; Schema: public; Owner: overseer
--

CREATE UNIQUE INDEX rome_hourly_dt_idx ON public.rome_hourly USING btree (dt);


--
-- Name: rome_hourly_lat_lon_dt_idx; Type: INDEX; Schema: public; Owner: overseer
--

CREATE INDEX rome_hourly_lat_lon_dt_idx ON public.rome_hourly USING btree (lat, lon, dt);


--
-- Name: daily_summary_data daily_summary_data_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: overseer
--

ALTER TABLE ONLY public.daily_summary_data
    ADD CONSTRAINT daily_summary_data_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.locations(id);


--
-- Name: fincastle_hourly fincastle_fk; Type: FK CONSTRAINT; Schema: public; Owner: overseer
--

ALTER TABLE ONLY public.fincastle_hourly
    ADD CONSTRAINT fincastle_fk FOREIGN KEY (location_id) REFERENCES public.locations(id);


--
-- Name: fincastle_daily fincastle_fk; Type: FK CONSTRAINT; Schema: public; Owner: overseer
--

ALTER TABLE ONLY public.fincastle_daily
    ADD CONSTRAINT fincastle_fk FOREIGN KEY (location_id) REFERENCES public.locations(id);


--
-- Name: hourly_data hourly_data_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: overseer
--

ALTER TABLE ONLY public.hourly_data
    ADD CONSTRAINT hourly_data_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.locations(id);


--
-- Name: rome_hourly rome_fk; Type: FK CONSTRAINT; Schema: public; Owner: overseer
--

ALTER TABLE ONLY public.rome_hourly
    ADD CONSTRAINT rome_fk FOREIGN KEY (location_id) REFERENCES public.locations(id);


--
-- Name: rome_daily rome_fk; Type: FK CONSTRAINT; Schema: public; Owner: overseer
--

ALTER TABLE ONLY public.rome_daily
    ADD CONSTRAINT rome_fk FOREIGN KEY (location_id) REFERENCES public.locations(id);


--
-- Name: SCHEMA pg_catalog; Type: ACL; Schema: -; Owner: postgres
--

GRANT USAGE ON SCHEMA pg_catalog TO grafana_user;


--
-- Name: TABLE pg_aggregate; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_aggregate TO grafana_user;


--
-- Name: TABLE pg_am; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_am TO grafana_user;


--
-- Name: TABLE pg_amop; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_amop TO grafana_user;


--
-- Name: TABLE pg_amproc; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_amproc TO grafana_user;


--
-- Name: TABLE pg_attrdef; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_attrdef TO grafana_user;


--
-- Name: TABLE pg_attribute; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_attribute TO grafana_user;


--
-- Name: TABLE pg_auth_members; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_auth_members TO grafana_user;


--
-- Name: TABLE pg_authid; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_authid TO grafana_user;


--
-- Name: TABLE pg_available_extension_versions; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_available_extension_versions TO grafana_user;


--
-- Name: TABLE pg_available_extensions; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_available_extensions TO grafana_user;


--
-- Name: TABLE pg_backend_memory_contexts; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_backend_memory_contexts TO grafana_user;


--
-- Name: TABLE pg_cast; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_cast TO grafana_user;


--
-- Name: TABLE pg_class; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_class TO grafana_user;


--
-- Name: TABLE pg_collation; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_collation TO grafana_user;


--
-- Name: TABLE pg_config; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_config TO grafana_user;


--
-- Name: TABLE pg_constraint; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_constraint TO grafana_user;


--
-- Name: TABLE pg_conversion; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_conversion TO grafana_user;


--
-- Name: TABLE pg_cursors; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_cursors TO grafana_user;


--
-- Name: TABLE pg_database; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_database TO grafana_user;


--
-- Name: TABLE pg_db_role_setting; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_db_role_setting TO grafana_user;


--
-- Name: TABLE pg_default_acl; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_default_acl TO grafana_user;


--
-- Name: TABLE pg_depend; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_depend TO grafana_user;


--
-- Name: TABLE pg_description; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_description TO grafana_user;


--
-- Name: TABLE pg_enum; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_enum TO grafana_user;


--
-- Name: TABLE pg_event_trigger; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_event_trigger TO grafana_user;


--
-- Name: TABLE pg_extension; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_extension TO grafana_user;


--
-- Name: TABLE pg_file_settings; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_file_settings TO grafana_user;


--
-- Name: TABLE pg_foreign_data_wrapper; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_foreign_data_wrapper TO grafana_user;


--
-- Name: TABLE pg_foreign_server; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_foreign_server TO grafana_user;


--
-- Name: TABLE pg_foreign_table; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_foreign_table TO grafana_user;


--
-- Name: TABLE pg_group; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_group TO grafana_user;


--
-- Name: TABLE pg_hba_file_rules; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_hba_file_rules TO grafana_user;


--
-- Name: TABLE pg_ident_file_mappings; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_ident_file_mappings TO grafana_user;


--
-- Name: TABLE pg_index; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_index TO grafana_user;


--
-- Name: TABLE pg_indexes; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_indexes TO grafana_user;


--
-- Name: TABLE pg_inherits; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_inherits TO grafana_user;


--
-- Name: TABLE pg_init_privs; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_init_privs TO grafana_user;


--
-- Name: TABLE pg_language; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_language TO grafana_user;


--
-- Name: TABLE pg_largeobject; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_largeobject TO grafana_user;


--
-- Name: TABLE pg_largeobject_metadata; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_largeobject_metadata TO grafana_user;


--
-- Name: TABLE pg_locks; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_locks TO grafana_user;


--
-- Name: TABLE pg_matviews; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_matviews TO grafana_user;


--
-- Name: TABLE pg_namespace; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_namespace TO grafana_user;


--
-- Name: TABLE pg_opclass; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_opclass TO grafana_user;


--
-- Name: TABLE pg_operator; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_operator TO grafana_user;


--
-- Name: TABLE pg_opfamily; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_opfamily TO grafana_user;


--
-- Name: TABLE pg_parameter_acl; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_parameter_acl TO grafana_user;


--
-- Name: TABLE pg_partitioned_table; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_partitioned_table TO grafana_user;


--
-- Name: TABLE pg_policies; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_policies TO grafana_user;


--
-- Name: TABLE pg_policy; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_policy TO grafana_user;


--
-- Name: TABLE pg_prepared_statements; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_prepared_statements TO grafana_user;


--
-- Name: TABLE pg_prepared_xacts; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_prepared_xacts TO grafana_user;


--
-- Name: TABLE pg_proc; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_proc TO grafana_user;


--
-- Name: TABLE pg_publication; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_publication TO grafana_user;


--
-- Name: TABLE pg_publication_namespace; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_publication_namespace TO grafana_user;


--
-- Name: TABLE pg_publication_rel; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_publication_rel TO grafana_user;


--
-- Name: TABLE pg_publication_tables; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_publication_tables TO grafana_user;


--
-- Name: TABLE pg_range; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_range TO grafana_user;


--
-- Name: TABLE pg_replication_origin; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_replication_origin TO grafana_user;


--
-- Name: TABLE pg_replication_origin_status; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_replication_origin_status TO grafana_user;


--
-- Name: TABLE pg_replication_slots; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_replication_slots TO grafana_user;


--
-- Name: TABLE pg_rewrite; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_rewrite TO grafana_user;


--
-- Name: TABLE pg_roles; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_roles TO grafana_user;


--
-- Name: TABLE pg_rules; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_rules TO grafana_user;


--
-- Name: TABLE pg_seclabel; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_seclabel TO grafana_user;


--
-- Name: TABLE pg_seclabels; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_seclabels TO grafana_user;


--
-- Name: TABLE pg_sequence; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_sequence TO grafana_user;


--
-- Name: TABLE pg_sequences; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_sequences TO grafana_user;


--
-- Name: TABLE pg_settings; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_settings TO grafana_user;


--
-- Name: TABLE pg_shadow; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_shadow TO grafana_user;


--
-- Name: TABLE pg_shdepend; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_shdepend TO grafana_user;


--
-- Name: TABLE pg_shdescription; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_shdescription TO grafana_user;


--
-- Name: TABLE pg_shmem_allocations; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_shmem_allocations TO grafana_user;


--
-- Name: TABLE pg_shseclabel; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_shseclabel TO grafana_user;


--
-- Name: TABLE pg_stat_activity; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_stat_activity TO grafana_user;


--
-- Name: TABLE pg_stat_all_indexes; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_stat_all_indexes TO grafana_user;


--
-- Name: TABLE pg_stat_all_tables; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_stat_all_tables TO grafana_user;


--
-- Name: TABLE pg_stat_archiver; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_stat_archiver TO grafana_user;


--
-- Name: TABLE pg_stat_bgwriter; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_stat_bgwriter TO grafana_user;


--
-- Name: TABLE pg_stat_database; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_stat_database TO grafana_user;


--
-- Name: TABLE pg_stat_database_conflicts; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_stat_database_conflicts TO grafana_user;


--
-- Name: TABLE pg_stat_gssapi; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_stat_gssapi TO grafana_user;


--
-- Name: TABLE pg_stat_io; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_stat_io TO grafana_user;


--
-- Name: TABLE pg_stat_progress_analyze; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_stat_progress_analyze TO grafana_user;


--
-- Name: TABLE pg_stat_progress_basebackup; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_stat_progress_basebackup TO grafana_user;


--
-- Name: TABLE pg_stat_progress_cluster; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_stat_progress_cluster TO grafana_user;


--
-- Name: TABLE pg_stat_progress_copy; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_stat_progress_copy TO grafana_user;


--
-- Name: TABLE pg_stat_progress_create_index; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_stat_progress_create_index TO grafana_user;


--
-- Name: TABLE pg_stat_progress_vacuum; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_stat_progress_vacuum TO grafana_user;


--
-- Name: TABLE pg_stat_recovery_prefetch; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_stat_recovery_prefetch TO grafana_user;


--
-- Name: TABLE pg_stat_replication; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_stat_replication TO grafana_user;


--
-- Name: TABLE pg_stat_replication_slots; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_stat_replication_slots TO grafana_user;


--
-- Name: TABLE pg_stat_slru; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_stat_slru TO grafana_user;


--
-- Name: TABLE pg_stat_ssl; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_stat_ssl TO grafana_user;


--
-- Name: TABLE pg_stat_subscription; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_stat_subscription TO grafana_user;


--
-- Name: TABLE pg_stat_subscription_stats; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_stat_subscription_stats TO grafana_user;


--
-- Name: TABLE pg_stat_sys_indexes; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_stat_sys_indexes TO grafana_user;


--
-- Name: TABLE pg_stat_sys_tables; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_stat_sys_tables TO grafana_user;


--
-- Name: TABLE pg_stat_user_functions; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_stat_user_functions TO grafana_user;


--
-- Name: TABLE pg_stat_user_indexes; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_stat_user_indexes TO grafana_user;


--
-- Name: TABLE pg_stat_user_tables; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_stat_user_tables TO grafana_user;


--
-- Name: TABLE pg_stat_wal; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_stat_wal TO grafana_user;


--
-- Name: TABLE pg_stat_wal_receiver; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_stat_wal_receiver TO grafana_user;


--
-- Name: TABLE pg_stat_xact_all_tables; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_stat_xact_all_tables TO grafana_user;


--
-- Name: TABLE pg_stat_xact_sys_tables; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_stat_xact_sys_tables TO grafana_user;


--
-- Name: TABLE pg_stat_xact_user_functions; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_stat_xact_user_functions TO grafana_user;


--
-- Name: TABLE pg_stat_xact_user_tables; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_stat_xact_user_tables TO grafana_user;


--
-- Name: TABLE pg_statio_all_indexes; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_statio_all_indexes TO grafana_user;


--
-- Name: TABLE pg_statio_all_sequences; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_statio_all_sequences TO grafana_user;


--
-- Name: TABLE pg_statio_all_tables; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_statio_all_tables TO grafana_user;


--
-- Name: TABLE pg_statio_sys_indexes; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_statio_sys_indexes TO grafana_user;


--
-- Name: TABLE pg_statio_sys_sequences; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_statio_sys_sequences TO grafana_user;


--
-- Name: TABLE pg_statio_sys_tables; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_statio_sys_tables TO grafana_user;


--
-- Name: TABLE pg_statio_user_indexes; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_statio_user_indexes TO grafana_user;


--
-- Name: TABLE pg_statio_user_sequences; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_statio_user_sequences TO grafana_user;


--
-- Name: TABLE pg_statio_user_tables; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_statio_user_tables TO grafana_user;


--
-- Name: TABLE pg_statistic; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_statistic TO grafana_user;


--
-- Name: TABLE pg_statistic_ext; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_statistic_ext TO grafana_user;


--
-- Name: TABLE pg_statistic_ext_data; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_statistic_ext_data TO grafana_user;


--
-- Name: TABLE pg_stats; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_stats TO grafana_user;


--
-- Name: TABLE pg_stats_ext; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_stats_ext TO grafana_user;


--
-- Name: TABLE pg_stats_ext_exprs; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_stats_ext_exprs TO grafana_user;


--
-- Name: TABLE pg_subscription; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_subscription TO grafana_user;


--
-- Name: TABLE pg_subscription_rel; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_subscription_rel TO grafana_user;


--
-- Name: TABLE pg_tables; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_tables TO grafana_user;


--
-- Name: TABLE pg_tablespace; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_tablespace TO grafana_user;


--
-- Name: TABLE pg_timezone_abbrevs; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_timezone_abbrevs TO grafana_user;


--
-- Name: TABLE pg_timezone_names; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_timezone_names TO grafana_user;


--
-- Name: TABLE pg_transform; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_transform TO grafana_user;


--
-- Name: TABLE pg_trigger; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_trigger TO grafana_user;


--
-- Name: TABLE pg_ts_config; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_ts_config TO grafana_user;


--
-- Name: TABLE pg_ts_config_map; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_ts_config_map TO grafana_user;


--
-- Name: TABLE pg_ts_dict; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_ts_dict TO grafana_user;


--
-- Name: TABLE pg_ts_parser; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_ts_parser TO grafana_user;


--
-- Name: TABLE pg_ts_template; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_ts_template TO grafana_user;


--
-- Name: TABLE pg_type; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_type TO grafana_user;


--
-- Name: TABLE pg_user; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_user TO grafana_user;


--
-- Name: TABLE pg_user_mapping; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_user_mapping TO grafana_user;


--
-- Name: TABLE pg_user_mappings; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_user_mappings TO grafana_user;


--
-- Name: TABLE pg_views; Type: ACL; Schema: pg_catalog; Owner: postgres
--

GRANT SELECT ON TABLE pg_catalog.pg_views TO grafana_user;


--
-- Name: TABLE ar_internal_metadata; Type: ACL; Schema: public; Owner: overseer
--

GRANT SELECT ON TABLE public.ar_internal_metadata TO grafana;
GRANT SELECT ON TABLE public.ar_internal_metadata TO grafana_user;


--
-- Name: TABLE daily_summary_data; Type: ACL; Schema: public; Owner: overseer
--

GRANT SELECT ON TABLE public.daily_summary_data TO grafana;
GRANT SELECT ON TABLE public.daily_summary_data TO grafana_user;


--
-- Name: TABLE fincastle_daily; Type: ACL; Schema: public; Owner: overseer
--

GRANT SELECT ON TABLE public.fincastle_daily TO grafana_user;


--
-- Name: TABLE hourly_data; Type: ACL; Schema: public; Owner: overseer
--

GRANT SELECT ON TABLE public.hourly_data TO grafana;
GRANT SELECT ON TABLE public.hourly_data TO grafana_user;


--
-- Name: TABLE fincastle_hourly; Type: ACL; Schema: public; Owner: overseer
--

GRANT SELECT ON TABLE public.fincastle_hourly TO grafana_user;


--
-- Name: TABLE locations; Type: ACL; Schema: public; Owner: overseer
--

GRANT SELECT ON TABLE public.locations TO grafana;
GRANT SELECT ON TABLE public.locations TO grafana_user;


--
-- Name: TABLE rome_daily; Type: ACL; Schema: public; Owner: overseer
--

GRANT SELECT ON TABLE public.rome_daily TO grafana_user;


--
-- Name: TABLE rome_hourly; Type: ACL; Schema: public; Owner: overseer
--

GRANT SELECT ON TABLE public.rome_hourly TO grafana_user;


--
-- Name: TABLE schema_migrations; Type: ACL; Schema: public; Owner: overseer
--

GRANT SELECT ON TABLE public.schema_migrations TO grafana;
GRANT SELECT ON TABLE public.schema_migrations TO grafana_user;


--
-- PostgreSQL database dump complete
--

