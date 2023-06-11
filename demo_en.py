Import relevant libraries
import okx.demo_account_api as account # Use simulation account API
import okx.demo_futures_api as future # Use simulation futures API
import time
import numpy as np
import talib

API key information
api_key = 'YOUR_API_KEY'
secret_key = 'YOUR_SECRET_KEY'
passphrase = 'YOUR_PASSPHRASE'

Trading parameters
"""
symbol: The cryptocurrency pair you want to trade. Here it is BTC/USDT.
interval: The K-line time interval you want to use. Here it is hourly K-line.
quantity: The quantity for each order. Here it is 1 BTC.
stop_loss_pct: Stop loss ratio. When the price falls below a certain percentage, stop loss will be triggered. Here it is set as 2%.
take_profit_pct: Take profit ratio. When the price rises above a certain percentage, take profit will be triggered. Here it is set as 2%.
leverage: Leverage multiplier. Here it is set as 10.
"""

symbol = 'btc-usdt'
interval = '1h'
quantity = 1
stop_loss_pct = 0.02
take_profit_pct = 0.02
leverage = 10

class OKXTrader:
def init(self, api_key, secret_key, passphrase):
try:
# Initialize account API and futures API
self.account_api = account.AccountAPI(api_key, secret_key, passphrase, True)
self.future_api = future.FutureAPI(api_key, secret_key, passphrase, True)
# Initialize historical K-line cache
self.historical_klines = {}
except Exception as e:
# Print error information and close API connection when an error occurs
print(f'Error occurred while initializing the API: {e}')
self.future_api = None
self.account_api = None

def __del__(self):
    try:
        # Close API connection
        if self.future_api is not None:
            self.future_api.close()
        if self.account_api is not None:
            self.account_api.close()
    except Exception as e:
        # Print error information when an error occurs
        print(f'Error occurred while closing the API connection: {e}')

def get_historical_klines(self, symbol, interval, limit):
    """
    Get historical K-line data

    :param symbol: Trading pair
    :param interval: K-line period
    :param limit: Number of K-lines returned
    :return: Time, high price, low price and closing price of historical K-line data
    """
    # Check whether there is already K-line data for this trading pair in the historical K-line cache
    if symbol in self.historical_klines and interval in self.historical_klines[symbol]:
        times, high_prices, low_prices, close_prices = self.historical_klines[symbol][interval]
    else:
        times, high_prices, low_prices, close_prices = None, None, None, None
        try:
            # Get historical K-line data
            kline_data = self.future_api.get_kline(symbol=symbol, interval=interval, limit=limit)

            # Convert k-line data to numpy array
            klines = np.array(kline_data['data'])

            # Separate different price data
            times = klines[:, 0]
            high_prices = klines[:, 2].astype(float)
            low_prices = klines[:, 3].astype(float)
            close_prices = klines[:, 4].astype(float)

            # Cache K-line data
            if symbol not in self.historical_klines:
                self.historical_klines[symbol] = {}
            self.historical_klines[symbol][interval] = (times, high_prices, low_prices, close_prices)

        except Exception as e:
            # Print error information when an error occurs
            print(f'Error occurred while getting historical K-line data: {e}')

    # Return different price data
    return times, high_prices, low_prices, close_prices

