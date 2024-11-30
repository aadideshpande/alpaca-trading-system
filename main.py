from utils import *
from api.client import AlpacaClient


if __name__ == "__main__":

    # Initialize Alpaca client
    alpaca_client = AlpacaClient()

    # Example: Get account details
    account = alpaca_client.get_account()
    print(f"Account Equity: {account['equity']}")

    # Example: Place an order
    # try:
    #     order = alpaca_client.place_order(
    #         symbol="AAPL",
    #         qty=1,
    #         side="buy",
    #         order_type="market",
    #         time_in_force="gtc"
    #     )
    #     print(f"Order placed: {order}")
    # except Exception as e:
    #     print(f"Failed to place order: {e}")
    #
    # # Example: Get open orders
    # orders = alpaca_client.get_orders()
    # print(f"Open Orders: {orders}")
    #
    # # Example: Get positions
    # positions = alpaca_client.get_positions()
    # print(f"Positions: {positions}")

    try:
        data = alpaca_client.get_latest_quotes("APPL")
        print(data)

    except Exception as e:
        print("Failed to get quotes")

    print("Get Account Details: ")
    try:
        account = alpaca_client.get_account()
        print(account)

    except Exception as e:
        print("Failed to get quotes")

