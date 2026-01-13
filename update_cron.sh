#!/bin/bash
# Remove old ET-based schedule
crontab -l | grep -v "trading_bot" | crontab -

# Add for YOUR timezone (GMT+4)
# Run at 2:05 PM local time (10:05 AM ET)
(crontab -l 2>/dev/null; echo "# Trading Bot - 2:05 PM GMT+4 (10:05 AM ET)") | crontab -
(crontab -l 2>/dev/null; echo "5 14 * * 1-5 /Users/ali/trading_bot/run_daily.sh") | crontab -

echo "✅ Cron job set for 2:05 PM GMT+4 daily (10:05 AM ET)"
echo "Current schedule:"
crontab -l
