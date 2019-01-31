CREATE DATABASE "hlcup18"
  WITH OWNER "postgres"
  ENCODING 'UTF8'
  LC_COLLATE = 'en_US.UTF-8'
  LC_CTYPE = 'en_US.UTF-8'
  TEMPLATE template0;

\connect hlcup18;

CREATE TABLE accounts (
  id INT PRIMARY KEY,
  email VARCHAR(100) UNIQUE,
  email_domain VARCHAR(100) NULL,
  fname VARCHAR(50) NULL,
  sname VARCHAR(50) NULL,
  phone VARCHAR(16) NULL,
  phone_code VARCHAR(3) NULL,
  sex CHAR(1),
  birth INT,
  birth_year INT,
  country VARCHAR(50) NULL,
  city VARCHAR(50) NULL,
  joined INT,
  joined_year INT,
  status VARCHAR(10),
  interests VARCHAR(100)[] NULL,
  premium_start INT NULL,
  premium_finish INT NULL,
  likees_ids INT[] NULL
);

CREATE TABLE likes (
  liker_id INT, -- REFERENCES accounts (id),
  likee_id INT, -- REFERENCES accounts (id),
  ts INT
);

CREATE FUNCTION array_intersect(anyarray, anyarray)
  RETURNS anyarray
  language sql
as $FUNCTION$
    SELECT ARRAY(
        SELECT UNNEST($1)
        INTERSECT
        SELECT UNNEST($2)
    );
$FUNCTION$;