def calculate_super_trend(self(times, high_prices, low_prices, close_prices, period=10, multiplier=3):
"""
Calculate the SuperTrend indicator

    :param times: Time data of historical K-lines
    :param high_prices: Historical high price data
    :param low_prices: Historical low price data
    :param close_prices: Historical closing price data
    :param period: Period parameter of ATR calculation
    :param multiplier: Multiplier parameter of ATR calculation
    :return: SuperTrend values of historical K-line data
    """
    # Calculate ATR
    atr = talib.ATR(high_prices, low_prices, close_prices, timeperiod=period)
    # Calculate Upper and Lower Supertrend
    upperband = ((high_prices + low_prices) / 2) + (multiplier * atr)
    lowerband = ((high_prices + low_prices) / 2) - (multiplier * atr)

    # Initialize supertrend to the first value
    supertrend = np.zeros_like(close_prices)
    if len(close_prices)>0:
        supertrend[0] = 0.0

    # Loop through prices to calculate supertrend using previous values
    for i in range(1, len(close_prices)):
        if close_prices[i] > supertrend[i-1]:
            supertrend[i] = upperband[i]
        else:
            supertrend[i] = lowerband[i]

    return supertrend

def get_current_price(self, symbol):
    """
    Get the current price of a trading pair

    :param symbol: Trading pair
    :return: Current price
    """
    current_price = None
    try:
        # Get ticker data
        ticker_data = self.future_api.get_ticker(symbol=symbol)
        # Extract current price
        current_price = float(ticker_data['last'])
    except Exception as e:
        # Print error information when an error occurs
        print(f'Error occurred while getting current price: {e}')

    return current_price

def place_order(self, symbol, quantity, trade_type, price=None):
    """
    Place an order

    :param symbol: Trading pair
    :param quantity: Order quantity
    :param trade_type: Order type (buy/sell)
    :param price: Order price (optional)
    :return: Order ID
    """
    order_id = None
    try:
        if price is None:
            # Market order
            order_data = self.future_api.place_market_order(symbol=symbol, quantity=quantity, trade_type=trade_type,
                                                            leverage=leverage)
        else:
            # Limit order
            order_data = self.future_api.place_limit_order(symbol=symbol, quantity=quantity, trade_type=trade_type,
                                                           price=price, leverage=leverage)

        # Extract order ID
        order_id = order_data.get('order_id')
    except Exception as e:
        # Print error information when an error occurs
        print(f'Error occurred while placing the order: {e}')

    return order_id

def cancel_order(self, symbol, order_id):
    """
    Cancel an order

    :param symbol: Trading pair
    :param order_id: Order ID
    :return: True if successful, False otherwise
    """
    success = False
    try:
        # Cancel the order
        self.future_api.cancel_order(symbol=symbol, order_id=order_id)
        success = True
    except Exception as e:
        # Print error information when an error occurs
        print(f'Error occurred while cancelling the order: {e}')

    return success

def run_strategy(self, symbol, interval, quantity, stop_loss_pct, take_profit_pct):
    """
    Run the trading strategy

    :param symbol: Trading pair
    :param interval: K-line period
    :param quantity: Quantity for each order
    :param stop_loss_pct: Stop loss ratio
    :param take_profit_pct: Take profit ratio
    :return: None
    """
    # Get initial historical K-line data and supertrend values
    times, high_prices, low_prices, close_prices = self.get_historical_klines(symbol=symbol, interval=interval,
                                                                               limit=100)
    supertrend_values = self.calculate_super_trend(times, high_prices, low_prices, close_prices)

    # Initialize variables for the current trade
    current_position = None
    current_entry_price = None
    stop_loss_price = None
    take_profit_price = None

    while True:
        try:
            # Wait for 5 minutes before checking the price again
            time.sleep(300)
            # Get the latest price
            current_price = self.get_current_price(symbol=symbol)

            # If there # is no current price, skip this iteration
            if current_price is None:
                continue

            # Calculate new supertrend value for the latest K-line data
            times, high_prices, low_prices, close_prices = self.get_historical_klines(symbol=symbol,
                                                                                       interval=interval, limit=1)
            supertrend_values = np.append(supertrend_values, self.calculate_super_trend(times, high_prices,
                                                                                       low_prices, close_prices)[-1])

            # If there is an open position, check if stop loss or take profit has been triggered
            if current_position is not None:
                unrealized_pnl = (current_price - current_entry_price) * quantity * (1 if current_position == 'long' else -1)
                if unrealized_pnl < 0 and abs(unrealized_pnl / current_entry_price) >= stop_loss_pct:
                    # Close the position with a market order
                    self.place_order(symbol=symbol, quantity=quantity, trade_type='sell' if current_position == 'long' else 'buy')
                    # Reset variables for the current trade
                    current_position = None
                    current_entry_price = None
                    stop_loss_price = None
                    take_profit_price = None
                elif unrealized_pnl > 0 and abs(unrealized_pnl / current_entry_price) >= take_profit_pct:
                    # Close the position with a market order
                    self.place_order(symbol=symbol, quantity=quantity, trade_type='sell' if current_position == 'long' else 'buy')
                    # Reset variables for the current trade
                    current_position = None
                    current_entry_price = None
                    stop_loss_price = None
                    take_profit_price = None
                else:
                    # Update stop loss and take profit prices based on current price and supertrend values
                    if current_position == 'long':
                        stop_loss_price = max(stop_loss_price, supertrend_values[-1]) if stop_loss_price is not None else supertrend_values[-1]
                        take_profit_price = min(take_profit_price, (current_entry_price * (1 + take_profit_pct))) if take_profit_price is not None else (current_entry_price * (1 + take_profit_pct))
                    else:
                        stop_loss_price = min(stop_loss_price, supertrend_values[-1]) if stop_loss_price is not None else supertrend_values[-1]
                        take_profit_price = max(take_profit_price, (current_entry_price * (1 - take_profit_pct))) if take_profit_price is not None else (current_entry_price * (1 - take_profit_pct))

            # If there is no open position, check if a new position should be opened
            else:
                # Check if the current price is above or below the supertrend line
                if current_price > supertrend_values[-1]:
                    # Place a long order with a limit price equal to the current price
                    order_id = self.place_order(symbol=symbol, quantity=quantity, trade_type='buy', price=current_price)
                    if order_id is not None:
                        # Update variables for the current trade
                        current_position = 'long'
                        current_entry_price = current_price
                        stop_loss_price = supertrend_values[-1]
                        take_profit_price = current_entry_price * (1 + take_profit_pct)
                elif current_price < supertrend_values[-1]:
                    # Place a short order with a limit price equal to the current price
                    order_id = self.place_order(symbol=symbol, quantity=quantity, trade_type='sell', price=current_price)
                    if order_id is not None:
                        # Update variables for the current trade
                        current_position = 'short'
                        current_entry_price = current_price
                        stop_loss_price = supertrend_values[-1]
                        take_profit_price = current_entry_price * (1 - take_profit_pct)
        except KeyboardInterrupt:
            # If the user stops the program, print a message and exit the loop
            print('Program stopped by user.')
            break
        except Exception as e:
            # Print error information when an error occurs
            print(f'Error occurred while running the strategy: {e}')



