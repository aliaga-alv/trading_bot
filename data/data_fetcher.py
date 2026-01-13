# data/data_fetcher.py - Data acquisition module
import yfinance as yf
import pandas as pd

class DataFetcher:
    def __init__(self, symbol, start_date, end_date):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        
    def fetch_historical_data(self):
        """Fetch OHLCV data from Yahoo Finance"""
        try:
            print(f"📥 Fetching data for {self.symbol}...")
            ticker = yf.Ticker(self.symbol)
            df = ticker.history(start=self.start_date, end=self.end_date)
            
            # Clean the data
            df.columns = [col.lower() for col in df.columns]
            if 'adj close' in df.columns:
                df.rename(columns={'adj close': 'close'}, inplace=True)
            
            # Ensure we have required columns
            required_cols = ['open', 'high', 'low', 'close', 'volume']
            for col in required_cols:
                if col not in df.columns:
                    raise ValueError(f"Missing column: {col}")
            
            # Calculate daily returns
            df['returns'] = df['close'].pct_change()
            
            print(f"✅ Successfully fetched {len(df)} trading days")
            print(f"   Date range: {df.index[0].date()} to {df.index[-1].date()}")
            
            return df
            
        except Exception as e:
            print(f"❌ Error fetching data: {e}")
            return None