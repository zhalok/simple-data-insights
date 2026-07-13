CREATE TABLE IF NOT EXISTS takapay_posts (
    id BIGINT PRIMARY KEY,
    platform VARCHAR(50),
    timestamp TIMESTAMP,
    author VARCHAR(255),
    text TEXT,
    language VARCHAR(20),
    brand_mention BOOLEAN,
    sentiment VARCHAR(20),
    sentiment_score INTEGER,
    topic VARCHAR(100),
    reactions INTEGER,
    comments INTEGER
);
