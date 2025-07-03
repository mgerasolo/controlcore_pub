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
    controller_id text NOT NULL,
    sensor_id text NOT NULL,
    sensor_type text NOT NULL,
    source_id text NOT NULL,
    pin integer,
    value real,
    unit text,
    received_at timestamp with time zone DEFAULT now() NOT NULL,
    location_id text NOT NULL
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
-- Name: _hyper_2_21_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._hyper_2_21_chunk (
    CONSTRAINT constraint_21 CHECK (((received_at >= '2025-07-02 20:00:00-04'::timestamp with time zone) AND (received_at < '2025-07-09 20:00:00-04'::timestamp with time zone)))
)
INHERITS (public.sensor_data);


ALTER TABLE _timescaledb_internal._hyper_2_21_chunk OWNER TO postgres;

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
    received_at timestamp with time zone DEFAULT now(),
    source_id text,
    duration integer,
    "timestamp" bigint
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
-- Name: forecast_accuracy; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.forecast_accuracy (
    run_time timestamp with time zone NOT NULL,
    mae double precision,
    rmse double precision
);


ALTER TABLE public.forecast_accuracy OWNER TO postgres;

--
-- Name: forecast_accuracy_lead; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.forecast_accuracy_lead (
    run_time timestamp with time zone,
    lead_hours double precision,
    mae double precision,
    rmse double precision
);


ALTER TABLE public.forecast_accuracy_lead OWNER TO postgres;

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
-- Name: module_status; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.module_status (
    module_name text NOT NULL,
    last_run_time timestamp with time zone NOT NULL,
    status text,
    details jsonb
);


ALTER TABLE public.module_status OWNER TO postgres;

--
-- Name: sensor_assignments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sensor_assignments (
    controller_id text NOT NULL,
    pin integer NOT NULL,
    sensor_id text,
    sensor_type text,
    unit text,
    location_hint text,
    config_source text,
    assigned_at timestamp with time zone DEFAULT now(),
    location_id text
);


ALTER TABLE public.sensor_assignments OWNER TO postgres;

--
-- Name: session_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.session_logs (
    id integer NOT NULL,
    user_id integer NOT NULL,
    action text NOT NULL,
    session_token text,
    ip_address text,
    user_agent text,
    "timestamp" timestamp with time zone DEFAULT now(),
    CONSTRAINT session_logs_action_check CHECK ((action = ANY (ARRAY['login'::text, 'logout'::text])))
);


ALTER TABLE public.session_logs OWNER TO postgres;

--
-- Name: session_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.session_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.session_logs_id_seq OWNER TO postgres;

--
-- Name: session_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.session_logs_id_seq OWNED BY public.session_logs.id;


--
-- Name: stations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.stations (
    station_id text NOT NULL,
    location_id text,
    label text,
    notes text,
    is_active boolean DEFAULT true
);


ALTER TABLE public.stations OWNER TO postgres;

