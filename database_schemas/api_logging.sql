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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: api_call_types; Type: TABLE; Schema: public; Owner: sauron
--

CREATE TABLE public.api_call_types (
    api_call_type_id integer NOT NULL,
    platform text NOT NULL,
    api_call_type text NOT NULL,
    api_call_prototype text NOT NULL
);


ALTER TABLE public.api_call_types OWNER TO sauron;

--
-- Name: api_call_types_api_call_type_id_seq; Type: SEQUENCE; Schema: public; Owner: sauron
--

CREATE SEQUENCE public.api_call_types_api_call_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.api_call_types_api_call_type_id_seq OWNER TO sauron;

--
-- Name: api_call_types_api_call_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sauron
--

ALTER SEQUENCE public.api_call_types_api_call_type_id_seq OWNED BY public.api_call_types.api_call_type_id;


--
-- Name: api_calls; Type: TABLE; Schema: public; Owner: sauron
--

CREATE TABLE public.api_calls (
    api_call_id integer NOT NULL,
    call_timestamp bigint NOT NULL,
    api_call_type_id integer,
    call_event text NOT NULL,
    request_payload text,
    response_code integer,
    response_message text,
    retry_count integer DEFAULT 0,
    call_log_message text
);


ALTER TABLE public.api_calls OWNER TO sauron;

--
-- Name: api_calls_api_call_id_seq; Type: SEQUENCE; Schema: public; Owner: sauron
--

CREATE SEQUENCE public.api_calls_api_call_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.api_calls_api_call_id_seq OWNER TO sauron;

--
-- Name: api_calls_api_call_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sauron
--

ALTER SEQUENCE public.api_calls_api_call_id_seq OWNED BY public.api_calls.api_call_id;


--
-- Name: api_script_tracking; Type: TABLE; Schema: public; Owner: sauron
--

CREATE TABLE public.api_script_tracking (
    log_id integer NOT NULL,
    script_name text NOT NULL,
    platform text NOT NULL,
    api_call_alt_name text NOT NULL,
    status text NOT NULL,
    last_checked timestamp without time zone NOT NULL,
    requests_made_today integer DEFAULT 0 NOT NULL,
    daily_limit_reached boolean DEFAULT false,
    previous_status text,
    force_restart boolean DEFAULT false,
    stopped_reason text
);


ALTER TABLE public.api_script_tracking OWNER TO sauron;

--
-- Name: api_logging_log_id_seq; Type: SEQUENCE; Schema: public; Owner: sauron
--

CREATE SEQUENCE public.api_logging_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.api_logging_log_id_seq OWNER TO sauron;

--
-- Name: api_logging_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sauron
--

ALTER SEQUENCE public.api_logging_log_id_seq OWNED BY public.api_script_tracking.log_id;


--
-- Name: credentials; Type: TABLE; Schema: public; Owner: sauron
--

CREATE TABLE public.credentials (
    key_name text NOT NULL,
    username text NOT NULL,
    password text NOT NULL,
    target_service text,
    notes text,
    dbname text
);


ALTER TABLE public.credentials OWNER TO sauron;

--
-- Name: sql_handling; Type: TABLE; Schema: public; Owner: sauron
--

CREATE TABLE public.sql_handling (
    sql_log_id integer NOT NULL,
    api_call_id integer,
    insert_timestamp bigint NOT NULL,
    insert_status text NOT NULL,
    error_message text,
    retry_count integer DEFAULT 0
);


ALTER TABLE public.sql_handling OWNER TO sauron;

--
-- Name: sql_handling_sql_log_id_seq; Type: SEQUENCE; Schema: public; Owner: sauron
--

CREATE SEQUENCE public.sql_handling_sql_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sql_handling_sql_log_id_seq OWNER TO sauron;

--
-- Name: sql_handling_sql_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sauron
--

ALTER SEQUENCE public.sql_handling_sql_log_id_seq OWNED BY public.sql_handling.sql_log_id;


--
-- Name: api_call_types api_call_type_id; Type: DEFAULT; Schema: public; Owner: sauron
--

ALTER TABLE ONLY public.api_call_types ALTER COLUMN api_call_type_id SET DEFAULT nextval('public.api_call_types_api_call_type_id_seq'::regclass);


--
-- Name: api_calls api_call_id; Type: DEFAULT; Schema: public; Owner: sauron
--

ALTER TABLE ONLY public.api_calls ALTER COLUMN api_call_id SET DEFAULT nextval('public.api_calls_api_call_id_seq'::regclass);


--
-- Name: api_script_tracking log_id; Type: DEFAULT; Schema: public; Owner: sauron
--

ALTER TABLE ONLY public.api_script_tracking ALTER COLUMN log_id SET DEFAULT nextval('public.api_logging_log_id_seq'::regclass);


--
-- Name: sql_handling sql_log_id; Type: DEFAULT; Schema: public; Owner: sauron
--

ALTER TABLE ONLY public.sql_handling ALTER COLUMN sql_log_id SET DEFAULT nextval('public.sql_handling_sql_log_id_seq'::regclass);


--
-- Name: api_call_types api_call_types_pkey; Type: CONSTRAINT; Schema: public; Owner: sauron
--

ALTER TABLE ONLY public.api_call_types
    ADD CONSTRAINT api_call_types_pkey PRIMARY KEY (api_call_type_id);


--
-- Name: api_calls api_calls_pkey; Type: CONSTRAINT; Schema: public; Owner: sauron
--

ALTER TABLE ONLY public.api_calls
    ADD CONSTRAINT api_calls_pkey PRIMARY KEY (api_call_id);


--
-- Name: api_script_tracking api_logging_pkey; Type: CONSTRAINT; Schema: public; Owner: sauron
--

ALTER TABLE ONLY public.api_script_tracking
    ADD CONSTRAINT api_logging_pkey PRIMARY KEY (log_id);


--
-- Name: credentials credentials_pkey; Type: CONSTRAINT; Schema: public; Owner: sauron
--

ALTER TABLE ONLY public.credentials
    ADD CONSTRAINT credentials_pkey PRIMARY KEY (key_name);


--
-- Name: sql_handling sql_handling_pkey; Type: CONSTRAINT; Schema: public; Owner: sauron
--

ALTER TABLE ONLY public.sql_handling
    ADD CONSTRAINT sql_handling_pkey PRIMARY KEY (sql_log_id);


--
-- Name: api_script_tracking unique_script_platform_type; Type: CONSTRAINT; Schema: public; Owner: sauron
--

ALTER TABLE ONLY public.api_script_tracking
    ADD CONSTRAINT unique_script_platform_type UNIQUE (script_name, platform, api_call_alt_name);


--
-- Name: api_calls api_calls_api_call_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sauron
--

ALTER TABLE ONLY public.api_calls
    ADD CONSTRAINT api_calls_api_call_type_id_fkey FOREIGN KEY (api_call_type_id) REFERENCES public.api_call_types(api_call_type_id);


--
-- Name: sql_handling sql_handling_api_call_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sauron
--

ALTER TABLE ONLY public.sql_handling
    ADD CONSTRAINT sql_handling_api_call_id_fkey FOREIGN KEY (api_call_id) REFERENCES public.api_calls(api_call_id);


--
-- PostgreSQL database dump complete
--

