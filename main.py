import logging

from app.db import get_engine
from app.extract import run_extract
from app.load import load_raw_to_postgres


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def run_pipeline():
    df_raw = run_extract()
    engine = get_engine()
    load_raw_to_postgres(df_raw, engine)


if __name__ == "__main__":
    run_pipeline()