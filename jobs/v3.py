import threading
import pandas as pd
from datetime import datetime as dt, timedelta
from pytz import timezone
import schedule
import numpy as np
import os
import time

# Import your custom AlpacaClient
import alpacaclient as AlpacaClient

# Replace with your actual API keys
# API_KEY = 'your_api_key'
# SECRET_KEY = 'your_secret_key'

# Initialize your custom AlpacaClient
alpaca_client = AlpacaClient(api_key=API_KEY, secret_key=SECRET_KEY)

# Use symbols with '/' as required by the Alpaca API
# TICKERS = ['BTC/USD', 'ETH/USD', 'SOL/USD']

# Global variables to store the latest prices
latest_prices = {}

# Ensure tick_data directory exists
if not os.path.exists('tick_data'):
    os.makedirs('tick_data')

# Function to handle incoming trade updates
def on_crypto_trade(trade):
    symbol = trade.symbol
    price = trade.price
    latest_prices[symbol] = price
    print(f"Trade update for {symbol}: {price}")

# Function to set up and run the WebSocket client
def start_websocket():
    from alpaca.data.live import CryptoDataStream

    # Initialize the WebSocket client
    wss_client = CryptoDataStream(API_KEY, SECRET_KEY)

    # Subscribe to trade updates
    wss_client.subscribe_trades(on_crypto_trade, *TICKERS)

    # Start the WebSocket client (blocking call)
    wss_client.run()

# Function to fetch historical data
def get_crypto_data(tickers):
    print("Fetching historical data...")
    end_time = dt.now(timezone('UTC'))
    start_time = end_time - timedelta(hours=3)

    for ticker in tickers:
        try:
            data = alpaca_client.get_historical_crypto_prices(ticker, start_date=start_time, end_date=end_time).df

            # Ensure the DataFrame is not empty
            if not data.empty:
                filename = f'tick_data/{ticker.replace("/", "_")}.csv'
                data.to_csv(filename)
                print(f"Data for {ticker} saved to {filename}. Here's a preview:")
                print(data.head())
            else:
                print(f"No data fetched for {ticker}.")
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
    print("Data fetching completed.\n")

# Function to calculate ROC
def ROC(prices):
    if len(prices) >= 36:
        rocs = (prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0]
    else:
        rocs = 0
    return rocs * 100  # Convert to percentage

# Function to generate ROC rankings
def return_ROC_list(tickers):
    print("Calculating ROC rankings...")
    ROC_tickers = []
    for ticker in tickers:
        try:
            filename = f'tick_data/{ticker.replace("/", "_")}.csv'
            df = pd.read_csv(filename)
            roc_value = ROC(df['close'])
            ROC_tickers.append({'Ticker': ticker, 'ROC': roc_value})
        except Exception as e:
            print(f"Error calculating ROC for {ticker}: {e}")
    roc_df = pd.DataFrame(ROC_tickers)
    roc_df = roc_df.sort_values(by='ROC', ascending=False)
    print(roc_df)
    return roc_df

# Function to log orders
def log_order(ticker, order_type, price, quantity):
    account = alpaca_client.get_account()
    order_data = {
        'Time': dt.now().strftime("%Y-%m-%d %H:%M:%S"),
        'Ticker': ticker,
        'Type': order_type,
        'Price': price,
        'Quantity': quantity,
        'Total': price * quantity,
        'Acc Balance': account.cash
    }

    if os.path.isfile('Orders.csv'):
        df = pd.read_csv('Orders.csv', index_col=0)
        df = df.append(order_data, ignore_index=True)
    else:
        df = pd.DataFrame([order_data])

    df.to_csv('Orders.csv')

