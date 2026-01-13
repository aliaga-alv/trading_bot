import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.data_fetcher import DataFetcher
from strategies.main_strategy import SimpleCombinedWithATR
from backtesting.backtester import Backtester
import matplotlib.pyplot as plt

# Settings
SYMBOL = "AAPL"
START_DATE = "2020-01-01"
END_DATE = "2023-12-31"
INITIAL_CAPITAL = 10000

def main():
    print("="*60)
    print("🚀 TRADING BOT - PRODUCTION STRATEGY")
    print("="*60)
    
    # Initialize
    fetcher = DataFetcher(SYMBOL, START_DATE, END_DATE)
    strategy = SimpleCombinedWithATR(risk_per_trade=0.02)
    backtester = Backtester(initial_capital=INITIAL_CAPITAL)
    
    # Fetch data
    print(f"\n1. Fetching {SYMBOL} data...")
    df = fetcher.fetch_historical_data()
    
    # Run backtest
    print("\n2. Running strategy...")
    results, metrics = backtester.run_backtest(df, strategy)
    
    # Show results
    print("\n" + "="*60)
    print("📊 FINAL RESULTS")
    print("="*60)
    for key, value in metrics.items():
        print(f"{key:25}: {value}")
    print("="*60)
    
    # Save to CSV
    results.to_csv(f'trading_results_{SYMBOL}.csv')
    print(f"\n📄 Results saved to: trading_results_{SYMBOL}.csv")
    
    # Plot
    print("\n3. Generating charts...")
    fig = backtester.plot_results(results, SYMBOL)
    fig.savefig('trading_charts.png', dpi=300, bbox_inches='tight')
    
    print("\n✅ Trading bot complete!")
    print("   Strategy: 20/50 EMA + RSI + ATR")
    print(f"   Period: {START_DATE} to {END_DATE}")
    print(f"   Initial Capital: ${INITIAL_CAPITAL:,}")
    print(f"   Final Portfolio: ${float(metrics['Final Portfolio Value'][1:].replace(',','')):,.2f}")

if __name__ == "__main__":
    main()
