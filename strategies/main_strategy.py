import pandas as pd
import numpy as np

class SimpleCombinedWithATR:
    def __init__(self, risk_per_trade=0.02):  # 2% risk per trade
        self.ma_fast = 20
        self.ma_slow = 50
        self.rsi_period = 14
        self.atr_period = 14
        self.risk_per_trade = risk_per_trade
        
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
            (df['rsi'] > 40) & 
            (df['rsi'] < 80)
        )
        
        # Sell conditions
        sell_condition = (
            (df['ma_fast'] < df['ma_slow']) | 
            (df['rsi'] > 85)
        )
        
        df.loc[buy_condition, 'signal'] = 1
        df.loc[sell_condition, 'signal'] = -1
        
        # Calculate position size based on ATR (risk management)
        # Position size = Risk per trade / (ATR * 1.5)
        # This means we risk 2% of capital, stop loss is 1.5x ATR away
        for i in range(len(df)):
            if df['signal'].iloc[i] == 1 and df['atr'].iloc[i] > 0:
                df.iloc[i, df.columns.get_loc('position_size')] = min(
                    self.risk_per_trade / (df['atr'].iloc[i] * 1.5 / df['close'].iloc[i]),
                    1.0  # Max 100% position
                )
                df.iloc[i, df.columns.get_loc('stop_loss')] = df['close'].iloc[i] - (df['atr'].iloc[i] * 1.5)
        
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
