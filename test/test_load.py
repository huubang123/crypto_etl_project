import logging
from unittest.mock import MagicMock, patch

import pandas as pd

from app.load import load_to_postgres


def test_load_to_postgres_logs_actual_inserted_row_count(caplog):
    caplog.set_level(logging.INFO, logger="app.load")

    dataframe = pd.DataFrame(
        [
            {
                "id": "bitcoin",
                "symbol": "btc",
                "name": "Bitcoin",
                "last_updated": "2026-03-20T12:00:00Z",
            },
            {
                "id": "ethereum",
                "symbol": "eth",
                "name": "Ethereum",
                "last_updated": "2026-03-20T12:00:00Z",
            },
        ]
    )
    engine = MagicMock()
    connection = MagicMock()
    engine.begin.return_value.__enter__.return_value = connection
    connection.execute.side_effect = [MagicMock(rowcount=1), MagicMock(rowcount=0)]

    with (
        patch("app.load.MetaData"),
        patch("app.load.Table"),
        patch("app.load.insert") as mock_insert,
    ):
        statement = mock_insert.return_value
        statement.values.return_value = statement
        statement.on_conflict_do_nothing.return_value = statement

        load_to_postgres(dataframe, engine)

    assert "Inserted 1 rows into PostgreSQL." in caplog.text
    assert connection.execute.call_count == 2
