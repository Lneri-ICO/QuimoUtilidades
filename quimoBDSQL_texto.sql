--
-- PostgreSQL database dump
--

-- Dumped from database version 17.2
-- Dumped by pg_dump version 17.2

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
-- Name: comprasmateriaprima; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.comprasmateriaprima (
    id_compra integer NOT NULL,
    id_mp integer NOT NULL,
    id_proveedor integer NOT NULL,
    fecha_compra date DEFAULT CURRENT_DATE NOT NULL,
    cantidad numeric(10,3) NOT NULL,
    precio_unitario numeric(10,2) NOT NULL,
    tipo_moneda character varying(3) NOT NULL,
    total numeric(12,2) GENERATED ALWAYS AS ((cantidad * precio_unitario)) STORED,
    estatus_compra boolean DEFAULT true NOT NULL,
    comentarios text,
    usuario_registro character varying(50),
    CONSTRAINT comprasmateriaprima_tipo_moneda_check CHECK (((tipo_moneda)::text = ANY (ARRAY[('MXN'::character varying)::text, ('USD'::character varying)::text, ('EUR'::character varying)::text])))
);


ALTER TABLE public.comprasmateriaprima OWNER TO postgres;

--
-- Name: comprasmateriaprima_id_compra_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.comprasmateriaprima_id_compra_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.comprasmateriaprima_id_compra_seq OWNER TO postgres;

--
-- Name: comprasmateriaprima_id_compra_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.comprasmateriaprima_id_compra_seq OWNED BY public.comprasmateriaprima.id_compra;


--
-- Name: formulas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.formulas (
    id_formula_mp integer NOT NULL,
    id_producto integer NOT NULL,
    id_mp integer NOT NULL,
    porcentaje numeric(5,2) NOT NULL
);


ALTER TABLE public.formulas OWNER TO postgres;

--
-- Name: formulas_id_formula_mp_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.formulas ALTER COLUMN id_formula_mp ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.formulas_id_formula_mp_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: materiasprimas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.materiasprimas (
    id_mp integer NOT NULL,
    proveedor integer NOT NULL,
    nombre_mp character varying(255) NOT NULL,
    unidad_medida_mp character varying(10) NOT NULL,
    cantidad_comprada_mp numeric(10,3) NOT NULL,
    estatus_mp boolean DEFAULT true NOT NULL,
    fecha_mp date DEFAULT CURRENT_DATE NOT NULL,
    costo_unitario_mp numeric(10,2) NOT NULL,
    tipo_moneda character varying(3) NOT NULL,
    total_mp numeric(12,2) NOT NULL,
    CONSTRAINT chk_tipo_moneda_mp CHECK (((tipo_moneda)::text = ANY (ARRAY[('MXN'::character varying)::text, ('USD'::character varying)::text, ('EUR'::character varying)::text]))),
    CONSTRAINT chk_unidad_medida_mp CHECK (((unidad_medida_mp)::text = ANY (ARRAY[('KG'::character varying)::text, ('L'::character varying)::text, ('PZA'::character varying)::text, ('CAJA'::character varying)::text, ('PAR'::character varying)::text])))
);


ALTER TABLE public.materiasprimas OWNER TO postgres;

--
-- Name: materiasprimas_id_mp_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.materiasprimas_id_mp_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.materiasprimas_id_mp_seq OWNER TO postgres;

--
-- Name: materiasprimas_id_mp_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.materiasprimas_id_mp_seq OWNED BY public.materiasprimas.id_mp;


--
-- Name: produccion; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.produccion (
    id_produccion integer NOT NULL,
    fecha date DEFAULT CURRENT_DATE NOT NULL,
    producto_id integer NOT NULL,
    dia character(1) NOT NULL,
    cantidad numeric(10,3) NOT NULL,
    CONSTRAINT produccion_dia_check CHECK ((dia = ANY (ARRAY['L'::bpchar, 'M'::bpchar, 'J'::bpchar, 'V'::bpchar, 'S'::bpchar, 'D'::bpchar])))
);


ALTER TABLE public.produccion OWNER TO postgres;

