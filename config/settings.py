# config/settings.py - Configuration settings

# Trading parameters
SYMBOL = "AAPL"
START_DATE = "2020-01-01"
END_DATE = "2023-12-31"
INITIAL_CAPITAL = 10000

# Strategy parameters
FAST_MA = 50
SLOW_MA = 200
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

# Risk management
STOP_LOSS_PCT = 0.02  # 2% stop loss
COMMISSION = 0.001  # 0.1% commission per trade