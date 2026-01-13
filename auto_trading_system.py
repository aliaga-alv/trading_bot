import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import TimeFrame
import pandas as pd
from datetime import datetime, timedelta
import pytz
import os
from dotenv import load_dotenv
import sys

load_dotenv()

class AutomatedTradingSystem:
    def __init__(self):
        self.api = tradeapi.REST(
            os.getenv('APCA_API_KEY_ID'),
            os.getenv('APCA_API_SECRET_KEY'),
            'https://paper-api.alpaca.markets',
            api_version='v2'
        )
        self.symbol = "AAPL"
        
        from strategies.main_strategy import SimpleCombinedWithATR
        self.strategy = SimpleCombinedWithATR(risk_per_trade=0.02)
        
        # Telegram alerts (optional)
        self.use_telegram = False
        if os.getenv('TELEGRAM_BOT_TOKEN'):
            from telegram_alerts import TelegramAlerts
            self.telegram = TelegramAlerts()
            self.use_telegram = True
    
    def get_market_data(self):
        """Get current market data"""
        eastern = pytz.timezone('US/Eastern')
        now_et = datetime.now(eastern)
        
        # Use appropriate date range
        if now_et.year >= 2025:
            # Use historical 2023 data for testing
            end_date = datetime(2023, 12, 31, tzinfo=pytz.UTC)
            start_date = end_date - timedelta(days=60)
        else:
            # Real current data
            end_date = now_et
            start_date = end_date - timedelta(days=60)
        
        try:
            bars = self.api.get_bars(
                symbol=self.symbol,
                timeframe=TimeFrame.Day,
                start=start_date.isoformat(),
                end=end_date.isoformat(),
                feed='iex'
            )
            
            df = bars.df
            if df is None or len(df) == 0:
                return None
            
            # Convert cents to dollars
            if 'close' in df.columns and df['close'].mean() > 1000:
                price_columns = ['open', 'high', 'low', 'close']
                for col in price_columns:
                    if col in df.columns:
                        df[col] = df[col] / 100.0
            
            return df[['open', 'high', 'low', 'close', 'volume']]
            
        except Exception as e:
            print(f"❌ Data error: {e}")
            return None
    
    def execute_trading_session(self):
        """Full trading session"""
        print(f"\n{'='*60}")
        print(f"🤖 AUTOMATED TRADING SESSION")
        print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print('='*60)
        
        # 1. Account status
        account = self.api.get_account()
        equity = float(account.equity)
        print(f"💰 Account Equity: ${equity:,.2f}")
        
        # 2. Get market data
        df = self.get_market_data()
        if df is None:
            print("❌ No data available")
            return
        
        # 3. Generate signal
        df = self.strategy.generate_signals(df)
        signal = df['signal'].iloc[-1]
        signal_text = "BUY" if signal == 1 else "SELL" if signal == -1 else "HOLD"
        
        # 4. Check existing position
        try:
            position = self.api.get_position(self.symbol)
            has_position = True
            position_qty = int(position.qty)
            avg_price = float(position.avg_entry_price)
            current_price = float(position.current_price)
            pnl = float(position.unrealized_pl)
            
            print(f"\n📦 EXISTING POSITION:")
            print(f"   Shares: {position_qty}")
            print(f"   Avg Entry: ${avg_price:.2f}")
            print(f"   Current Price: ${current_price:.2f}")
            print(f"   Unrealized P&L: ${pnl:+.2f}")
        except:
            has_position = False
            print(f"\n📦 EXISTING POSITION: None")
        
        # 5. Execute trading logic
        print(f"\n🎯 STRATEGY SIGNAL: {signal_text}")
        
        TRADE_SHARES = 5
        
        if signal == 1 and not has_position:
            # BUY signal, no position
            print(f"🚀 ACTION: BUY {TRADE_SHARES} shares")
            
            try:
                order = self.api.submit_order(
                    symbol=self.symbol,
                    qty=TRADE_SHARES,
                    side='buy',
                    type='market',
                    time_in_force='day'
                )
                print(f"✅ Buy order placed: {order.id}")
                
                # Send alert
                if self.use_telegram:
                    self.telegram.send_trade_alert(
                        'BUY', self.symbol, TRADE_SHARES, current_price
                    )
                    
            except Exception as e:
                print(f"❌ Buy order failed: {e}")
                
        elif signal == -1 and has_position:
            # SELL signal, has position
            print(f"🚀 ACTION: SELL {position_qty} shares")
            
            try:
                self.api.close_position(self.symbol)
                print(f"✅ Sell order executed")
                
                # Send alert with P&L
                if self.use_telegram:
                    self.telegram.send_trade_alert(
                        'SELL', self.symbol, position_qty, current_price, pnl
                    )
                    
            except Exception as e:
                print(f"❌ Sell order failed: {e}")
                
        else:
            # HOLD
            reason = "Already invested" if has_position else "Wait for BUY signal"
            print(f"⏸️  ACTION: HOLD ({reason})")
        
        # 6. Session summary
        print(f"\n{'='*60}")
        print(f"✅ SESSION COMPLETE")
        print('='*60)
        
        # Log to file
        self.log_session(signal_text, has_position)
        
        return signal_text
    
    def log_session(self, signal, had_position):
        """Log trading session to file"""
        log_entry = f"{datetime.now()},{signal},{had_position},{self.api.get_account().equity}\n"
        
        with open('trading_log.csv', 'a') as f:
            if os.path.getsize('trading_log.csv') == 0:
                f.write("timestamp,signal,had_position,equity\n")
            f.write(log_entry)

def main():
    """Main execution with error handling"""
    print("Initializing Automated Trading System...")
    
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        return
    
    trader = AutomatedTradingSystem()
    
    try:
        # Check market hours
        clock = trader.api.get_clock()
        if not clock.is_open:
            print(f"⏸️  Market closed. Next open: {clock.next_open}")
            return
        
        # Execute trading session
        signal = trader.execute_trading_session()
        
        print(f"\n📊 Next run recommended: Tomorrow at market open")
        print(f"💡 Tip: Set up cron job for automatic daily execution")
        
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
    except Exception as e:
        print(f"\n❌ System error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