--
-- Name: produccion_id_produccion_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.produccion_id_produccion_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.produccion_id_produccion_seq OWNER TO postgres;

--
-- Name: produccion_id_produccion_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.produccion_id_produccion_seq OWNED BY public.produccion.id_produccion;


--
-- Name: productos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.productos (
    id_producto integer NOT NULL,
    nombre_producto character varying(255) NOT NULL,
    unidad_medida_producto character varying(10) NOT NULL,
    area_producto character varying(15) NOT NULL,
    cantidad_producto numeric(10,3) NOT NULL,
    estatus_producto boolean DEFAULT true NOT NULL,
    fecha_producto date DEFAULT CURRENT_DATE NOT NULL,
    CONSTRAINT chk_area_producto CHECK (((area_producto)::text = ANY (ARRAY[('QUIMO'::character varying)::text, ('QUIMO CLEAN'::character varying)::text]))),
    CONSTRAINT chk_unidad_medida_producto CHECK (((unidad_medida_producto)::text = ANY (ARRAY[('KG'::character varying)::text, ('L'::character varying)::text, ('PZA'::character varying)::text, ('CAJA'::character varying)::text, ('PAR'::character varying)::text])))
);


ALTER TABLE public.productos OWNER TO postgres;

--
-- Name: productos_id_producto_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.productos_id_producto_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.productos_id_producto_seq OWNER TO postgres;

--
-- Name: productos_id_producto_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.productos_id_producto_seq OWNED BY public.productos.id_producto;


--
-- Name: productosreventa; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.productosreventa (
    id_prev integer NOT NULL,
    proveedor integer NOT NULL,
    nombre_prev character varying(255) NOT NULL,
    unidad_medida_prev character varying(10) NOT NULL,
    area_prev character varying(15) NOT NULL,
    cantidad_prev numeric(10,3) NOT NULL,
    estatus_prev boolean DEFAULT true NOT NULL,
    CONSTRAINT chk_area_prev CHECK (((area_prev)::text = ANY (ARRAY[('QUIMO'::character varying)::text, ('QUIMO CLEAN'::character varying)::text]))),
    CONSTRAINT chk_unidad_medida_prev CHECK (((unidad_medida_prev)::text = ANY (ARRAY[('KG'::character varying)::text, ('L'::character varying)::text, ('PZA'::character varying)::text, ('CAJA'::character varying)::text, ('PAR'::character varying)::text])))
);


ALTER TABLE public.productosreventa OWNER TO postgres;

--
-- Name: productosreventa_id_prev_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.productosreventa_id_prev_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.productosreventa_id_prev_seq OWNER TO postgres;

--
-- Name: productosreventa_id_prev_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.productosreventa_id_prev_seq OWNED BY public.productosreventa.id_prev;


--
-- Name: proveedor; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.proveedor (
    id_proveedor integer NOT NULL,
    nombre_proveedor character varying(100) NOT NULL,
    telefono_proveedor character varying(20),
    email_proveedor character varying(255)
);


ALTER TABLE public.proveedor OWNER TO postgres;

--
-- Name: proveedor_id_proveedor_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.proveedor_id_proveedor_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.proveedor_id_proveedor_seq OWNER TO postgres;

--
-- Name: proveedor_id_proveedor_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.proveedor_id_proveedor_seq OWNED BY public.proveedor.id_proveedor;


--
-- Name: comprasmateriaprima id_compra; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comprasmateriaprima ALTER COLUMN id_compra SET DEFAULT nextval('public.comprasmateriaprima_id_compra_seq'::regclass);


--
-- Name: materiasprimas id_mp; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.materiasprimas ALTER COLUMN id_mp SET DEFAULT nextval('public.materiasprimas_id_mp_seq'::regclass);


--
-- Name: produccion id_produccion; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.produccion ALTER COLUMN id_produccion SET DEFAULT nextval('public.produccion_id_produccion_seq'::regclass);


--
-- Name: productos id_producto; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.productos ALTER COLUMN id_producto SET DEFAULT nextval('public.productos_id_producto_seq'::regclass);


--
-- Name: productosreventa id_prev; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.productosreventa ALTER COLUMN id_prev SET DEFAULT nextval('public.productosreventa_id_prev_seq'::regclass);


