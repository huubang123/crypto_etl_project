import logging
from unittest.mock import MagicMock, patch

import pandas as pd

from app.load import load_raw_to_postgres


def test_load_raw_to_postgres_stores_json_payload(caplog):
    caplog.set_level(logging.INFO, logger="app.load")

    dataframe = pd.DataFrame(
        [
            {
                "id": "bitcoin",
                "symbol": "btc",
                "name": "Bitcoin",
                "current_price": 100000.5,
            }
        ]
    )
    engine = MagicMock()
    connection = MagicMock()
    engine.begin.return_value.__enter__.return_value = connection
    connection.execute.return_value = MagicMock(rowcount=1)

    with (
        patch("app.load.MetaData"),
        patch("app.load.Table"),
        patch("app.load.insert") as mock_insert,
    ):
        statement = mock_insert.return_value
        statement.values.return_value = statement
        statement.on_conflict_do_nothing.return_value = statement

        load_raw_to_postgres(dataframe, engine)

    assert "Inserted 1 rows into PostgreSQL raw table." in caplog.text
    assert connection.execute.call_count == 1
