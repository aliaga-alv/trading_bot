import alpaca_trade_api as tradeapi
import os
from dotenv import load_dotenv
import time
from datetime import datetime, time as dt_time
import pytz

# Load environment variables
load_dotenv()

class PaperTrader:
    def __init__(self):
        self.api = tradeapi.REST(
            os.getenv('APCA_API_KEY_ID'),
            os.getenv('APCA_API_SECRET_KEY'),
            'https://paper-api.alpaca.markets',
            api_version='v2'
        )
        self.symbol = 'AAPL'
        self.position_size = 10  # Number of shares per trade
        
    def check_market_hours(self):
        """Check if the market is open"""
        clock = self.api.get_clock()
        return clock.is_open
    
    def get_account_info(self):
        """Get paper trading account information"""
        account = self.api.get_account()
        print(f"Account Equity: ${account.equity}")
        print(f"Buying Power: ${account.buying_power}")
        return account
    
    def get_current_price(self):
        """Get the current price of the symbol"""
        bars = self.api.get_bars(self.symbol, '1Min', limit=1).df
        return bars['close'].iloc[-1]
    
    def place_order(self, side='buy'):
        """Place an order (market order)"""
        try:
            order = self.api.submit_order(
                symbol=self.symbol,
                qty=self.position_size,
                side=side,
                type='market',
                time_in_force='day'
            )
            print(f"Order placed: {side.upper()} {self.position_size} {self.symbol}")
            return order
        except Exception as e:
            print(f"Error placing order: {e}")
            return None
    
    def close_position(self):
        """Close the current position for the symbol"""
        try:
            self.api.close_position(self.symbol)
            print(f"Closed position for {self.symbol}")
        except Exception as e:
            print(f"No position to close for {self.symbol}: {e}")
    
    def run_simple_strategy(self):
        """Run a simple moving average crossover strategy (for demo)"""
        # This is a simplified version for paper trading
        # In reality, you would use the same strategy logic as in backtesting
        print("Running simple strategy...")
        
        # Get recent data for the symbol
        bars = self.api.get_bars(self.symbol, '1Day', limit=200).df
        bars.columns = [col.lower() for col in bars.columns]
        
        # Calculate indicators (simplified)
        bars['sma_20'] = bars['close'].rolling(20).mean()
        bars['sma_50'] = bars['close'].rolling(50).mean()
        
        # Get the latest signal
        latest = bars.iloc[-1]
        prev = bars.iloc[-2]
        
        # Generate signal
        signal = 0
        if latest['sma_20'] > latest['sma_50'] and prev['sma_20'] <= prev['sma_50']:
            signal = 1  # Buy signal
        elif latest['sma_20'] < latest['sma_50'] and prev['sma_20'] >= prev['sma_50']:
            signal = -1  # Sell signal
        
        return signal

def main():
    trader = PaperTrader()
    
    # Check account
    trader.get_account_info()
    
    # Check market hours
    if not trader.check_market_hours():
        print("Market is closed. Exiting.")
        return
    
    # Run strategy and get signal
    signal = trader.run_simple_strategy()
    
    # Execute based on signal
    if signal == 1:
        print("Buy signal generated.")
        trader.place_order('buy')
    elif signal == -1:
        print("Sell signal generated.")
        trader.close_position()
    else:
        print("No signal.")

if __name__ == "__main__":
    main()