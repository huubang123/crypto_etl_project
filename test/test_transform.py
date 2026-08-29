import pandas as pd

from app.transform import clean_crypto_data


def test_clean_crypto_data_normalizes_and_deduplicates_records():
    raw_data = pd.DataFrame(
        [
            {
                "id": "bitcoin",
                "symbol": "btc",
                "name": "Bitcoin",
                "current_price": "100000.5",
                "market_cap": "2000000",
                "market_cap_rank": "1",
                "total_volume": "50000",
                "high_24h": "101000",
                "low_24h": "99000",
                "price_change_percentage_24h": "1.25",
                "last_updated": "2026-03-20T12:00:00Z",
                "image": "unused",
            },
            {
                "id": "bitcoin",
                "symbol": "btc",
                "name": "Bitcoin",
                "current_price": "100000.5",
                "market_cap": "2000000",
                "market_cap_rank": "1",
                "total_volume": "50000",
                "high_24h": "101000",
                "low_24h": "99000",
                "price_change_percentage_24h": "1.25",
                "last_updated": "2026-03-20T12:00:00Z",
                "image": "unused",
            },
            {
                "id": "invalid",
                "symbol": "inv",
                "name": "Invalid",
                "current_price": "not-a-number",
                "market_cap": "1",
                "market_cap_rank": "2",
                "total_volume": "3",
                "high_24h": "4",
                "low_24h": "5",
                "price_change_percentage_24h": "6",
                "last_updated": "not-a-timestamp",
                "image": "unused",
            },
        ]
    )

    cleaned = clean_crypto_data(raw_data)

    assert list(cleaned.columns) == [
        "id", "symbol", "name", "current_price", "market_cap",
        "market_cap_rank", "total_volume", "high_24h", "low_24h",
        "price_change_percentage_24h", "last_updated", "ingested_at",
    ]
    assert len(cleaned) == 1
    assert cleaned.iloc[0]["current_price"] == 100000.5
    assert pd.api.types.is_numeric_dtype(cleaned["market_cap"])
    assert str(cleaned.iloc[0]["last_updated"].tz) == "UTC"
    assert str(cleaned.iloc[0]["ingested_at"].tz) == "UTC"


def test_clean_crypto_data_returns_empty_dataframe_unchanged():
    raw_data = pd.DataFrame()

    cleaned = clean_crypto_data(raw_data)

    assert cleaned.empty
    assert cleaned.equals(raw_data)
