"""
Telegram Trading Scanner Bot - GitHub Actions version.
Each run does ONE scan (or one daily screen) and exits.
GitHub Actions scheduler triggers this file on a cron schedule instead of
the script looping forever itself.

Usage:
    python bot.py scan     -> runs the indicator scan, sends alerts if any
    python bot.py daily    -> runs the daily watch list screen
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
        "disable_web_page_preview": True,
    }
    r = requests.post(url, data=payload, timeout=15)
    if r.status_code != 200:
        print("telegram send failed:", r.status_code, r.text)


PERIOD_FOR_INTERVAL = {"5m": "1mo", "15m": "1mo"}


def fetch_ohlcv(ticker, interval):
    period = PERIOD_FOR_INTERVAL.get(interval, "1mo")
    df = yf.download(
        tickers=ticker, period=period, interval=interval,
        progress=False, auto_adjust=True,
    )
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df.dropna()


def position_size_suggestion(entry_price, stop_loss_price):
    risk_per_share = abs(entry_price - stop_loss_price)
    if risk_per_share == 0:
        return None
    risk_budget = cfg.ACCOUNT_BALANCE_EUR * (cfg.RISK_PER_TRADE_PCT / 100)
    shares = int(risk_budget / risk_per_share)
    if shares <= 0:
        return None
    move_needed = cfg.TARGET_PROFIT_EUR / shares
    return {
        "shares": shares,
        "risk_budget_eur": round(risk_budget, 2),
        "target_price": round(entry_price + move_needed, 4),
    }


def scan_ticker(ticker):
    results = {}
    for interval in cfg.TIMEFRAMES:
        try:
            df = fetch_ohlcv(ticker, interval)
            if len(df) < max(cfg.SMA_SLOW, cfg.BB_PERIOD, cfg.VOLUME_LOOKBACK) + 2:
                continue
            enriched = compute_all_indicators(df, cfg)
            latest = enriched.iloc[-1]
            results[interval] = score_signal(latest, cfg)
        except Exception as e:
            print("scan failed:", ticker, interval, e)
    return results


def format_alert(ticker, interval, result):
    direction = result["direction"]
    emoji = "UP" if direction == "BUY" else "DOWN"
    reasons = "\n".join("- " + r for r in result["reasons"])
    msg = (
        emoji + " " + direction + " signal - " + ticker + " (" + interval + ")\n"
        + "Price: " + format(result["close"], ".2f")
        + "  RSI: " + format(result["rsi"], ".1f")
        + "  Vol: " + format(result["vol_ratio"], ".1f") + "x avg\n"
        + "Confluence: " + str(result["score"]) + "/" + str(result["max_score"]) + "\n"
        + reasons + "\n"
    )
    if direction == "BUY":
        pos = position_size_suggestion(result["close"], result["close"] * 0.99)
        if pos:
            msg += (
                "\nSizing example (1% risk, 1% stop, "
                + str(cfg.TARGET_PROFIT_EUR) + " EUR target):\n"
                + "~" + str(pos["shares"]) + " shares, risk approx "
                + str(pos["risk_budget_eur"]) + " EUR, target price approx "
                + str(pos["target_price"]) + "\n"
                + "(Set your own real stop loss - this is illustrative math only.)"
            )
    msg += "\nNot financial advice - verify before acting."
    return msg


def run_scan_cycle():
    print("Running scan over", len(cfg.WATCHLIST), "tickers")
    any_alerts = False
    for ticker in cfg.WATCHLIST:
        try:
            results = scan_ticker(ticker)
            for interval, result in results.items():
                if result["direction"] is not None:
                    send_telegram_message(format_alert(ticker, interval, result))
                    any_alerts = True
        except Exception:
            print("scan_cycle error on", ticker)
            traceback.print_exc()
    if not any_alerts:
        print("No signals this cycle.")


def run_daily_screen():
    print("Running daily screen")
    scored = []
    for ticker in cfg.DAILY_SCREEN_UNIVERSE:
        try:
            df = fetch_ohlcv(ticker, "15m")
            if len(df) < cfg.VOLUME_LOOKBACK + 2:
                continue
            enriched = compute_all_indicators(df, cfg)
            latest = enriched.iloc[-1]
            vol_ratio = latest["vol_ratio"]
            recent_range = (df["High"] - df["Low"]).rolling(cfg.VOLUME_LOOKBACK).mean().iloc[-1]
            today_range = df["High"].iloc[-1] - df["Low"].iloc[-1]
            volatility_ratio = today_range / recent_range if recent_range else 0
            interest_score = (vol_ratio or 0) + volatility_ratio
            scored.append((ticker, interest_score, vol_ratio, volatility_ratio, latest["Close"]))
        except Exception as e:
            print("daily_screen failed:", ticker, e)

    scored.sort(key=lambda x: x[1], reverse=True)
    top = scored[:5]

    if not top:
        send_telegram_message("Daily screen: no data available today.")
        return

    lines = ["Today's watchlist candidates (by volume + volatility):\n"]
    for ticker, score, vr, volr, close in top:
        lines.append(
            "- " + ticker + " price " + format(close, ".2f")
            + ", volume " + format(vr, ".1f") + "x avg, range "
            + format(volr, ".1f") + "x normal"
        )
    lines.append(
        "\nScreened for unusual activity, not guaranteed opportunities. "
        "Check news and catalysts before trading."
    )
    send_telegram_message("\n".join(lines))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "scan"
    if mode == "daily":
        run_daily_screen()
    else:
        run_scan_cycle()
