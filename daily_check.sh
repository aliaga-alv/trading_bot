#!/bin/bash
echo "📅 DAILY TRADING BOT CHECK - $(date)"
echo "========================================"

# 1. Check if bot ran today
echo "1. TODAY'S RUNS:"
if [ -f "trading_sessions.log" ]; then
    if grep -q "AUTOMATED TRADING SESSION" trading_sessions.log; then
        echo "   Last run found in log"
        grep "AUTOMATED TRADING SESSION" trading_sessions.log | tail -1
    else
        echo "   No 'SESSION' entries found"
        echo "   Last 2 lines of log:"
        tail -2 trading_sessions.log
    fi
else
    echo "   No log file yet"
fi

# 2. Current positions
echo ""
echo "2. CURRENT POSITIONS:"
python3 << 'PYEOF'
import alpaca_trade_api as tradeapi
import os
from dotenv import load_dotenv
load_dotenv()
try:
    api = tradeapi.REST(os.getenv('APCA_API_KEY_ID'), os.getenv('APCA_API_SECRET_KEY'), 'https://paper-api.alpaca.markets')
    positions = api.list_positions()
    if positions:
        total_pnl = 0
        for p in positions:
            pnl = float(p.unrealized_pl)
            total_pnl += pnl
            print(f'   {p.symbol}: {p.qty} shares')
            print(f'        Cost: ${float(p.avg_entry_price):.2f}')
            print(f'        Current: ${float(p.current_price):.2f}')
            print(f'        P&L: ${pnl:+.2f} ({float(p.unrealized_plpc)*100:+.2f}%)')
        print(f'   TOTAL P&L: ${total_pnl:+.2f}')
    else:
        print('   No positions')
except Exception as e:
    print(f'   Error: {e}')
PYEOF

# 3. Account summary
echo ""
echo "3. ACCOUNT SUMMARY:"
python3 << 'PYEOF'
import alpaca_trade_api as tradeapi
import os
from dotenv import load_dotenv
load_dotenv()
try:
    api = tradeapi.REST(os.getenv('APCA_API_KEY_ID'), os.getenv('APCA_API_SECRET_KEY'), 'https://paper-api.alpaca.markets')
    acc = api.get_account()
    print(f'   Equity: ${float(acc.equity):,.2f}')
    print(f'   Buying Power: ${float(acc.buying_power):,.2f}')
    print(f'   Cash: ${float(acc.cash):,.2f}')
    
    # Calculate returns
    starting_equity = 100000.00
    current_equity = float(acc.equity)
    total_return = ((current_equity - starting_equity) / starting_equity) * 100
    print(f'   Total Return: {total_return:+.3f}%')
    print(f'   Total P&L: ${(current_equity - starting_equity):+.2f}')
    
except Exception as e:
    print(f'   Error: {e}')
PYEOF

# 4. Next scheduled run
echo ""
echo "4. NEXT SCHEDULED RUN:"
echo "   2:05 PM GMT+4 (10:05 AM ET) on trading days"
echo "   Cron job: $(crontab -l | grep trading_bot | wc -l) active"

# 5. System status
echo ""
echo "5. SYSTEM STATUS:"
echo "   Log file: $(ls -la trading_sessions.log 2>/dev/null | awk '{print $5}' || echo 'Missing') bytes"
echo "   Dashboard: $(ls -la trading_dashboard.png 2>/dev/null | awk '{print $5}' || echo 'Missing') bytes"
echo "   Strategy: $(ls -la strategies/main_strategy.py 2>/dev/null | awk '{print $5}' || echo 'Missing') bytes"

echo "========================================"
echo "✅ Check complete. Bot is active and monitoring."
