#!/bin/bash
cd /Users/ali/trading_bot
source venv/bin/activate

echo "========================================" >> trading_sessions.log
date >> trading_sessions.log
echo "========================================" >> trading_sessions.log

python auto_trading_system.py >> trading_sessions.log 2>&1

echo "" >> trading_sessions.log
