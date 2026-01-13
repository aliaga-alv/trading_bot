import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import (
    SYMBOL, BACKTEST_START_DATE, BACKTEST_END_DATE, 
    INITIAL_CAPITAL, COMMISSION
)
from data.data_fetcher import DataFetcher
from strategies.main_strategy import SimpleCombinedWithATR
from backtesting.backtester import Backtester
import matplotlib.pyplot as plt

def main():
    print("="*60)
    print("🚀 TRADING BOT - PRODUCTION STRATEGY")
    print("="*60)
    
    # Initialize
    fetcher = DataFetcher(SYMBOL, BACKTEST_START_DATE, BACKTEST_END_DATE)
    strategy = SimpleCombinedWithATR()
    backtester = Backtester(initial_capital=INITIAL_CAPITAL, commission=COMMISSION)
    
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
    print(f"   Strategy: {strategy.ma_fast}/{strategy.ma_slow} EMA + RSI + ATR")
    print(f"   Period: {BACKTEST_START_DATE} to {BACKTEST_END_DATE}")
    print(f"   Initial Capital: ${INITIAL_CAPITAL:,}")
    print(f"   Final Portfolio: ${float(metrics['Final Portfolio Value'][1:].replace(',','')):,.2f}")

if __name__ == "__main__":
    main()
