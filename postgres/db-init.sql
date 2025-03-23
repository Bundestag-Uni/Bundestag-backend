BEGIN;


CREATE TABLE IF NOT EXISTS public.abgeordnete
(
    id character varying(255) COLLATE pg_catalog."default" NOT NULL,
    nachname character varying(255) COLLATE pg_catalog."default",
    vorname character varying(255) COLLATE pg_catalog."default",
    anrede_titel character varying(255) COLLATE pg_catalog."default",
    akad_titel character varying(255) COLLATE pg_catalog."default",
    geburtsdatum date,
    geburtsort character varying(255) COLLATE pg_catalog."default",
    geburtsland character varying(255) COLLATE pg_catalog."default",
    sterbedatum date,
    geschlecht character varying(50) COLLATE pg_catalog."default",
    familienstand character varying(255) COLLATE pg_catalog."default",
    religion character varying(255) COLLATE pg_catalog."default",
    beruf character varying(255) COLLATE pg_catalog."default",
    partei_kurz character varying(50) COLLATE pg_catalog."default",
    wahlperioden jsonb,
    CONSTRAINT abgeordnete_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.members
(
    id character varying(255) COLLATE pg_catalog."default" NOT NULL,
    nachname character varying(255) COLLATE pg_catalog."default",
    vorname character varying(255) COLLATE pg_catalog."default",
    typ character varying(255) COLLATE pg_catalog."default",
    wahlperiode integer,
    aktualisiert timestamp without time zone,
    titel character varying(255) COLLATE pg_catalog."default",
    datum date,
    basisdatum date,
    CONSTRAINT members_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.zwischenruf
(
    id serial NOT NULL,
    zwischenrufer_id character varying(255) COLLATE pg_catalog."default" NOT NULL,
    rede_id character varying(255) COLLATE pg_catalog."default" NOT NULL,
    datum date NOT NULL,
    inhalt text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT zwischenruf_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.reden
(
    id character varying(255) NOT NULL,
    redner_id character varying(255) NOT NULL,
    inhalt text NOT NULL,
    datum date NOT NULL,
    PRIMARY KEY (id)
);
CREATE TABLE IF NOT EXISTS public.reden_efficiency
{
    id character varying(255) NOT NULL REFERENCES public.reden (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID,
    num_tokens integer NOT NULL,
    num_nodes integer NOT NULL,
    num_edges integer NOT NULL,
    efficiency double precision  NOT NULL,
    CONSTRAINT reden_effi_pkey PRIMARY KEY (id)
};
ALTER TABLE IF EXISTS public.zwischenruf
    ADD FOREIGN KEY (rede_id)
    REFERENCES public.reden (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;

END;
