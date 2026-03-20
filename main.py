import logging

from app.extract import run_extract
from app.transform import clean_crypto_data
from app.db import get_engine
from app.load import load_to_postgres


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)


def run_pipeline():
    df_raw = run_extract()
    df_clean = clean_crypto_data(df_raw)
    engine = get_engine()
    load_to_postgres(df_clean, engine)


if __name__ == "__main__":
    run_pipeline()