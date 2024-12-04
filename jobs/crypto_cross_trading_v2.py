import time

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from api.client import AlpacaClient
from alpaca.data.requests import CryptoLatestBarRequest

from config_loader import *
from alpaca.data.live import CryptoDataStream

alpaca_client = AlpacaClient()


def calculate_quantity(symbol, cash_balance):
    try:
        # Create the request for the latest bar data
        request = CryptoLatestBarRequest(symbol_or_symbols=[symbol])
        latest_bar = alpaca_client.crypto_historical_data_client.get_crypto_latest_bar(request)

        # Extract the latest price
        current_price = latest_bar[symbol].close

        # Use a fraction of the cash balance (e.g., 20%) for the trade
        trade_amount = cash_balance * 0.2

        # Calculate the quantity
        quantity = trade_amount / current_price

        # Ensure the quantity is above the minimum allowed for the exchange
        quantity = round(quantity, 6)  # Adjust rounding as per exchange rules
        return max(quantity, 0)  # Ensure non-negative quantity
    except Exception as e:
        print(f"Error calculating quantity for {symbol}: {e}")
        return 0


def cross_sectional_momentum(bar):
    try:
        # Get the Latest Data
        end_date = datetime.now()
        start_date = end_date - timedelta(hours=3)
        dataframe = pd.DataFrame()
        #symbols = ['BTC/USD','ETH/USD','SHIB/USD','MATIC/USD','ALGO/USD','AVAX/USD','LINK/USD','SOL/USD']
        symbols = ['BTC/USD', 'ETH/USD', 'SOL/USD'] #['BTC/USD','ETH/USD','DOGE/USD','SHIB/USD','MATIC/USD','ALGO/USD','AVAX/USD','LINK/USD','SOL/USD']
        SYMBOLS_LENGTH = len(symbols)
        for symbol in symbols:
            data = alpaca_client.get_historical_crypto_prices(symbol, start_date=start_date, end_date=end_date).df['close']
            data.index = pd.MultiIndex.from_tuples(data.index, names=["symbol", "time"])
            new_dataframe = data.unstack(level=0)  # 'level=0' corresponds to 'symbol'
            new_dataframe.index = pd.to_datetime(new_dataframe.index)
            new_dataframe.index.name = 'time'
            data = pd.DataFrame(data).rename(columns={"close": str(symbol)})

            dataframe = pd.concat([dataframe,new_dataframe], axis=1, sort=False)

        dataframe.dropna(inplace=True)
        returns_data = dataframe.apply(func=lambda x: x.shift(-1)/x - 1, axis=0)

        # Calculate Momentum Dataframe
        momentum_df = returns_data.apply(func=lambda x: x.shift(1)/x.shift(7) - 1, axis=0)
        momentum_df = momentum_df.rank(axis=1)
        for col in momentum_df.columns:
            momentum_df[col] = np.where(momentum_df[col] > SYMBOLS_LENGTH - 1, 1, 0)

        # Get Symbol with Highest Momentum
        momentum_df['Buy'] = momentum_df.astype(bool).dot(momentum_df.columns)
        buy_symbol = momentum_df['Buy'].iloc[-1]
        old_symbol = momentum_df['Buy'].iloc[-2]

        # Account Details
        current_position = alpaca_client.check_positions(symbol=buy_symbol)
        old_position = alpaca_client.check_positions(symbol=old_symbol)

        # No Current Positions
        if current_position == 0 and old_position == 0:
            cash_balance = float(alpaca_client.get_account().non_marginable_buying_power)
            quantity = calculate_quantity(buy_symbol, cash_balance)
            if quantity > 0:
                alpaca_client.submit_market_order(buy_symbol, quantity=quantity, side='buy')
                message = f'Symbol: {buy_symbol} | Side: Buy | Quantity: {quantity}'
                print(message)

        # No Current Position and Yes Old Position
        if current_position == 0 and old_position == 1:
            alpaca_client.trading_client.close_position(old_symbol)
            message = f'Symbol: {old_symbol} | Side: Sell'
            print(message)

            cash_balance = float(alpaca_client.get_account().non_marginable_buying_power)
            quantity = calculate_quantity(buy_symbol, cash_balance)
            if quantity > 0:
                alpaca_client.submit_market_order(buy_symbol, quantity=quantity, side='buy')
                message = f'Symbol: {buy_symbol} | Side: Buy | Quantity: {quantity}'
                print(message)

        print("-"*20)

    except Exception as e:
        print (e)


if __name__ == "__main__":
    alpaca_client.close_all_positions()
    start_time = time.time()
    while time.time() - start_time < 60 * 60:  # 60 minutes
        cross_sectional_momentum(None)
        time.sleep(60)
    alpaca_client.close_all_positions()

    #wss_client = CryptoDataStream(ALPACA_API_KEY, ALPACA_SECRET_KEY)
    # Create handler for receiving live bar data
    # async def on_crypto_bar(bar):
    #     time.sleep(10)
    #     print(bar)
    #     cross_sectional_momentum(bar)


    # Subscribe to data and assign handler
    # wss_client.subscribe_quotes(on_crypto_bar, 'BTC/USD', 'ETH/USD', 'DOGE/USD', 'SHIB/USD', 'MATIC/USD',
    #                              'ALGO/USD', 'AVAX/USD', 'LINK/USD', 'SOL/USD')
    #
    # wss_client.run()
