import os
import logging
from typing import List, Optional
import requests
import pandas as pd

logger = logging.getLogger(__name__)

class CoinGeckoExtractor:
    def __init__(self, api_key : Optional[str] = None, base_url : Optional[str] = None):
            self.api_key = api_key or os.getenv("COINGECKO_API_KEY")
            self.base_url = base_url or os.getenv("COINGECKO_BASE_URL","https://api.coingecko.com/api/v3")

            self.session = requests.Session()
            self.session.headers.update({
                "accept": "application/json"
                }
            )
            if self.api_key:
                self.session.headers.update({
                    "x-cg-demo-api-key": self.api_key
                })
    def fetch_market_data(
        self
        ,vs_currency : str = "usd"
        ,coin_ids : Optional[List[str]] =None
        ,per_page: int = 10
        ,page : int=1
    ) ->list:
        endpoint = f"{self.base_url}/coins/markets"
        
        params = {
            "vs_currency":vs_currency
            ,"order": "market_cap_desc",
            "per_page": per_page,
            "page": page,
            "sparkline": "false",
            "price_change_percentage": "24h"
        }

        if coin_ids:
            params["ids"] = ",".join(coin_ids)

        try:
            logger.info("Requesting data from CoinGecko API...")
            response = self.session.get(endpoint, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if not isinstance(data , list):
                raise ValueError("Expected API response to be a list of records.")
            
            logger.info("Successfully fetched %s records from API.",len(data))
            return data
        except requests.exceptions.RequestException as e:
            logger.error("API request failed: %s", e)
            raise
        except ValueError as e:
            logger.error("Invalid API response format: %s", e)
            raise
    @staticmethod
    def json_to_dataframe(data:list) ->pd.DataFrame:
        if not data:
            logger.warning("Received empty data.")
            return pd.DataFrame()
        df = pd.DataFrame(data)
        logger.info("Converted JSON to DataFrame with shape: %s", df.shape)
        return df 
def run_extract()->pd.DataFrame:
        extractor = CoinGeckoExtractor()
        rawdata = extractor.fetch_market_data(
            vs_currency="usd"
            ,coin_ids=["bitcoin", "ethereum", "solana", "ripple", "cardano"]
            ,per_page=5
            ,page=1
        )
        df = extractor.json_to_dataframe(rawdata)
        return df

if __name__ == "__main__":
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )
        df = run_extract()
        print(df.head())