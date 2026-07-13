CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS takapay_posts (
    id BIGINT,
    platform VARCHAR(50),
    timestamp TIMESTAMP NOT NULL,
    author VARCHAR(255),
    text TEXT,
    language VARCHAR(20),
    brand_mention BOOLEAN,
    sentiment VARCHAR(20),
    sentiment_score INTEGER,
    topic VARCHAR(100),
    reactions INTEGER,
    comments INTEGER,
    PRIMARY KEY (id, timestamp)
);

SELECT create_hypertable('takapay_posts', 'timestamp', if_not_exists => TRUE);
