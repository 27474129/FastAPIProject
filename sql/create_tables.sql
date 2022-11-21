CREATE TABLE clients (
    id SERIAL,
    phone numeric(15) NOT NULL,
    operator_code INT NOT NULL,
    tag VARCHAR NOT NULL,
    time_zone VARCHAR NOT NULL
);

CREATE TABLE mailings (
    id SERIAL,
    start_time TIMESTAMP NOT NULL,
    message VARCHAR NOT NULL,
    filters VARCHAR,
    end_time TIMESTAMP NOT NULL
);

CREATE TABLE messages (
    id SERIAL,
    creation_time TIMESTAMP NOT NULL,
    status VARCHAR NOT NULL,
    mailing_id INT NOT NULL,
    client_id INT NOT NULL
);
