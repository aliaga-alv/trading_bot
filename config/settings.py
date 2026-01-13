# config/settings.py - Central Configuration

import os
from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# TRADING PARAMETERS
# =============================================================================
SYMBOL = os.getenv("TRADING_SYMBOL", "AAPL")

# Position sizing - risk % of actual account balance
RISK_PERCENT = float(os.getenv("RISK_PERCENT", "0.025"))  # 2.5% risk per trade

# Legacy (fallback)
TRADE_SHARES = int(os.getenv("TRADE_SHARES", "5"))
INITIAL_CAPITAL = float(os.getenv("INITIAL_CAPITAL", "1000"))

# Backtesting date range
BACKTEST_START_DATE = "2020-01-01"
BACKTEST_END_DATE = "2023-12-31"

# =============================================================================
# STRATEGY PARAMETERS
# =============================================================================
FAST_MA = 20          # Fast EMA period
SLOW_MA = 50          # Slow EMA period
RSI_PERIOD = 14       # RSI calculation period
RSI_OVERSOLD = 40     # RSI buy threshold
RSI_OVERBOUGHT = 85   # RSI sell threshold
ATR_PERIOD = 14       # ATR calculation period

# =============================================================================
# RISK MANAGEMENT
# =============================================================================
RISK_PER_TRADE = 0.02   # 2% risk per trade
ATR_MULTIPLIER = 1.5    # Stop loss = ATR * multiplier
COMMISSION = 0.001      # 0.1% commission per trade

# =============================================================================
# API CONFIGURATION
# =============================================================================
ALPACA_API_KEY = os.getenv("APCA_API_KEY_ID")
ALPACA_SECRET_KEY = os.getenv("APCA_API_SECRET_KEY")
ALPACA_BASE_URL = "https://paper-api.alpaca.markets"

# =============================================================================
# TELEGRAM (Optional)
# =============================================================================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")