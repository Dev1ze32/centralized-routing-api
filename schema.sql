--
-- PostgreSQL database dump
--

\restrict 33bsbWS8sh82q8TUcwdmNJMkefczPVsppD17uKwFLiH4pSYguToW66x5VHrhihc

-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4

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
-- Name: activities; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.activities (
    id integer NOT NULL,
    inventory_id character varying(50) NOT NULL,
    type character varying(20),
    item_id text,
    qty_required double precision,
    activity_name text,
    class character varying(10),
    class_1 character varying(10),
    pax integer,
    machine integer,
    time_min double precision,
    sort_order integer
);


ALTER TABLE public.activities OWNER TO postgres;

--
-- Name: activities_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.activities_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.activities_id_seq OWNER TO postgres;

--
-- Name: activities_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.activities_id_seq OWNED BY public.activities.id;


--
-- Name: line_activities; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.line_activities (
    id integer NOT NULL,
    production_line_code character varying(20) NOT NULL,
    activity_name text NOT NULL,
    sort_order integer NOT NULL,
    stage character varying(10)
);


ALTER TABLE public.line_activities OWNER TO postgres;

--
-- Name: line_activities_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.line_activities_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.line_activities_id_seq OWNER TO postgres;

--
-- Name: line_activities_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.line_activities_id_seq OWNED BY public.line_activities.id;


--
-- Name: production_lines; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.production_lines (
    production_line_code character varying(20) NOT NULL,
    production_line_name text NOT NULL
);


ALTER TABLE public.production_lines OWNER TO postgres;

--
-- Name: products; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products (
    inventory_id character varying(50) NOT NULL,
    revision_descr text,
    revision character varying(10),
    notes text,
    bm_production_line text,
    bm_production_line_code character varying(20),
    fg_production_line text,
    fg_production_line_code character varying(20),
    product_type character varying(50)
);


ALTER TABLE public.products OWNER TO postgres;

--
-- Name: activities id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activities ALTER COLUMN id SET DEFAULT nextval('public.activities_id_seq'::regclass);


--
-- Name: line_activities id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.line_activities ALTER COLUMN id SET DEFAULT nextval('public.line_activities_id_seq'::regclass);


--
-- Name: activities activities_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activities
    ADD CONSTRAINT activities_pkey PRIMARY KEY (id);


--
-- Name: line_activities line_activities_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.line_activities
    ADD CONSTRAINT line_activities_pkey PRIMARY KEY (id);


--
-- Name: line_activities line_activities_production_line_code_activity_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.line_activities
    ADD CONSTRAINT line_activities_production_line_code_activity_name_key UNIQUE (production_line_code, activity_name);


--
-- Name: production_lines production_lines_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.production_lines
    ADD CONSTRAINT production_lines_pkey PRIMARY KEY (production_line_code);


--
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (inventory_id);


--
-- Name: idx_activities_inventory_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_activities_inventory_id ON public.activities USING btree (inventory_id);


--
-- Name: idx_line_activities_line_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_line_activities_line_code ON public.line_activities USING btree (production_line_code);


--
-- Name: activities activities_inventory_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activities
    ADD CONSTRAINT activities_inventory_id_fkey FOREIGN KEY (inventory_id) REFERENCES public.products(inventory_id) ON DELETE CASCADE;


--
-- Name: products fk_products_bm_line; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT fk_products_bm_line FOREIGN KEY (bm_production_line_code) REFERENCES public.production_lines(production_line_code);


--
-- Name: products fk_products_fg_line; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT fk_products_fg_line FOREIGN KEY (fg_production_line_code) REFERENCES public.production_lines(production_line_code);


--
-- Name: products fk_products_production_line; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT fk_products_production_line FOREIGN KEY (bm_production_line_code) REFERENCES public.production_lines(production_line_code) ON UPDATE CASCADE;


--
-- Name: line_activities line_activities_production_line_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.line_activities
    ADD CONSTRAINT line_activities_production_line_code_fkey FOREIGN KEY (production_line_code) REFERENCES public.production_lines(production_line_code) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict 33bsbWS8sh82q8TUcwdmNJMkefczPVsppD17uKwFLiH4pSYguToW66x5VHrhihc