# Function to place buy orders
def buy(stocks_to_buy):
    global initial_cash_balance
    allocation_per_stock = initial_cash_balance * 0.20  # 20% of initial capital

    for stock in stocks_to_buy:
        print(f"Attempting to buy {stock}...")
        # Check if we have enough buying power
        account = alpaca_client.get_account()
        buying_power = float(account.non_marginable_buying_power)
        if buying_power < allocation_per_stock:
            print(f"Not enough buying power to buy {stock}. Available: ${buying_power:.2f}, Required: ${allocation_per_stock:.2f}")
            continue  # Skip buying this stock

        try:
            price_stock = latest_prices.get(stock)
            if price_stock is None:
                print(f"No latest price available for {stock}. Skipping.")
                continue  # Skip if price couldn't be fetched

            target_position_size = allocation_per_stock / price_stock
            target_position_size = round(target_position_size, 6)  # Crypto can be fractional

            if target_position_size <= 0:
                print(f"Target position size for {stock} is zero or negative. Skipping.")
                continue

            # Place the market order using your AlpacaClient
            alpaca_client.submit_market_order(stock, quantity=target_position_size, side='buy')
            print(f"Buy order submitted for {stock}: {target_position_size} units at approx ${price_stock}")
            # Log the order
            log_order(stock, 'buy', price_stock, target_position_size)
        except Exception as e:
            print(f"Error buying {stock}: {e}")

# Function to place sell orders
def sell(stocks_to_sell):
    for stock in stocks_to_sell:
        print(f"Attempting to sell {stock}...")
        try:
            position_qty = alpaca_client.check_positions(symbol=stock)
            if position_qty == 0:
                print(f"No position to sell for {stock}")
                continue
            quantity = position_qty
            current_price = latest_prices.get(stock)
            if current_price is None:
                print(f"No latest price available for {stock}. Skipping.")
                continue  # Skip if price couldn't be fetched

            # Place the market sell order
            alpaca_client.submit_market_order(stock, quantity=quantity, side='sell')
            print(f"Sell order submitted for {stock}: {quantity} units at approx ${current_price}")
            # Log the order
            log_order(stock, 'sell', current_price, float(quantity))
        except Exception as e:
            print(f"Error selling {stock}: {e}")

# Function to check profit and loss
def check_profit_and_loss():
    print("Checking for profit targets and stop losses...")
    positions = alpaca_client.get_all_positions()
    for position in positions:
        symbol = position.symbol
        if symbol not in TICKERS:
            continue  # Skip positions not in our tickers list
        try:
            current_price = latest_prices.get(symbol)
            if current_price is None:
                print(f"No latest price available for {symbol}. Skipping.")
                continue  # Skip if price couldn't be fetched

            avg_entry_price = float(position.avg_entry_price)
            pnl_percentage = (current_price - avg_entry_price) / avg_entry_price * 100

            print(f"{symbol}: P&L = {pnl_percentage:.2f}%")

            # User-defined profit target and stop loss
            profit_target = 2.0  # 2%
            stop_loss = -2.0     # -2%

            if pnl_percentage >= profit_target or pnl_percentage <= stop_loss:
                # Sell the position
                sell([symbol])
        except Exception as e:
            print(f"Error checking P&L for {symbol}: {e}")
    print()

# Function to execute trading logic
def execute_trading_logic():
    print("Executing trading logic...")
    # Calculate ROC rankings
    roc_df = return_ROC_list(TICKERS)
    top_tickers = roc_df['Ticker'].head(1).tolist()  # Get top ticker

    # Get current positions
    positions = alpaca_client.get_all_positions()
    current_positions = [position.symbol for position in positions if position.symbol in TICKERS]

    # Determine which assets to buy or sell
    stocks_to_buy = list(set(top_tickers) - set(current_positions))
    stocks_to_sell = list(set(current_positions) - set(top_tickers))

    # Limit positions to a maximum of 5
    if len(current_positions) >= 5:
        stocks_to_buy = []

    # Adjust positions if rankings have changed
    if stocks_to_sell:
        print(f"Stocks to sell: {stocks_to_sell}")
        sell(stocks_to_sell)

    if stocks_to_buy:
        print(f"Stocks to buy: {stocks_to_buy}")
        buy(stocks_to_buy)
    print("Trading logic execution completed.\n")

# Main function to run the bot
def main():
    global initial_cash_balance

    # Start the WebSocket client in a separate thread
    websocket_thread = threading.Thread(target=start_websocket, daemon=True)
    websocket_thread.start()

    # Initialize initial_cash_balance
    account = alpaca_client.get_account()
    initial_cash_balance = float(account.cash)
    print(f"Initial cash balance: ${initial_cash_balance:.2f}")

    # Fetch historical data initially
    get_crypto_data(TICKERS)

    # Schedule the trading logic to run periodically
    schedule.every(1).minutes.do(execute_trading_logic)
    schedule.every(1).minutes.do(check_profit_and_loss)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
