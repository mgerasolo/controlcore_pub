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
-- Name: timescaledb; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS timescaledb WITH SCHEMA public;


--
-- Name: EXTENSION timescaledb; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION timescaledb IS 'Enables scalable inserts and complex queries for time-series data (Community Edition)';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: sensor_data; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sensor_data (
    station_id text NOT NULL,
    location_id text,
    controller_id text NOT NULL,
    sensor_id text NOT NULL,
    sensor_type text NOT NULL,
    source_id text NOT NULL,
    pin integer,
    value real,
    unit text,
    received_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.sensor_data OWNER TO postgres;

--
-- Name: _hyper_2_18_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_2_18_chunk (
    CONSTRAINT constraint_18 CHECK (((received_at >= '2025-06-18 20:00:00-04'::timestamp with time zone) AND (received_at < '2025-06-25 20:00:00-04'::timestamp with time zone)))
)
INHERITS (public.sensor_data);


ALTER TABLE _timescaledb_internal._hyper_2_18_chunk OWNER TO postgres;

--
-- Name: _hyper_2_19_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_2_19_chunk (
    CONSTRAINT constraint_19 CHECK (((received_at >= '1969-12-31 19:00:00-05'::timestamp with time zone) AND (received_at < '1970-01-07 19:00:00-05'::timestamp with time zone)))
)
INHERITS (public.sensor_data);


ALTER TABLE _timescaledb_internal._hyper_2_19_chunk OWNER TO postgres;

--
-- Name: _hyper_2_20_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_2_20_chunk (
    CONSTRAINT constraint_20 CHECK (((received_at >= '2025-06-25 20:00:00-04'::timestamp with time zone) AND (received_at < '2025-07-02 20:00:00-04'::timestamp with time zone)))
)
INHERITS (public.sensor_data);


ALTER TABLE _timescaledb_internal._hyper_2_20_chunk OWNER TO postgres;

--
-- Name: control_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.control_log (
    id integer NOT NULL,
    station text NOT NULL,
    controller_id text NOT NULL,
    sensor_id text,
    sensor_type text,
    command text NOT NULL,
    value real,
    unit text,
    source text,
    requestor_id text,
    received_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.control_log OWNER TO postgres;

--
-- Name: control_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.control_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.control_log_id_seq OWNER TO postgres;

--
-- Name: control_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.control_log_id_seq OWNED BY public.control_log.id;


--
-- Name: controller_boot_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.controller_boot_log (
    controller_id text,
    boot_time bigint,
    startup_config_hash text,
    running_config_applied boolean,
    sensors_loaded jsonb,
    received_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.controller_boot_log OWNER TO postgres;

--
-- Name: controller_health; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.controller_health (
    controller_id text NOT NULL,
    last_reported timestamp without time zone DEFAULT now(),
    issue text NOT NULL,
    severity text DEFAULT 'warning'::text,
    notes text
);


ALTER TABLE public.controller_health OWNER TO postgres;

--
-- Name: controllers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.controllers (
    controller_id text NOT NULL,
    station_id text,
    last_seen timestamp with time zone,
    config_source text,
    startup_config_hash text,
    running_config_applied boolean
);


ALTER TABLE public.controllers OWNER TO postgres;

--
-- Name: locations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.locations (
    location_id text NOT NULL,
    friendly_name text,
    lat double precision,
    lon double precision,
    zip_code text
);


ALTER TABLE public.locations OWNER TO postgres;

--
-- Name: sensor_assignments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sensor_assignments (
    controller_id text NOT NULL,
    pin integer NOT NULL,
    location_id text,
    sensor_id text,
    sensor_type text,
    unit text,
    location_hint text,
    config_source text,
    assigned_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.sensor_assignments OWNER TO postgres;

--
-- Name: stations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.stations (
    station_id text NOT NULL,
    location_id text,
    label text,
    notes text
);


ALTER TABLE public.stations OWNER TO postgres;

--
-- Name: watering_schedule; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.watering_schedule (
    id integer NOT NULL,
    zone_id text NOT NULL,
    sensor_id text NOT NULL,
    source_id text NOT NULL,
    station text NOT NULL,
    controller_id text NOT NULL,
    start_time timestamp with time zone NOT NULL,
    duration_seconds integer NOT NULL,
    status text DEFAULT 'scheduled'::text,
    confirmed_execution boolean DEFAULT false,
    scheduled_by text DEFAULT 'advisor'::text,
    requestor_id text,
    metadata jsonb,
    notes text,
    created_at timestamp with time zone DEFAULT now(),
    last_updated timestamp with time zone DEFAULT now()
);


ALTER TABLE public.watering_schedule OWNER TO postgres;

--
-- Name: watering_schedule_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.watering_schedule_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.watering_schedule_id_seq OWNER TO postgres;

--
-- Name: watering_schedule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.watering_schedule_id_seq OWNED BY public.watering_schedule.id;


--
-- Name: _hyper_2_18_chunk received_at; Type: DEFAULT; Schema: _timescaledb_internal; Owner: postgres
--

ALTER TABLE ONLY _timescaledb_internal._hyper_2_18_chunk ALTER COLUMN received_at SET DEFAULT now();


--
-- Name: _hyper_2_19_chunk received_at; Type: DEFAULT; Schema: _timescaledb_internal; Owner: postgres
--

ALTER TABLE ONLY _timescaledb_internal._hyper_2_19_chunk ALTER COLUMN received_at SET DEFAULT now();


--
-- Name: _hyper_2_20_chunk received_at; Type: DEFAULT; Schema: _timescaledb_internal; Owner: postgres
--

ALTER TABLE ONLY _timescaledb_internal._hyper_2_20_chunk ALTER COLUMN received_at SET DEFAULT now();


--
-- Name: control_log id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.control_log ALTER COLUMN id SET DEFAULT nextval('public.control_log_id_seq'::regclass);


--
-- Name: watering_schedule id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.watering_schedule ALTER COLUMN id SET DEFAULT nextval('public.watering_schedule_id_seq'::regclass);


--
-- Name: control_log control_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.control_log
    ADD CONSTRAINT control_log_pkey PRIMARY KEY (id);


--
-- Name: controller_health controller_health_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.controller_health
    ADD CONSTRAINT controller_health_pkey PRIMARY KEY (controller_id, issue);


--
-- Name: controllers controllers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.controllers
    ADD CONSTRAINT controllers_pkey PRIMARY KEY (controller_id);


--
-- Name: locations locations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.locations
    ADD CONSTRAINT locations_pkey PRIMARY KEY (location_id);


--
-- Name: sensor_assignments sensor_assignments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sensor_assignments
    ADD CONSTRAINT sensor_assignments_pkey PRIMARY KEY (controller_id, pin);


--
-- Name: stations stations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stations
    ADD CONSTRAINT stations_pkey PRIMARY KEY (station_id);


--
-- Name: watering_schedule watering_schedule_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.watering_schedule
    ADD CONSTRAINT watering_schedule_pkey PRIMARY KEY (id);


--
-- Name: _hyper_2_18_chunk_sensor_data_received_at_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_18_chunk_sensor_data_received_at_idx ON _timescaledb_internal._hyper_2_18_chunk USING btree (received_at DESC);


--
-- Name: _hyper_2_19_chunk_sensor_data_received_at_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_19_chunk_sensor_data_received_at_idx ON _timescaledb_internal._hyper_2_19_chunk USING btree (received_at DESC);


--
-- Name: _hyper_2_20_chunk_sensor_data_received_at_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_20_chunk_sensor_data_received_at_idx ON _timescaledb_internal._hyper_2_20_chunk USING btree (received_at DESC);


--
-- Name: sensor_data_received_at_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX sensor_data_received_at_idx ON public.sensor_data USING btree (received_at DESC);


--
-- Name: watering_schedule_zone_time_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX watering_schedule_zone_time_idx ON public.watering_schedule USING btree (zone_id, start_time);


--
-- Name: sensor_data ts_insert_blocker; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER ts_insert_blocker BEFORE INSERT ON public.sensor_data FOR EACH ROW EXECUTE FUNCTION _timescaledb_functions.insert_blocker();


--
-- Name: stations stations_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stations
    ADD CONSTRAINT stations_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.locations(location_id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT USAGE ON SCHEMA public TO controlcore_user;
GRANT USAGE ON SCHEMA public TO grafana_user;
GRANT USAGE ON SCHEMA public TO sauron;


--
-- Name: TABLE sensor_data; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE public.sensor_data TO controlcore_user;
GRANT SELECT ON TABLE public.sensor_data TO sauron;


--
-- Name: TABLE _hyper_2_18_chunk; Type: ACL; Schema: _timescaledb_internal; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE _timescaledb_internal._hyper_2_18_chunk TO controlcore_user;
GRANT SELECT ON TABLE _timescaledb_internal._hyper_2_18_chunk TO sauron;


--
-- Name: TABLE _hyper_2_19_chunk; Type: ACL; Schema: _timescaledb_internal; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE _timescaledb_internal._hyper_2_19_chunk TO controlcore_user;
GRANT SELECT ON TABLE _timescaledb_internal._hyper_2_19_chunk TO sauron;


--
-- Name: TABLE _hyper_2_20_chunk; Type: ACL; Schema: _timescaledb_internal; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE _timescaledb_internal._hyper_2_20_chunk TO controlcore_user;
GRANT SELECT ON TABLE _timescaledb_internal._hyper_2_20_chunk TO sauron;


--
-- Name: TABLE control_log; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE public.control_log TO controlcore_user;
GRANT SELECT ON TABLE public.control_log TO grafana_user;
GRANT SELECT ON TABLE public.control_log TO sauron;


--
-- Name: SEQUENCE control_log_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,USAGE ON SEQUENCE public.control_log_id_seq TO controlcore_user;
GRANT SELECT ON SEQUENCE public.control_log_id_seq TO sauron;


--
-- Name: TABLE controller_boot_log; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE public.controller_boot_log TO controlcore_user;
GRANT SELECT ON TABLE public.controller_boot_log TO sauron;


--
-- Name: TABLE controller_health; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE public.controller_health TO controlcore_user;
GRANT SELECT ON TABLE public.controller_health TO sauron;


--
-- Name: TABLE controllers; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE public.controllers TO controlcore_user;
GRANT SELECT ON TABLE public.controllers TO sauron;


--
-- Name: TABLE locations; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE public.locations TO controlcore_user;
GRANT SELECT ON TABLE public.locations TO sauron;


--
-- Name: TABLE sensor_assignments; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE public.sensor_assignments TO controlcore_user;
GRANT SELECT ON TABLE public.sensor_assignments TO sauron;


--
-- Name: TABLE stations; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE public.stations TO controlcore_user;
GRANT SELECT ON TABLE public.stations TO sauron;


--
-- Name: TABLE watering_schedule; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE public.watering_schedule TO controlcore_user;
GRANT SELECT ON TABLE public.watering_schedule TO sauron;


--
-- Name: SEQUENCE watering_schedule_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,USAGE ON SEQUENCE public.watering_schedule_id_seq TO controlcore_user;
GRANT SELECT ON SEQUENCE public.watering_schedule_id_seq TO sauron;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT,INSERT,UPDATE ON TABLES TO controlcore_user;


--
-- PostgreSQL database dump complete
--

