DROP TABLE IF EXISTS url_checks;
DROP TABLE IF EXISTS urls;
CREATE TABLE urls (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE url_checks (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    url_id bigint REFERENCES urls(id) NOT NULL,
    status_code int NOT NULL,
    h1 VARCHAR(255),
    title VARCHAR(255),
    description text,
    created_at TIMESTAMP NOT NULL
);