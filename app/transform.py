import logging
import pandas as pd

logger = logging.getLogger(__name__)

def clean_crypto_data(df:pd.DataFrame)->pd.DataFrame:
    if df.empty:
        logger.warning(" Input DataFrame is empty")
        return df
    
    selected_columns = [
        "id",
        "symbol",
        "name",
        "current_price",
        "market_cap",
        "market_cap_rank",
        "total_volume",
        "high_24h",
        "low_24h",
        "price_change_percentage_24h",
        "last_updated"
    ]

    # Chỉ giữ cột cần thiết
    df = df[selected_columns].copy()

    # Chuẩn hóa timestamp
    df["last_updated"] = pd.to_datetime(df["last_updated"], utc=True, errors="coerce")

    # Thêm thời điểm pipeline ingest
    df["ingested_at"] = pd.Timestamp.utcnow()

    # Xử lý null cơ bản
    numeric_columns = [
        "current_price",
        "market_cap",
        "market_cap_rank",
        "total_volume",
        "high_24h",
        "low_24h",
        "price_change_percentage_24h"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Loại record thiếu khóa chính quan trọng
    df = df.dropna(subset=["id", "symbol", "name", "last_updated"])

    # Xóa duplicate nếu có
    df = df.drop_duplicates(subset=["id", "last_updated"])

    logger.info("Cleaned DataFrame shape: %s", df.shape)
    return df