import time
import os
from datetime import datetime, timedelta
import subprocess
import sys

def monitor_trading_bot():
    """Monitor trading bot in real-time"""
    print("📊 TRADING BOT LIVE MONITOR")
    print("="*60)
    print("Monitors: trading_sessions.log | Positions | Account")
    print("Press Ctrl+C to stop")
    print("="*60)
    
    log_file = 'trading_sessions.log'
    iteration = 0
    
    try:
        while True:
            iteration += 1
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"\n🔄 Update #{iteration} - {current_time}")
            print("-"*40)
            
            # 1. Show latest log entries
            if os.path.exists(log_file):
                print("📝 RECENT LOG ENTRIES:")
                try:
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                        if lines:
                            # Show last relevant lines
                            recent = [l for l in lines[-20:] if l.strip()]
                            for line in recent[-5:]:
                                # Clean up the output
                                clean_line = line.rstrip()[:80] + "..." if len(line) > 80 else line.rstrip()
                                print(f"  {clean_line}")
                        else:
                            print("  Log file empty")
                except:
                    print("  Error reading log")
            else:
                print("📝 No log file yet")
            
            # 2. File info
            if os.path.exists(log_file):
                size_kb = os.path.getsize(log_file) / 1024
                mod_time = datetime.fromtimestamp(os.path.getmtime(log_file))
                print(f"\n💾 Log: {size_kb:.1f} KB, updated: {mod_time.strftime('%H:%M:%S')}")
            
            # 3. Next scheduled run
            now = datetime.now()
            next_run = now.replace(hour=14, minute=5, second=0, microsecond=0)
            if now > next_run:
                next_run += timedelta(days=1)
            
            # Skip weekends
            while next_run.weekday() >= 5:
                next_run += timedelta(days=1)
            
            time_left = next_run - now
            hours = time_left.seconds // 3600
            minutes = (time_left.seconds % 3600) // 60
            
            print(f"\n⏰ NEXT SCHEDULED RUN:")
            print(f"  Time: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  In: {hours}h {minutes}m")
            
            # 4. Quick position check (every 3 updates)
            if iteration % 3 == 0:
                print(f"\n🔍 QUICK POSITION CHECK:")
                try:
                    # Simple position check without full imports
                    check_code = '''
import alpaca_trade_api as tradeapi
import os
from dotenv import load_dotenv
load_dotenv()
api = tradeapi.REST(os.getenv("APCA_API_KEY_ID"), os.getenv("APCA_API_SECRET_KEY"), "https://paper-api.alpaca.markets")
try:
    pos = api.get_position("AAPL")
    print(f"AAPL: {pos.qty} shares, P&L: ${float(pos.unrealized_pl):+.2f}")
except:
    print("AAPL: No position")
'''
                    result = subprocess.run(
                        [sys.executable, '-c', check_code],
                        capture_output=True,
                        text=True
                    )
                    if result.stdout:
                        print(f"  {result.stdout.strip()}")
                except:
                    print("  Position check failed")
            
            print("-"*40)
            print("Sleeping 60 seconds... (Ctrl+C to stop)")
            
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Monitor stopped by user")
        print("="*60)

if __name__ == "__main__":
    monitor_trading_bot()
