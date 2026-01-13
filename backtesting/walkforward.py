# backtesting/walkforward.py
class WalkForwardTester:
    def run_walkforward(self, df, strategy, train_months=24, test_months=6):
        """Walk-forward validation"""
        results = []
        
        # Split data into overlapping windows
        total_months = len(df) // 21  # Approximate months
        start_idx = 0
        
        while start_idx + train_months + test_months <= total_months:
            # Define windows
            train_end = start_idx + train_months
            test_end = train_end + test_months
            
            # Split data
            train_data = df.iloc[start_idx:train_end]
            test_data = df.iloc[train_end:test_end]
            
            # Optimize on training data
            best_params = self.optimize_params(train_data)
            strategy.set_params(**best_params)
            
            # Test on out-of-sample data
            test_result = self.run_backtest(test_data, strategy)
            results.append(test_result)
            
            start_idx += test_months  # Move window forward
        
        return pd.DataFrame(results)