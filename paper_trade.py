"""
Paper trading scanner.

IMPORTANT:
This does NOT send orders to any broker.

It generates hypothetical trade candidates.
"""

import config as cfg

from data_provider import get_ohlcv

from risk import build_risk_plan

from strategy import generate_signal


def scan_paper(
    ticker,
    timeframe="1d",
):
    """
    Generate a paper-trading candidate.
    """

    if timeframe == "1d":

        period = cfg.DAILY_PERIOD

    else:

        period = cfg.INTRADAY_PERIOD

    df = get_ohlcv(
        ticker,
        period=period,
        interval=timeframe,
    )

    signal = generate_signal(
        ticker,
        timeframe,
        df,
        cfg,
    )

    if signal is None:

        return {
            "ticker": ticker,
            "signal": None,
        }

    plan = build_risk_plan(
        signal.close,
        signal.stop_loss,
        cfg.ACCOUNT_BALANCE_EUR,
        cfg.RISK_PER_TRADE_PCT,
        cfg.MAX_POSITION_PCT,
    )

    return {
        "ticker": ticker,

        "timeframe":
            timeframe,

        "signal":
            signal.direction,

        "score":
            f"{signal.score}/{signal.max_score}",

        "entry":
            round(signal.close, 4),

        "stop":
            round(signal.stop_loss, 4),

        "target":
            round(signal.take_profit, 4),

        "quantity":
            plan.quantity,

        "risk_eur":
            plan.risk_eur,

        "notional_eur":
            plan.notional_eur,

        "reasons":
            signal.reasons,
    }


if __name__ == "__main__":

    for ticker in cfg.WATCHLIST:

        try:

            result = scan_paper(
                ticker,
                "1d",
            )

            if result["signal"]:

                print(
                    result
                )

        except Exception as exc:

            print(
                f"{ticker}: {exc}"
            )
