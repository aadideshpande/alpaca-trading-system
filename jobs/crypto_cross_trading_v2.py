import time

import numpy as np
import pandas as pd
import datetime as datetime
from api.client import AlpacaClient

from config_loader import *
from alpaca.data.live import CryptoDataStream

alpaca_client = AlpacaClient()

def cross_sectional_momentum(bar):
    try:
        # Get the Latest Data
        start_date = datetime.datetime(2024, 12, 1, 12, 0, 0)
        end_date = datetime.datetime(2024, 12, 1, 17, 0, 0)
        dataframe = pd.DataFrame()
        symbols = ['BTC/USD', 'ETH/USD', 'SHIB/USD'] #['BTC/USD','ETH/USD','DOGE/USD','SHIB/USD','MATIC/USD','ALGO/USD','AVAX/USD','LINK/USD','SOL/USD']
        for symbol in symbols:
            data = alpaca_client.get_historical_crypto_prices(symbol, start_date=start_date, end_date=end_date).df['close']
            data = pd.DataFrame(data)
            data.reset_index(inplace=True)
            dataframe = pd.concat([dataframe,data], axis=1, sort=False)
            # dataframe.reset_index()

        returns_data = dataframe.apply(func = lambda x: x.shift(-1)/x - 1, axis = 0)

        # Calculate Momentum Dataframe
        momentum_df = returns_data.apply(func = lambda x: x.shift(1)/x.shift(7) - 1, axis = 0)
        momentum_df = momentum_df.rank(axis = 1)
        for col in momentum_df.columns:
            momentum_df[col] = np.where(momentum_df[col] > 8, 1, 0)

        # Get Symbol with Highest Momentum
        momentum_df['Buy'] = momentum_df.astype(bool).dot(momentum_df.columns)
        buy_symbol = momentum_df['Buy'].iloc[-1]
        old_symbol = momentum_df['Buy'].iloc[-2]

        # Account Details
        current_position = alpaca_client.check_positions(symbol=buy_symbol)
        old_position = alpaca_client.check_positions(symbol=old_symbol)

        # No Current Positions
        if current_position == 0 and old_position == 0:
            cash_balance = alpaca_client.get_account().non_marginable_buying_power
            alpaca_client.submit_market_order(buy_symbol, quantity=0.0005, side='buy')
            message = f'Symbol: {buy_symbol} | Side: Buy | Notional: {cash_balance}'
            print(message)

        # No Current Position and Yes Old Position
        if current_position == 0 and old_position == 1:
            alpaca_client.trading_client.close_position(old_symbol)
            message = f'Symbol: {old_symbol} | Side: Sell'
            print(message)

            cash_balance = alpaca_client.get_account().non_marginable_buying_power
            alpaca_client.submit_market_order(buy_symbol, quantity=0.0005, side='buy')
            message = f'Symbol: {buy_symbol} | Side: Buy | Notional: {cash_balance}'
            print(message)

        print("-"*20)

    except Exception as e:
        print (e)


if __name__ == "__main__":
    alpaca_client.close_all_positions()
    cross_sectional_momentum(None)


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
