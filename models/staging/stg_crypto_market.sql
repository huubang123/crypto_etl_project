with source as (
    select
        coin_id,
        symbol,
        coin_name,
        source_updated_at,
        raw_payload,
        ingested_at
    from {{ source('crypto', 'crypto_market_raw') }}
)

select
    coin_id,
    coalesce(symbol, 'unknown') as symbol,
    coalesce(coin_name, 'unknown') as coin_name,
    (raw_payload ->> 'current_price')::numeric as current_price,
    (raw_payload ->> 'market_cap')::numeric as market_cap,
    (raw_payload ->> 'market_cap_rank')::numeric as market_cap_rank,
    (raw_payload ->> 'total_volume')::numeric as total_volume,
    (raw_payload ->> 'high_24h')::numeric as high_24h,
    (raw_payload ->> 'low_24h')::numeric as low_24h,
    (raw_payload ->> 'price_change_percentage_24h')::numeric as price_change_percentage_24h,
    source_updated_at,
    ingested_at
from source
where coin_id is not null
  and source_updated_at is not null
