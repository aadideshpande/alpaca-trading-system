from datetime import datetime

import requests
import os

from alpaca.data import TimeFrame

from config_loader import *
from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient, CryptoHistoricalDataClient, OptionHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest
from alpaca.data.requests import CryptoLatestQuoteRequest
from alpaca.data.requests import CryptoBarsRequest, StockBarsRequest, OptionBarsRequest
from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus
from alpaca.trading.requests import LimitOrderRequest, MarketOrderRequest, GetOrdersRequest


class AlpacaClient:
    def __init__(self, api_key=None, secret_key=None, base_url=None):
        self.api_key = api_key or ALPACA_API_KEY  # os.getenv("ALPACA_API_KEY")
        self.secret_key = secret_key or ALPACA_SECRET_KEY  # os.getenv("ALPACA_SECRET_KEY")
        # self.base_paper_url = base_url or PAPER_API
        # self.base_data_url = DATA_API
        # self.headers = {
        #     "APCA-API-KEY-ID": self.api_key,
        #     "APCA-API-SECRET-KEY": self.secret_key,
        # }
        self.option_historical_data_client = OptionHistoricalDataClient(ALPACA_API_KEY, ALPACA_SECRET_KEY)
        self.crypto_historical_data_client = CryptoHistoricalDataClient(ALPACA_API_KEY, ALPACA_SECRET_KEY)
        self.stock_historical_data_client = StockHistoricalDataClient(ALPACA_API_KEY, ALPACA_SECRET_KEY)
        self.trading_client = TradingClient(ALPACA_API_KEY, ALPACA_SECRET_KEY, paper=True)

        if not self.api_key or not self.secret_key:
            raise ValueError("API keys are required. Please set them in environment variables or pass explicitly.")

    # def _make_request(self, method, endpoint, params=None, data=None):
    #     url = f"{self.base_paper_url}/{endpoint}"
    #     response = requests.request(
    #         method, url, headers=self.headers, params=params, json=data
    #     )
    #
    #     if not response.ok:
    #         raise Exception(f"API call failed: {response.status_code} {response.text}")
    #
    #     return response.json()

    # def _make_data_request(self, method, endpoint, params=None, data=None):
    #     url = f"{self.base_data_url}/{endpoint}"
    #     response = requests.request(
    #         method, url, headers=self.headers, params=params, json=data
    #     )
    #
    #     if not response.ok:
    #         raise Exception(f"API call failed: {response.status_code} {response.text}")
    #
    #     return response.json()

    def get_account(self):
        return self.trading_client.get_account()

    # def place_order(self, symbol, qty, side, order_type="market", time_in_force="gtc"):
    #     """Place an order."""
    #     data = {
    #         "symbol": symbol,
    #         "qty": qty,
    #         "side": side,
    #         "type": order_type,
    #         "time_in_force": time_in_force,
    #     }
    #     return self._make_request("POST", "v2/orders", data=data)
    #
    # def get_orders(self, status="open"):
    #     """Retrieve all orders based on their status."""
    #     params = {"status": status}
    #     return self._make_request("GET", "v2/orders", params=params)
    #
    # def get_positions(self):
    #     """Retrieve all open positions."""
    #     return self._make_request("GET", "v2/positions")
    # def get_latest_quotes(self, symbols):
    #     return self.stock_historical_data_client.g
    #     return self._make_data_request("GET", "stocks/quotes/latest", {"symbols": "AAPL,TSLA", "feed": "iex"})

    def get_historical_stock_prices(self, symbols, start_date, end_date):
        """Retrieve the historical stock prices"""
        request_params = StockBarsRequest(
            symbol_or_symbols=symbols,
            timeframe=TimeFrame.Minute,
            start=start_date,
            end=end_date

        )
        return self.stock_historical_data_client.get_stock_bars(request_params)

    def get_historical_options_prices(self, symbols, start_date, end_date):
        """Retrieve the historical options prices"""
        request_params = OptionBarsRequest(
            symbol_or_symbols=symbols,
            timeframe=TimeFrame.Minute,
            start=start_date,
            end=end_date

        )
        return self.option_historical_data_client.get_option_bars(request_params)

    def submit_market_order(self, symbol, quantity, side):
        """Submit a market order"""
        if side == "buy":
            side = OrderSide.BUY
        elif side == "sell":
            side = OrderSide.SELL
        market_order_data = MarketOrderRequest(
            symbol=symbol,
            qty=quantity,
            side=side,
            time_in_force=TimeInForce.DAY
        )

        # Market order
        market_order = self.trading_client.submit_order(
            order_data=market_order_data
        )
        print("submitted market order....")
        return market_order

    def submit_limit_order(self, symbol, limit_price, notional, side):
        """Submit a limit order"""
        limit_order_data = LimitOrderRequest(
            symbol=symbol,
            limit_price=limit_price,
            notional=notional,
            side=side,
            time_in_force=TimeInForce.FOK
        )

        # Limit order
        limit_order = self.trading_client.submit_order(
            order_data=limit_order_data
        )

    def get_all_orders(self, status=None, side=None):
        """Fetch all orders for the account"""
        if side == "buy" or side is None:
            side = OrderSide.BUY
        elif side == "sell":
            side = OrderSide.SELL
        request_params = GetOrdersRequest(
            status=status,
            side=side
        )

        # orders that satisfy params
        orders = self.trading_client.get_orders(filter=request_params)
        return orders

    def cancel_all_orders(self):
        """
        Cancel all orders for the account
        This can act like a 'kill switch' if the strategies do not work
        """
        cancel_statuses = self.trading_client.cancel_orders()

    def get_all_positions(self):
        """Get all positions for that account"""
        positions = self.trading_client.get_all_positions()

    def close_all_positions(self):
        """Close all positions and cancel all orders"""
        positions = self.trading_client.close_all_positions(cancel_orders=True)
