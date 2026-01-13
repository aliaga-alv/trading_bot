# paper_trading_real.py - FINAL CORRECTED VERSION
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import TimeFrame
import pandas as pd
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()


class RealPaperTrader:
    def __init__(self):
        """Initialize Alpaca API and trading strategy"""
        self.api = tradeapi.REST(
            os.getenv("APCA_API_KEY_ID"),
            os.getenv("APCA_API_SECRET_KEY"),
            "https://paper-api.alpaca.markets",
            api_version="v2",
        )
        self.symbol = "AAPL"

        # Import your proven trading strategy
        from strategies.main_strategy import SimpleCombinedWithATR

        self.strategy = SimpleCombinedWithATR(risk_per_trade=0.02)

    def get_real_data(self, days=30):  # Changed from 200 to 30
        """Fetch market data for current/future dates"""
        from datetime import datetime, timedelta
        import pytz

        # Use Eastern Time
        eastern = pytz.timezone("US/Eastern")
        now_et = datetime.now(eastern)

        print(f"🕒 Current Date: {now_et.strftime('%Y-%m-%d %H:%M:%S ET')}")

        # For dates in 2026, we need to use historical 2023-2024 data
        # since real 2026 data doesn't exist yet
        if now_et.year >= 2025:
            print("⚠️  Using historical data (real 2026 data not available)")
            # Use 2023 data as proxy
            end_date = datetime(2023, 12, 31, tzinfo=pytz.UTC)
            start_date = end_date - timedelta(days=days)
        else:
            # Normal case for current year
            end_date = now_et
            start_date = end_date - timedelta(days=days)

        # Ensure dates are in UTC for API
        if end_date.tzinfo is None:
            end_date = pytz.UTC.localize(end_date)
        if start_date.tzinfo is None:
            start_date = pytz.UTC.localize(start_date)

        try:
            print(f"📡 Requesting data: {start_date.date()} to {end_date.date()}")

            # Try to get data
            bars = self.api.get_bars(
                symbol=self.symbol,
                timeframe=TimeFrame.Day,
                start=start_date.isoformat(),
                end=end_date.isoformat(),
                feed="iex",
                limit=1000,  # Max rows
            )

            df = bars.df
            if df is None or len(df) == 0:
                print("❌ No data received. Possible reasons:")
                print("   - Date range has no trading days")
                print("   - Symbol may be incorrect")
                print("   - API permissions issue")
                return None

            print(f"✅ Received {len(df)} trading days of data")

            # Check and convert price format
            if "close" in df.columns and df["close"].mean() > 1000:
                print("🔄 Converting price data from cents to dollars...")
                price_columns = ["open", "high", "low", "close", "vwap"]
                for col in price_columns:
                    if col in df.columns:
                        df[col] = df[col] / 100.0

            # Display sample data
            print(f"\n📊 SAMPLE DATA (first 3 rows):")
            for i in range(min(3, len(df))):
                date_str = df.index[i].strftime("%Y-%m-%d")
                close_price = df["close"].iloc[i]
                print(f"   {date_str}: ${close_price:.2f}")

            print(f"📊 LATEST DATA (last row):")
            print(
                f"   {df.index[-1].strftime('%Y-%m-%d')}: ${df['close'].iloc[-1]:.2f}"
            )

            # Ensure correct column names
            column_map = {
                "o": "open",
                "h": "high",
                "l": "low",
                "c": "close",
                "v": "volume",
            }
            df.rename(columns=column_map, inplace=True)

            # Ensure we have all required columns
            required_cols = ["open", "high", "low", "close", "volume"]
            missing = [col for col in required_cols if col not in df.columns]
            if missing:
                print(f"❌ Missing columns: {missing}")
                print(f"   Available: {list(df.columns)}")
                return None

            return df[required_cols]

        except Exception as e:
            print(f"❌ Data fetch error: {e}")
            import traceback

            traceback.print_exc()
            return None

    def run_trading_session(self):
        """Execute one complete trading decision cycle"""
        print("\n" + "=" * 60)
        print("🤖 ALGORITHMIC TRADING BOT - LIVE PAPER TRADING")
        print("=" * 60)

        # 1. ACCOUNT STATUS
        account = self.api.get_account()
        equity = float(account.equity)
        buying_power = float(account.buying_power)
        print(f"💰 PAPER ACCOUNT:")
        print(f"   Equity: ${equity:,.2f}")
        print(f"   Buying Power: ${buying_power:,.2f}")

        # 2. MARKET DATA
        print(f"\n📊 FETCHING MARKET DATA...")
        df = self.get_real_data(days=200)

        if df is None:
            print("❌ Cannot proceed without market data.")
            return

        print(f"✅ Data loaded: {len(df)} trading days")
        print(f"   Symbol: {self.symbol}")
        # CORRECTED: Use the actual price from the dataframe
        latest_date = df.index[-1].strftime("%Y-%m-%d")
        latest_price = df["close"].iloc[-1]
        print(f"   Latest: {latest_date} at ${latest_price:.2f}")  # FIXED LINE
        print(
            f"   Range: {df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}"
        )

        # 3. STRATEGY SIGNAL GENERATION
        print(f"\n🎯 GENERATING TRADING SIGNAL...")
        df = self.strategy.generate_signals(df)
        latest_signal = df["signal"].iloc[-1]
        current_position = df["position"].iloc[-1]

        signal_text = (
            "BUY" if latest_signal == 1 else "SELL" if latest_signal == -1 else "HOLD"
        )
        position_text = "INVESTED" if current_position == 1 else "CASH"

        print(f"📈 STRATEGY DECISION:")
        print(f"   Signal: {signal_text}")
        print(f"   Model Position: {position_text}")
        print(f"   Buy signals in period: {sum(df['signal'] == 1)}")
        print(f"   Sell signals in period: {sum(df['signal'] == -1)}")

        # 4. CHECK EXISTING POSITION
        try:
            position = self.api.get_position(self.symbol)
            has_position = True
            position_qty = int(position.qty)
            avg_price = float(position.avg_entry_price)
            current_value = float(position.market_value)
            print(f"\n📦 EXISTING POSITION:")
            print(f"   Shares: {position_qty}")
            print(f"   Avg Entry: ${avg_price:.2f}")
            print(f"   Current Value: ${current_value:,.2f}")
            print(f"   Unrealized P&L: ${float(position.unrealized_pl):,.2f}")
        except:
            has_position = False
            print(f"\n📦 EXISTING POSITION: None")

        # 5. EXECUTE TRADING LOGIC
        print(f"\n" + "=" * 60)
        print(f"🚀 TRADING EXECUTION")
        print("=" * 60)

        # TRADE PARAMETERS
        SHARES_TO_TRADE = 5

        if latest_signal == 1 and not has_position:
            # BUY SIGNAL
            print(f"✅ EXECUTING BUY ORDER")
            print(f"   Action: BUY {SHARES_TO_TRADE} shares of {self.symbol}")
            print(f"   Estimated Cost: ${SHARES_TO_TRADE * latest_price:.2f}")

            try:
                order = self.api.submit_order(
                    symbol=self.symbol,
                    qty=SHARES_TO_TRADE,
                    side="buy",
                    type="market",
                    time_in_force="day",
                )
                print(f"   Order ID: {order.id}")
                print(f"   Status: {order.status}")
            except Exception as e:
                print(f"❌ Order failed: {e}")

        elif latest_signal == -1 and has_position:
            # SELL SIGNAL
            print(f"✅ EXECUTING SELL ORDER")
            print(f"   Action: SELL {position_qty} shares of {self.symbol}")

            try:
                self.api.close_position(self.symbol)
                print(f"   Position closed successfully")
            except Exception as e:
                print(f"❌ Close position failed: {e}")

        else:
            # NO ACTION
            action_reason = ""
            if has_position and latest_signal != -1:
                action_reason = "Hold existing position (signal not SELL)"
            elif not has_position and latest_signal != 1:
                action_reason = "Wait for BUY signal"
            elif has_position and latest_signal == -1:
                action_reason = "Should sell but position check failed"
            elif not has_position and latest_signal == 1:
                action_reason = "Should buy but position check failed"

            print(f"⏸️  NO TRADE EXECUTED")
            print(f"   Reason: {action_reason}")

        # 6. SESSION SUMMARY
        print(f"\n" + "=" * 60)
        print(f"✅ SESSION COMPLETE")
        print("=" * 60)
        print(f"Next steps:")
        print(f"1. Check position on Alpaca Dashboard")
        print(f"2. Run again during next market session")
        print(f"3. Monitor strategy performance weekly")


# MAIN EXECUTION
if __name__ == "__main__":
    import sys

    print("Initializing Trading Bot...")

    # Check for .env file
    if not os.path.exists(".env"):
        print("❌ ERROR: .env file not found!")
        print("Create a .env file with:")
        print("APCA_API_KEY_ID=your_key_here")
        print("APCA_API_SECRET_KEY=your_secret_here")
        sys.exit(1)

    # Create trader instance
    trader = RealPaperTrader()

    # Run trading session
    try:
        trader.run_trading_session()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
