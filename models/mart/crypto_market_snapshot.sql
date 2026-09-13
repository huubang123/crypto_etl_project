select
    coin_id,
    symbol,
    coin_name,
    current_price,
    market_cap,
    market_cap_rank,
    total_volume,
    high_24h,
    low_24h,
    price_change_percentage_24h,
    source_updated_at,
    ingested_at
from {{ ref('stg_crypto_market') }}
where current_price is not null
