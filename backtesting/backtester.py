import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class Backtester:
    """Simple backtesting engine"""
    
    def __init__(self, initial_capital=10000, commission=0.001):
        self.initial_capital = initial_capital
        self.commission = commission
        
    def run_backtest(self, df, strategy):
        """Run a basic backtest with commission"""
        print("🔄 Running backtest...")
        
        # Generate signals from strategy
        df = strategy.generate_signals(df)
        
        # Calculate strategy returns without commission
        df['strategy_returns_raw'] = df['position'] * df['returns']
        
        # Calculate commission adjustment
        df['position_change'] = df['position'].diff().fillna(0)
        df['commission_adj'] = 0.0
        # When we enter (position changes from 0 to 1) we pay commission
        df.loc[df['position_change'] == 1, 'commission_adj'] = -self.commission
        # When we exit (position changes from 1 to 0) we pay commission
        df.loc[df['position_change'] == -1, 'commission_adj'] = -self.commission
        
        # Adjust returns by commission
        df['strategy_returns'] = df['strategy_returns_raw'] + df['commission_adj']
        
        # Cumulative returns
        df['cumulative_strategy'] = (1 + df['strategy_returns']).cumprod()
        df['cumulative_market'] = (1 + df['returns']).cumprod()
        
        # Portfolio value
        df['portfolio_value'] = self.initial_capital * df['cumulative_strategy']
        
        # Calculate metrics
        metrics = self.calculate_metrics(df)
        
        return df, metrics
    
    def calculate_metrics(self, df):
        """Calculate performance metrics"""
        # Total returns
        total_return_strategy = df['cumulative_strategy'].iloc[-1] - 1
        total_return_market = df['cumulative_market'].iloc[-1] - 1
        
        # Sharpe ratio
        returns = df['strategy_returns'].dropna()
        if len(returns) > 0 and returns.std() > 0:
            sharpe_ratio = np.sqrt(252) * returns.mean() / returns.std()
        else:
            sharpe_ratio = 0
        
        # Max drawdown
        cumulative = df['cumulative_strategy']
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Win rate (of round trips)
        # We define a trade as a period when we are in the market (from entry to exit)
        # But for simplicity, let's use the position change to identify trades
        # We'll count the number of entries that resulted in a profit
        # Note: This is a simplified win rate calculation
        entries = df[df['position_change'] == 1]
        exits = df[df['position_change'] == -1]
        
        win_rate = 0
        if len(entries) > 0 and len(exits) > 0:
            # We'll match each entry with the next exit (assuming we are always in the market)
            # This is a simplified approach and might not be accurate if there are multiple entries without exits
            # We assume the strategy is always in the market after an entry until an exit
            profits = []
            for i in range(min(len(entries), len(exits))):
                entry_price = entries.iloc[i]['close']
                exit_price = exits.iloc[i]['close']
                profit = (exit_price - entry_price) / entry_price
                profits.append(profit)
            
            if profits:
                win_rate = sum(1 for p in profits if p > 0) / len(profits)
        
        # Total commission paid
        total_commission_pct = abs(df['commission_adj'].sum())
        total_commission_dollars = self.initial_capital * total_commission_pct
        
        # Number of round trips (entry and exit pairs)
        num_round_trips = min((df['position_change'] == 1).sum(), (df['position_change'] == -1).sum())
        
        metrics = {
            'Total Return (Strategy)': f"{total_return_strategy * 100:.2f}%",
            'Total Return (Market)': f"{total_return_market * 100:.2f}%",
            'Sharpe Ratio': f"{sharpe_ratio:.2f}",
            'Max Drawdown': f"{max_drawdown * 100:.2f}%",
            'Win Rate': f"{win_rate * 100:.2f}%",
            'Number of Trades': f"{num_round_trips}",
            'Final Portfolio Value': f"${df['portfolio_value'].iloc[-1]:,.2f}",
            'Total Commission Paid': f"${total_commission_dollars:.2f}"
        }
        
        return metrics
    
    def plot_results(self, df, symbol="AAPL"):
        """Plot backtest results"""
        print("📊 Generating charts...")
        
        fig, axes = plt.subplots(2, 1, figsize=(12, 8))
        
        # Plot 1: Price and position
        axes[0].plot(df.index, df['close'], label='Price', alpha=0.7)
        axes[0].set_title(f'{symbol} - Price')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Plot 2: Cumulative returns
        axes[1].plot(df.index, df['cumulative_strategy'], 
                    label='Strategy', linewidth=2)
        axes[1].plot(df.index, df['cumulative_market'], 
                    label='Buy & Hold', linewidth=2, alpha=0.7)
        axes[1].set_title('Cumulative Returns')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
