import pandas as pd
import numpy as np
from config.settings import (
    FAST_MA, SLOW_MA, RSI_PERIOD, RSI_OVERSOLD, RSI_OVERBOUGHT,
    ATR_PERIOD, RISK_PER_TRADE, ATR_MULTIPLIER
)

class SimpleCombinedWithATR:
    def __init__(self, risk_per_trade=None):
        self.ma_fast = FAST_MA
        self.ma_slow = SLOW_MA
        self.rsi_period = RSI_PERIOD
        self.rsi_oversold = RSI_OVERSOLD
        self.rsi_overbought = RSI_OVERBOUGHT
        self.atr_period = ATR_PERIOD
        self.risk_per_trade = risk_per_trade or RISK_PER_TRADE
        self.atr_multiplier = ATR_MULTIPLIER
        
    def calculate_indicators(self, df):
        df = df.copy()
        
        # Moving Averages (EMA for faster response)
        df['ma_fast'] = df['close'].ewm(span=self.ma_fast, adjust=False).mean()
        df['ma_slow'] = df['close'].ewm(span=self.ma_slow, adjust=False).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).ewm(span=self.rsi_period, adjust=False).mean()
        loss = (-delta.where(delta < 0, 0)).ewm(span=self.rsi_period, adjust=False).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # ATR (Average True Range) for risk management
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift())
        low_close = abs(df['low'] - df['close'].shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['atr'] = true_range.rolling(self.atr_period).mean()
        
        return df
    
    def generate_signals(self, df):
        df = self.calculate_indicators(df)
        
        # Initialize
        df['signal'] = 0
        df['position_size'] = 0.0  # % of capital to risk
        df['stop_loss'] = 0.0
        
        # Buy conditions
        buy_condition = (
            (df['ma_fast'] > df['ma_slow']) & 
            (df['rsi'] > self.rsi_oversold) & 
            (df['rsi'] < self.rsi_overbought)
        )
        
        # Sell conditions
        sell_condition = (
            (df['ma_fast'] < df['ma_slow']) | 
            (df['rsi'] > self.rsi_overbought)
        )
        
        df.loc[buy_condition, 'signal'] = 1
        df.loc[sell_condition, 'signal'] = -1
        
        # Calculate position size based on ATR (risk management)
        # Position size = Risk per trade / (ATR * multiplier)
        for i in range(len(df)):
            if df['signal'].iloc[i] == 1 and df['atr'].iloc[i] > 0:
                df.iloc[i, df.columns.get_loc('position_size')] = min(
                    self.risk_per_trade / (df['atr'].iloc[i] * self.atr_multiplier / df['close'].iloc[i]),
                    1.0  # Max 100% position
                )
                df.iloc[i, df.columns.get_loc('stop_loss')] = df['close'].iloc[i] - (df['atr'].iloc[i] * self.atr_multiplier)
        
        # Position logic
        position = 0
        positions = []
        for sig in df['signal']:
            if sig == 1:
                position = 1
            elif sig == -1:
                position = 0
            positions.append(position)
        
        df['position'] = positions
        df['position'] = df['position'].shift(1).fillna(0)
        
        print(f"📊 Strategy with ATR:")
        print(f"   Buy signals: {sum(df['signal'] == 1)}")
        print(f"   Sell signals: {sum(df['signal'] == -1)}")
        print(f"   Days invested: {sum(df['position'] == 1)} of {len(df)}")
        print(f"   Avg ATR: ${df['atr'].mean():.2f} ({df['atr'].mean()/df['close'].mean()*100:.1f}% of price)")
        
        return df
