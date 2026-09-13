"""
Telegram Trading Scanner Bot — GitHub Actions version.
Each run does ONE scan (or one daily screen) and exits.
GitHub Actions' scheduler triggers this file on a cron schedule instead of
the script looping forever itself.

Usage:
    python bot.py scan     -> runs the indicator scan, sends alerts if any
    python bot.py daily    -> runs the daily "what to watch" screen
"""

import sys
import traceback

import requests
import pandas as pd
import yfinance as yf

import config as cfg
from indicators import compute_all_indicators, score_signal


def send_telegram_message(text: str):
    url = f"https://api.telegram.org/bot{cfg.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": cfg.TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markd