--
-- Name: system_config; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.system_config (
    id integer NOT NULL,
    config_key character varying(100) NOT NULL,
    config_value text,
    description text,
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.system_config OWNER TO postgres;

--
-- Name: system_config_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.system_config_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.system_config_id_seq OWNER TO postgres;

--
-- Name: system_config_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.system_config_id_seq OWNED BY public.system_config.id;


--
-- Name: user_sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_sessions (
    id integer NOT NULL,
    user_id integer,
    session_token character varying(255) NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.user_sessions OWNER TO postgres;

--
-- Name: user_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_sessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_sessions_id_seq OWNER TO postgres;

--
-- Name: user_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_sessions_id_seq OWNED BY public.user_sessions.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying(255) NOT NULL,
    password_hash character varying(255) NOT NULL,
    first_name character varying(100),
    last_name character varying(100),
    role character varying(50) DEFAULT 'user'::character varying,
    demo_mode boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    last_login timestamp with time zone,
    is_active boolean DEFAULT true
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


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
-- Name: _hyper_2_21_chunk received_at; Type: DEFAULT; Schema: _timescaledb_internal; Owner: postgres
--

ALTER TABLE ONLY _timescaledb_internal._hyper_2_21_chunk ALTER COLUMN received_at SET DEFAULT now();


--
-- Name: control_log id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.control_log ALTER COLUMN id SET DEFAULT nextval('public.control_log_id_seq'::regclass);


--
-- Name: session_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.session_logs ALTER COLUMN id SET DEFAULT nextval('public.session_logs_id_seq'::regclass);


--
-- Name: system_config id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_config ALTER COLUMN id SET DEFAULT nextval('public.system_config_id_seq'::regclass);


--
-- Name: user_sessions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_sessions ALTER COLUMN id SET DEFAULT nextval('public.user_sessions_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


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
-- Name: forecast_accuracy forecast_accuracy_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forecast_accuracy
    ADD CONSTRAINT forecast_accuracy_pkey PRIMARY KEY (run_time);


--
-- Name: locations locations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.locations
    ADD CONSTRAINT locations_pkey PRIMARY KEY (location_id);


--
-- Name: module_status module_status_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.module_status
    ADD CONSTRAINT module_status_pkey PRIMARY KEY (module_name);


--
-- Name: sensor_assignments sensor_assignments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sensor_assignments
    ADD CONSTRAINT sensor_assignments_pkey PRIMARY KEY (controller_id, pin);


--
-- Name: session_logs session_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.session_logs
    ADD CONSTRAINT session_logs_pkey PRIMARY KEY (id);


--
-- Name: stations stations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stations
    ADD CONSTRAINT stations_pkey PRIMARY KEY (station_id);


--
-- Name: system_config system_config_config_key_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_config
    ADD CONSTRAINT system_config_config_key_key UNIQUE (config_key);


--
-- Name: system_config system_config_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_config
    ADD CONSTRAINT system_config_pkey PRIMARY KEY (id);


--
-- Name: user_sessions user_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_pkey PRIMARY KEY (id);


--
-- Name: user_sessions user_sessions_session_token_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_session_token_key UNIQUE (session_token);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: watering_schedule watering_schedule_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.watering_schedule
    ADD CONSTRAINT watering_schedule_pkey PRIMARY KEY (id);


--
-- Name: _hyper_2_18_chunk_sensor_data_location_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_18_chunk_sensor_data_location_idx ON _timescaledb_internal._hyper_2_18_chunk USING btree (location_id);


--
-- Name: _hyper_2_18_chunk_sensor_data_received_at_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_18_chunk_sensor_data_received_at_idx ON _timescaledb_internal._hyper_2_18_chunk USING btree (received_at DESC);


--
-- Name: _hyper_2_19_chunk_sensor_data_location_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_19_chunk_sensor_data_location_idx ON _timescaledb_internal._hyper_2_19_chunk USING btree (location_id);


--
-- Name: _hyper_2_19_chunk_sensor_data_received_at_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_19_chunk_sensor_data_received_at_idx ON _timescaledb_internal._hyper_2_19_chunk USING btree (received_at DESC);


--
-- Name: _hyper_2_20_chunk_sensor_data_location_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_20_chunk_sensor_data_location_idx ON _timescaledb_internal._hyper_2_20_chunk USING btree (location_id);


--
-- Name: _hyper_2_20_chunk_sensor_data_received_at_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_20_chunk_sensor_data_received_at_idx ON _timescaledb_internal._hyper_2_20_chunk USING btree (received_at DESC);


--
-- Name: _hyper_2_21_chunk_sensor_data_location_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_21_chunk_sensor_data_location_idx ON _timescaledb_internal._hyper_2_21_chunk USING btree (location_id);


--
-- Name: _hyper_2_21_chunk_sensor_data_received_at_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _hyper_2_21_chunk_sensor_data_received_at_idx ON _timescaledb_internal._hyper_2_21_chunk USING btree (received_at DESC);


--
-- Name: idx_user_sessions_expires; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_user_sessions_expires ON public.user_sessions USING btree (expires_at);


--
-- Name: idx_user_sessions_token; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_user_sessions_token ON public.user_sessions USING btree (session_token);


--
-- Name: idx_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_users_email ON public.users USING btree (email);


--
-- Name: sensor_assignments_location_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX sensor_assignments_location_idx ON public.sensor_assignments USING btree (location_id);


--
-- Name: sensor_data_location_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX sensor_data_location_idx ON public.sensor_data USING btree (location_id);


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
-- Name: session_logs session_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.session_logs
    ADD CONSTRAINT session_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: stations stations_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stations
    ADD CONSTRAINT stations_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.locations(location_id);


--
-- Name: user_sessions user_sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT USAGE ON SCHEMA public TO controlcore_user;
GRANT USAGE ON SCHEMA public TO grafana_user;
GRANT USAGE ON SCHEMA public TO sauron;


--
-- Name: TABLE sensor_data; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.sensor_data TO controlcore_user;
GRANT SELECT ON TABLE public.sensor_data TO sauron;


--
-- Name: TABLE _hyper_2_18_chunk; Type: ACL; Schema: _timescaledb_internal; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE _timescaledb_internal._hyper_2_18_chunk TO controlcore_user;
GRANT SELECT ON TABLE _timescaledb_internal._hyper_2_18_chunk TO sauron;


--
-- Name: TABLE _hyper_2_19_chunk; Type: ACL; Schema: _timescaledb_internal; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE _timescaledb_internal._hyper_2_19_chunk TO controlcore_user;
GRANT SELECT ON TABLE _timescaledb_internal._hyper_2_19_chunk TO sauron;


--
-- Name: TABLE _hyper_2_20_chunk; Type: ACL; Schema: _timescaledb_internal; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE _timescaledb_internal._hyper_2_20_chunk TO controlcore_user;
GRANT SELECT ON TABLE _timescaledb_internal._hyper_2_20_chunk TO sauron;


--
-- Name: TABLE _hyper_2_21_chunk; Type: ACL; Schema: _timescaledb_internal; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE _timescaledb_internal._hyper_2_21_chunk TO controlcore_user;
GRANT SELECT ON TABLE _timescaledb_internal._hyper_2_21_chunk TO sauron;


--
-- Name: TABLE control_log; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.control_log TO controlcore_user;
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

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.controller_boot_log TO controlcore_user;
GRANT SELECT ON TABLE public.controller_boot_log TO sauron;


--
-- Name: TABLE controller_health; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.controller_health TO controlcore_user;
GRANT SELECT ON TABLE public.controller_health TO sauron;


--
-- Name: TABLE controllers; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.controllers TO controlcore_user;
GRANT SELECT ON TABLE public.controllers TO sauron;


--
-- Name: TABLE forecast_accuracy; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.forecast_accuracy TO controlcore_user;
GRANT SELECT ON TABLE public.forecast_accuracy TO sauron;


--
-- Name: TABLE forecast_accuracy_lead; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.forecast_accuracy_lead TO controlcore_user;
GRANT SELECT ON TABLE public.forecast_accuracy_lead TO sauron;


--
-- Name: TABLE locations; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.locations TO controlcore_user;
GRANT SELECT ON TABLE public.locations TO sauron;


--
-- Name: TABLE module_status; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.module_status TO controlcore_user;
GRANT SELECT ON TABLE public.module_status TO sauron;


--
-- Name: TABLE sensor_assignments; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.sensor_assignments TO controlcore_user;
GRANT SELECT ON TABLE public.sensor_assignments TO sauron;


--
-- Name: TABLE session_logs; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.session_logs TO controlcore_user;
GRANT SELECT ON TABLE public.session_logs TO sauron;


--
-- Name: SEQUENCE session_logs_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,USAGE ON SEQUENCE public.session_logs_id_seq TO controlcore_user;


--
-- Name: TABLE stations; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.stations TO controlcore_user;
GRANT SELECT ON TABLE public.stations TO sauron;


--
-- Name: TABLE system_config; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.system_config TO controlcore_user;
GRANT SELECT ON TABLE public.system_config TO sauron;


--
-- Name: SEQUENCE system_config_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,USAGE ON SEQUENCE public.system_config_id_seq TO controlcore_user;


--
-- Name: TABLE user_sessions; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.user_sessions TO controlcore_user;
GRANT SELECT ON TABLE public.user_sessions TO sauron;


--
-- Name: SEQUENCE user_sessions_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,USAGE ON SEQUENCE public.user_sessions_id_seq TO controlcore_user;


--
-- Name: TABLE users; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.users TO controlcore_user;
GRANT SELECT ON TABLE public.users TO sauron;


--
-- Name: SEQUENCE users_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,USAGE ON SEQUENCE public.users_id_seq TO controlcore_user;


--
-- Name: TABLE watering_schedule; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.watering_schedule TO controlcore_user;
GRANT SELECT ON TABLE public.watering_schedule TO sauron;


--
-- Name: SEQUENCE watering_schedule_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,USAGE ON SEQUENCE public.watering_schedule_id_seq TO controlcore_user;
GRANT SELECT ON SEQUENCE public.watering_schedule_id_seq TO sauron;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT ON TABLES TO sauron;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT,INSERT,UPDATE ON TABLES TO controlcore_user;


--
-- PostgreSQL database dump complete
--

