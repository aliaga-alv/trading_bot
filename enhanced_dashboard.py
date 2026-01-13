import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import alpaca_trade_api as tradeapi
import os
from dotenv import load_dotenv
import numpy as np

load_dotenv()

class LiveDashboard:
    def __init__(self):
        self.api = tradeapi.REST(
            os.getenv('APCA_API_KEY_ID'),
            os.getenv('APCA_API_SECRET_KEY'),
            'https://paper-api.alpaca.markets',
            api_version='v2'
        )
    
    def show_dashboard(self):
        print("\n" + "="*70)
        print("📊 LIVE TRADING BOT DASHBOARD")
        print("="*70)
        
        # 1. LIVE ACCOUNT STATUS
        account = self.api.get_account()
        equity = float(account.equity)
        buying_power = float(account.buying_power)
        
        print(f"\n💰 LIVE ACCOUNT:")
        print(f"   Equity: ${equity:,.2f}")
        print(f"   Buying Power: ${buying_power:,.2f}")
        print(f"   Cash: ${float(account.cash):,.2f}")
        
        # 2. CURRENT POSITIONS
        print(f"\n📦 LIVE POSITIONS:")
        try:
            positions = self.api.list_positions()
            if positions:
                total_value = 0
                total_pnl = 0
                for pos in positions:
                    value = float(pos.market_value)
                    pnl = float(pos.unrealized_pl)
                    total_value += value
                    total_pnl += pnl
                    print(f"   {pos.symbol}: {pos.qty} shares @ ${float(pos.avg_entry_price):.2f}")
                    print(f"        Current: ${float(pos.current_price):.2f} | P&L: ${pnl:+.2f} ({float(pos.unrealized_plpc)*100:+.2f}%)")
                print(f"   TOTAL: ${total_value:,.2f} | P&L: ${total_pnl:+.2f}")
            else:
                print("   No active positions")
        except:
            print("   Error fetching positions")
        
        # 3. RECENT ORDERS
        print(f"\n📝 RECENT ORDERS (Last 5):")
        try:
            orders = self.api.list_orders(limit=5, status='all')
            for order in orders:
                filled_price = f"@ ${order.filled_avg_price}" if order.filled_avg_price else ""
                print(f"   {order.side.upper()} {order.qty} {order.symbol} {filled_price}")
                print(f"        {order.status} | {order.submitted_at}")
        except:
            print("   Error fetching orders")
        
        # 4. HISTORICAL PERFORMANCE
        if os.path.exists('trading_log.csv'):
            df = pd.read_csv('trading_log.csv')
            if len(df) > 0:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['equity'] = df['equity'].astype(float)
                
                initial = df['equity'].iloc[0]
                current = df['equity'].iloc[-1]
                total_return = ((current - initial) / initial) * 100
                
                print(f"\n📈 PERFORMANCE SUMMARY:")
                print(f"   Starting Equity: ${initial:,.2f}")
                print(f"   Current Equity: ${current:,.2f}")
                print(f"   Total Return: {total_return:+.3f}%")
                print(f"   Total P&L: ${(current - initial):+.2f}")
                print(f"   Trading Days: {len(df)}")
                
                # Daily returns
                if len(df) > 1:
                    df['daily_return'] = df['equity'].pct_change() * 100
                    avg_daily = df['daily_return'].mean()
                    best_day = df['daily_return'].max()
                    worst_day = df['daily_return'].min()
                    
                    print(f"   Avg Daily Return: {avg_daily:+.3f}%")
                    print(f"   Best Day: {best_day:+.3f}%")
                    print(f"   Worst Day: {worst_day:+.3f}%")
                
                # Generate chart
                self.generate_chart(df)
        
        # 5. NEXT SESSION INFO
        print(f"\n⏰ NEXT SESSION:")
        print(f"   Local Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"   Scheduled: Daily at 2:05 PM GMT+4 (10:05 AM ET)")
        print(f"   Status: {'🟢 ACTIVE' if os.path.exists('run_daily.sh') else '🔴 INACTIVE'}")
        
        print(f"\n" + "="*70)
        print("💡 Commands: python auto_trading_system.py | ./run_daily.sh | crontab -l")
        print("="*70)
    
    def generate_chart(self, df):
        """Generate performance chart"""
        plt.figure(figsize=(12, 8))
        
        # Equity curve
        plt.subplot(2, 2, 1)
        plt.plot(df['timestamp'], df['equity'], 'b-', linewidth=2, label='Equity')
        plt.fill_between(df['timestamp'], df['equity'], df['equity'].min(), alpha=0.1)
        plt.title('Account Equity Over Time', fontsize=12)
        plt.xlabel('Date')
        plt.ylabel('Equity ($)')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Daily returns
        plt.subplot(2, 2, 2)
        if 'daily_return' in df.columns:
            colors = ['green' if x >= 0 else 'red' for x in df['daily_return']]
            plt.bar(range(len(df)), df['daily_return'], color=colors, alpha=0.7)
            plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            plt.title('Daily Returns (%)', fontsize=12)
            plt.xlabel('Session')
            plt.ylabel('Return %')
            plt.grid(True, alpha=0.3)
        
        # Signal distribution
        plt.subplot(2, 2, 3)
        if 'signal' in df.columns:
            signals = df['signal'].value_counts()
            plt.pie(signals.values, labels=signals.index, autopct='%1.1f%%', 
                   colors=['green', 'red', 'gray'])
            plt.title('Signal Distribution', fontsize=12)
        
        # Drawdown
        plt.subplot(2, 2, 4)
        if 'equity' in df.columns:
            running_max = df['equity'].expanding().max()
            drawdown = (df['equity'] - running_max) / running_max * 100
            plt.fill_between(df['timestamp'], drawdown, 0, color='red', alpha=0.3)
            plt.plot(df['timestamp'], drawdown, 'r-', alpha=0.7)
            plt.title('Drawdown (%)', fontsize=12)
            plt.xlabel('Date')
            plt.ylabel('Drawdown %')
            plt.grid(True, alpha=0.3)
            plt.ylim([drawdown.min() - 1, 1])
        
        plt.tight_layout()
        plt.savefig('trading_dashboard.png', dpi=120, bbox_inches='tight')
        print(f"📊 Dashboard chart saved: trading_dashboard.png")
        
        # Show if in interactive environment
        try:
            plt.show()
        except:
            pass

if __name__ == "__main__":
    dashboard = LiveDashboard()
    dashboard.show_dashboard()
