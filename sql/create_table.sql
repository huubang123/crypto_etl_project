CREATE TABLE IF NOT EXISTS crypto.crypto_market_snapshot (
    coin_id TEXT NOT NULL,
    symbol TEXT NOT NULL,
    coin_name TEXT NOT NULL,
    current_price NUMERIC,
    market_cap NUMERIC,
    market_cap_rank NUMERIC,
    total_volume NUMERIC,
    high_24h NUMERIC,
    low_24h NUMERIC,
    price_change_percentage_24h NUMERIC,
    source_updated_at TIMESTAMPTZ,
    ingested_at TIMESTAMPTZ,
    UNIQUE (coin_id, source_updated_at)
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_crypto_coin_time
ON crypto.crypto_market_snapshot (coin_id, source_updated_at);
