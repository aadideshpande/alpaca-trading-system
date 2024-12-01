from datetime import datetime

from utils import *
from api.client import AlpacaClient


if __name__ == "__main__":

    # Initialize Alpaca client
    alpaca_client = AlpacaClient()

    # try:
    #     start_date = datetime(2022, 7, 1, 9, 30, 0)
    #     end_date = datetime(2022, 7, 1, 17, 0, 0)
    #     data = alpaca_client.get_historical_stock_prices(["APPL", "TSLA"], start_date, end_date)
    #     print(data)
    # except Exception as e:
    #     print("Failed to get quotes")
    #
    # print("Get Account Details: ")
    # try:
    #     account = alpaca_client.get_account()
    #     print(account)
    # except Exception as e:
    #     print("Failed to get account details")
    #
    # try:
    #     positions = alpaca_client.get_all_positions()
    #     print(positions)
    # except Exception as e:
    #     print("Failed to get account positions")

    # print(alpaca_client.get_all_orders())
    alpaca_client.get_real_time_data()

    try:
        pass
        # market_order = alpaca_client.submit_market_order("AAPL", 1, "buy")
        # print(market_order)
    except Exception as e:
        print("Failed to place order")
