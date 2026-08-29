from unittest.mock import Mock, patch

import pytest
import requests

from app.extract import CoinGeckoExtractor


def test_fetch_market_data_calls_coingecko_with_expected_parameters():
    payload = [{"id": "bitcoin", "symbol": "btc"}]
    response = Mock()
    response.json.return_value = payload

    extractor = CoinGeckoExtractor(base_url="https://example.test/api/v3")

    with patch.object(extractor.session, "get", return_value=response) as mock_get:
        result = extractor.fetch_market_data(
            vs_currency="usd", coin_ids=["bitcoin", "ethereum"], per_page=2, page=3
        )

    assert result == payload
    response.raise_for_status.assert_called_once_with()
    mock_get.assert_called_once_with(
        "https://example.test/api/v3/coins/markets",
        params={
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 2,
            "page": 3,
            "sparkline": "false",
            "price_change_percentage": "24h",
            "ids": "bitcoin,ethereum",
        },
        timeout=30,
    )


def test_fetch_market_data_rejects_non_list_response():
    response = Mock()
    response.json.return_value = {"error": "unexpected response"}
    extractor = CoinGeckoExtractor(base_url="https://example.test/api/v3")

    with patch.object(extractor.session, "get", return_value=response):
        try:
            extractor.fetch_market_data()
        except ValueError as error:
            assert str(error) == "Expected API response to be a list of records."
        else:
            raise AssertionError("Expected fetch_market_data to raise ValueError")


def test_fetch_market_data_retries_rate_limited_request_with_exponential_backoff():
    rate_limit_response = Mock(status_code=429)
    rate_limit_error = requests.exceptions.HTTPError(response=rate_limit_response)
    failed_response = Mock()
    failed_response.raise_for_status.side_effect = rate_limit_error
    successful_response = Mock()
    successful_response.json.return_value = [{"id": "bitcoin"}]
    extractor = CoinGeckoExtractor(max_retries=3, backoff_seconds=1)

    with (
        patch.object(extractor.session, "get", side_effect=[failed_response, successful_response]),
        patch("app.extract.time.sleep") as mock_sleep,
    ):
        result = extractor.fetch_market_data()

    assert result == [{"id": "bitcoin"}]
    assert mock_sleep.call_args_list == [((1,), {})]


def test_fetch_market_data_does_not_retry_non_transient_client_error():
    client_error_response = Mock(status_code=400)
    client_error = requests.exceptions.HTTPError(response=client_error_response)
    response = Mock()
    response.raise_for_status.side_effect = client_error
    extractor = CoinGeckoExtractor(max_retries=3)

    with (
        patch.object(extractor.session, "get", return_value=response) as mock_get,
        patch("app.extract.time.sleep") as mock_sleep,
        pytest.raises(requests.exceptions.HTTPError),
    ):
        extractor.fetch_market_data()

    assert mock_get.call_count == 1
    mock_sleep.assert_not_called()


def test_json_to_dataframe_creates_expected_dataframe():
    data = [{"id": "bitcoin", "current_price": 100000}]

    dataframe = CoinGeckoExtractor.json_to_dataframe(data)

    assert dataframe.to_dict(orient="records") == data


def test_json_to_dataframe_returns_empty_dataframe_for_empty_data():
    dataframe = CoinGeckoExtractor.json_to_dataframe([])

    assert dataframe.empty
