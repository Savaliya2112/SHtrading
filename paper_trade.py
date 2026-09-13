"""
Manual/paper-trading helper only.

This file NEVER sends orders to a broker.
"""


def position_size(account_value, risk_percent, entry, stop):
    risk_cash = account_value * (risk_percent / 100.0)
    risk_per_share = abs(entry - stop)

    if risk_per_share <= 0:
        raise ValueError("Entry and stop must be different.")

    return int(risk_cash / risk_per_share)


def paper_trade_summary(ticker, direction, entry, stop, target, quantity):
    return {
        "ticker": ticker,
        "direction": direction,
        "entry": float(entry),
        "stop": float(stop),
        "target": float(target),
        "quantity": int(quantity),
        "live_order": False,
    }
