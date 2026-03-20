CREATE TABLE IF NOT EXISTS crypto.coin_market (
    id SERIAL PRIMARY KEY,
    coin_name VARCHAR(100),
    price_usd NUMERIC,
    volume_24h NUMERIC,
    market_cap NUMERIC,
    extracted_at TIMESTAMP
);