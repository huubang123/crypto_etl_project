import json
import logging

import pandas as pd
from sqlalchemy import MetaData, Table
from sqlalchemy.dialects.postgresql import insert

logger = logging.getLogger(__name__)


def load_raw_to_postgres(df: pd.DataFrame, engine):
    if df.empty:
        logger.warning("No raw data to load.")
        return

    metadata = MetaData()
    metadata.reflect(bind=engine, schema="crypto")

    table = Table("crypto_market_raw", metadata, schema="crypto", autoload_with=engine)

    records = []
    for row in df.to_dict(orient="records"):
        payload = row.copy()
        record = {
            "coin_id": row.get("id"),
            "symbol": row.get("symbol"),
            "coin_name": row.get("name"),
            "source_updated_at": pd.to_datetime(row.get("last_updated"), utc=True, errors="coerce"),
            "raw_payload": payload,
            "ingested_at": pd.Timestamp.now(tz="UTC"),
        }
        records.append(record)

    inserted_rows = 0

    with engine.begin() as conn:
        for record in records:
            stmt = insert(table).values(**record)
            stmt = stmt.on_conflict_do_nothing(
                index_elements=["coin_id", "source_updated_at"]
            )
            result = conn.execute(stmt)
            inserted_rows += result.rowcount

    logger.info("Inserted %s rows into PostgreSQL raw table.", inserted_rows)


def load_to_postgres(df: pd.DataFrame, engine):
    if df.empty:
        logger.warning("No data to load.")
        return

    metadata = MetaData()
    metadata.reflect(bind=engine, schema="crypto")

    table = Table("crypto_market_snapshot", metadata, schema="crypto", autoload_with=engine)

    records = df.rename(columns={
        "id": "coin_id",
        "name": "coin_name",
        "last_updated": "source_updated_at"
    }).to_dict(orient="records")

    inserted_rows = 0

    with engine.begin() as conn:
        for record in records:
            stmt = insert(table).values(**record)
            stmt = stmt.on_conflict_do_nothing(
                index_elements=["coin_id", "source_updated_at"]
            )
            result = conn.execute(stmt)
            inserted_rows += result.rowcount

    logger.info("Inserted %s rows into PostgreSQL.", inserted_rows)
