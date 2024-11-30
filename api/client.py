import requests
import os
from config_loader import *


class AlpacaClient:
    def __init__(self, api_key=None, secret_key=None, base_url=None):
        self.api_key = api_key or ALPACA_API_KEY  # os.getenv("ALPACA_API_KEY")
        self.secret_key = secret_key or ALPACA_SECRET_KEY  # os.getenv("ALPACA_SECRET_KEY")
        self.base_paper_url = base_url or PAPER_API
        self.base_data_url = DATA_API
        self.headers = {
            "APCA-API-KEY-ID": self.api_key,
            "APCA-API-SECRET-KEY": self.secret_key,
        }

        if not self.api_key or not self.secret_key:
            raise ValueError("API keys are required. Please set them in environment variables or pass explicitly.")

    def _make_request(self, method, endpoint, params=None, data=None):
        url = f"{self.base_paper_url}/{endpoint}"
        response = requests.request(
            method, url, headers=self.headers, params=params, json=data
        )

        if not response.ok:
            raise Exception(f"API call failed: {response.status_code} {response.text}")

        return response.json()

    def _make_data_request(self, method, endpoint, params=None, data=None):
        url = f"{self.base_data_url}/{endpoint}"
        response = requests.request(
            method, url, headers=self.headers, params=params, json=data
        )

        if not response.ok:
            raise Exception(f"API call failed: {response.status_code} {response.text}")

        return response.json()

    def get_account(self):
        """Get account details."""
        return self._make_request("GET", "/account")

    def place_order(self, symbol, qty, side, order_type="market", time_in_force="gtc"):
        """Place an order."""
        data = {
            "symbol": symbol,
            "qty": qty,
            "side": side,
            "type": order_type,
            "time_in_force": time_in_force,
        }
        return self._make_request("POST", "v2/orders", data=data)

    def get_orders(self, status="open"):
        """Retrieve all orders based on their status."""
        params = {"status": status}
        return self._make_request("GET", "v2/orders", params=params)

    def get_positions(self):
        """Retrieve all open positions."""
        return self._make_request("GET", "v2/positions")

    def get_latest_quotes(self, symbols):
        return self._make_data_request("GET", "stocks/quotes/latest", {"symbols": "AAPL,TSLA", "feed": "iex"})

