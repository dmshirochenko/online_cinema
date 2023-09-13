CREATE SCHEMA IF NOT EXISTS content;
SET search_path TO content,public;

CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    creation_date DATE,
    rating FLOAT,
    type TEXT NOT NULL,
    file_path TEXT,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
); 

CREATE TABLE IF NOT EXISTS content.person (
	id uuid PRIMARY KEY,
	full_name VARCHAR(64) NOT NULL,
	created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),

  CONSTRAINT name_unique UNIQUE (full_name)
);

CREATE TABLE IF NOT EXISTS content.genre (
	id uuid PRIMARY KEY,
	name VARCHAR(64) NOT NULL,
	description TEXT,
	created_at timestamp with time zone DEFAULT now(),
	updated_at timestamp with time zone DEFAULT now(),

  CONSTRAINT name_unqiue UNIQUE (name)
);

CREATE TABLE IF NOT EXISTS content.person_film_work (
	id uuid PRIMARY KEY,
	person_id uuid NOT NULL REFERENCES content.person(id) ON DELETE	CASCADE,
	film_work_id uuid NOT NULL REFERENCES content.film_work(id) ON DELETE CASCADE,
	role VARCHAR(64),
	created_at timestamp with time zone DEFAULT now()
);

CREATE UNIQUE INDEX film_work_person_idx ON content.person_film_work (film_work_id, person_id, role);

CREATE TABLE IF NOT EXISTS content.genre_film_work (
	id uuid PRIMARY KEY,
	genre_id uuid NOT NULL REFERENCES content.genre(id) ON DELETE CASCADE,
	film_work_id uuid NOT NULL REFERENCES content.film_work(id) ON DELETE CASCADE,
	created_at timestamp with time zone DEFAULT now()
);

CREATE UNIQUE INDEX film_work_genre_idx ON content.genre_film_work (film_work_id, genre_id);
