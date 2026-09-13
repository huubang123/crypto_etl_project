CREATE TABLE IF NOT EXISTS crypto.crypto_market_raw (
    coin_id TEXT NOT NULL,
    symbol TEXT,
    coin_name TEXT,
    source_updated_at TIMESTAMPTZ,
    raw_payload JSONB NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (coin_id, source_updated_at)
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_crypto_raw_coin_time
ON crypto.crypto_market_raw (coin_id, source_updated_at);