--
-- Name: proveedor id_proveedor; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.proveedor ALTER COLUMN id_proveedor SET DEFAULT nextval('public.proveedor_id_proveedor_seq'::regclass);


--
-- Name: comprasmateriaprima comprasmateriaprima_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comprasmateriaprima
    ADD CONSTRAINT comprasmateriaprima_pkey PRIMARY KEY (id_compra);


--
-- Name: formulas formulas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.formulas
    ADD CONSTRAINT formulas_pkey PRIMARY KEY (id_formula_mp);


--
-- Name: materiasprimas materiasprimas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.materiasprimas
    ADD CONSTRAINT materiasprimas_pkey PRIMARY KEY (id_mp);


--
-- Name: produccion produccion_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.produccion
    ADD CONSTRAINT produccion_pkey PRIMARY KEY (id_produccion);


--
-- Name: productos productos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.productos
    ADD CONSTRAINT productos_pkey PRIMARY KEY (id_producto);


--
-- Name: productosreventa productosreventa_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.productosreventa
    ADD CONSTRAINT productosreventa_pkey PRIMARY KEY (id_prev);


--
-- Name: proveedor proveedor_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.proveedor
    ADD CONSTRAINT proveedor_pkey PRIMARY KEY (id_proveedor);


--
-- Name: idx_compras_fecha; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_compras_fecha ON public.comprasmateriaprima USING btree (fecha_compra);


--
-- Name: idx_compras_moneda; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_compras_moneda ON public.comprasmateriaprima USING btree (tipo_moneda);


--
-- Name: idx_compras_mp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_compras_mp ON public.comprasmateriaprima USING btree (id_mp);


--
-- Name: idx_compras_proveedor; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_compras_proveedor ON public.comprasmateriaprima USING btree (id_proveedor);


--
-- Name: idx_materiasprimas_fecha_proveedor; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_materiasprimas_fecha_proveedor ON public.materiasprimas USING btree (fecha_mp, proveedor);


--
-- Name: idx_productos_fecha; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_productos_fecha ON public.productos USING btree (fecha_producto);


--
-- Name: idx_productosreventa_proveedor; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_productosreventa_proveedor ON public.productosreventa USING btree (proveedor);


--
-- Name: comprasmateriaprima comprasmateriaprima_id_mp_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comprasmateriaprima
    ADD CONSTRAINT comprasmateriaprima_id_mp_fkey FOREIGN KEY (id_mp) REFERENCES public.materiasprimas(id_mp);


--
-- Name: comprasmateriaprima comprasmateriaprima_id_proveedor_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comprasmateriaprima
    ADD CONSTRAINT comprasmateriaprima_id_proveedor_fkey FOREIGN KEY (id_proveedor) REFERENCES public.proveedor(id_proveedor);


--
-- Name: productosreventa fk_productosreventa_proveedor; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.productosreventa
    ADD CONSTRAINT fk_productosreventa_proveedor FOREIGN KEY (proveedor) REFERENCES public.proveedor(id_proveedor);


--
-- Name: materiasprimas fk_proveedor_mp; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.materiasprimas
    ADD CONSTRAINT fk_proveedor_mp FOREIGN KEY (proveedor) REFERENCES public.proveedor(id_proveedor) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: productosreventa fk_proveedor_prev; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.productosreventa
    ADD CONSTRAINT fk_proveedor_prev FOREIGN KEY (proveedor) REFERENCES public.proveedor(id_proveedor) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: formulas formulas_id_mp_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.formulas
    ADD CONSTRAINT formulas_id_mp_fkey FOREIGN KEY (id_mp) REFERENCES public.materiasprimas(id_mp);


--
-- Name: formulas formulas_id_producto_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.formulas
    ADD CONSTRAINT formulas_id_producto_fkey FOREIGN KEY (id_producto) REFERENCES public.productos(id_producto);


--
-- Name: produccion produccion_producto_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.produccion
    ADD CONSTRAINT produccion_producto_id_fkey FOREIGN KEY (producto_id) REFERENCES public.productos(id_producto);


--
-- PostgreSQL database dump complete
--

