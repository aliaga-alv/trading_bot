import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

def show_performance():
    """Show trading performance dashboard"""
    print("\n" + "="*60)
    print("📊 TRADING BOT PERFORMANCE DASHBOARD")
    print("="*60)
    
    # Check if log exists
    if not os.path.exists('trading_log.csv'):
        print("No trading data yet. Run the bot during market hours.")
        return
    
    # Load data
    df = pd.read_csv('trading_log.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    print(f"\n📈 TRADING SUMMARY:")
    print(f"   Total Sessions: {len(df)}")
    print(f"   First Trade: {df['timestamp'].min().strftime('%Y-%m-%d')}")
    print(f"   Last Trade: {df['timestamp'].max().strftime('%Y-%m-%d')}")
    
    # Calculate performance
    df['equity'] = df['equity'].astype(float)
    initial_equity = df['equity'].iloc[0] if len(df) > 0 else 100000
    current_equity = df['equity'].iloc[-1] if len(df) > 0 else 100000
    total_return = ((current_equity - initial_equity) / initial_equity) * 100
    
    print(f"\n💰 PERFORMANCE METRICS:")
    print(f"   Initial Equity: ${initial_equity:,.2f}")
    print(f"   Current Equity: ${current_equity:,.2f}")
    print(f"   Total Return: {total_return:+.2f}%")
    print(f"   Total P&L: ${(current_equity - initial_equity):+.2f}")
    
    # Signal distribution
    if 'signal' in df.columns:
        signals = df['signal'].value_counts()
        print(f"\n🎯 SIGNAL DISTRIBUTION:")
        for signal, count in signals.items():
            print(f"   {signal}: {count} sessions ({count/len(df)*100:.1f}%)")
    
    # Plot equity curve
    if len(df) > 1:
        plt.figure(figsize=(10, 6))
        plt.plot(df['timestamp'], df['equity'], 'b-', linewidth=2)
        plt.fill_between(df['timestamp'], df['equity'], initial_equity, 
                        where=(df['equity'] >= initial_equity), 
                        alpha=0.3, color='green')
        plt.fill_between(df['timestamp'], df['equity'], initial_equity,
                        where=(df['equity'] < initial_equity),
                        alpha=0.3, color='red')
        
        plt.title('Trading Bot Equity Curve', fontsize=14)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Account Equity ($)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Save and show
        plt.savefig('equity_curve.png', dpi=100)
        print(f"\n📈 Equity curve saved to: equity_curve.png")
        plt.show()
    
    print(f"\n" + "="*60)
    print("Next: Run 'python auto_trading_system.py' during market hours")
    print("="*60)

if __name__ == "__main__":
    show_performance()
