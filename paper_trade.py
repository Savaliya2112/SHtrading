import config as cfg

from data_provider import get_ohlcv
from risk import build_risk_plan
from strategy import generate_signal


def scan_paper(
    ticker,
    timeframe="1d",
):
    """
    Analyse a market in paper mode.

    IMPORTANT:
    This function NEVER sends a broker order.
    """

    if timeframe == "1d":
        period = cfg.DAILY_PERIOD
    else:
        period = cfg.INTRADAY_PERIOD

    df = get_ohlcv(
        ticker=ticker,
        period=period,
        interval=timeframe,
    )

    signal = generate_signal(
        ticker=ticker,
        timeframe=timeframe,
        df=df,
        cfg=cfg,
    )

    if signal is None:
        return {
            "ticker": ticker,
            "timeframe": timeframe,
            "signal": None,
        }

    risk_plan = build_risk_plan(
        entry=signal.close,
        stop=signal.stop_loss,
        account_eur=cfg.ACCOUNT_BALANCE_EUR,
        risk_pct=cfg.RISK_PER_TRADE_PCT,
        max_notional_pct=cfg.MAX_NOTIONAL_PCT,
    )

    return {
        "ticker": ticker,
        "timeframe": timeframe,
        "signal": signal.direction,
        "score": (
            f"{signal.score}/"
            f"{signal.max_score}"
        ),
        "entry": signal.close,
        "stop": signal.stop_loss,
        "target": signal.take_profit,
        "quantity": risk_plan.quantity,
        "risk_eur": risk_plan.risk_eur,
        "notional_eur": risk_plan.notional_eur,
        "reasons": signal.reasons,
    }


def run_paper_scan():
    """Scan the complete configured universe."""

    print("")
    print("=" * 70)
    print("SHtrading PAPER SCAN")
    print("=" * 70)

    results = []

    timeframes = list(
        cfg.INTRADAY_TIMEFRAMES
    )

    if cfg.SWING_TIMEFRAME not in timeframes:
        timeframes.append(
            cfg.SWING_TIMEFRAME
        )

    for ticker in cfg.WATCHLIST:

        for timeframe in timeframes:

            try:

                result = scan_paper(
                    ticker,
                    timeframe,
                )

                if not result.get(
                    "signal"
                ):
                    continue

                results.append(
                    result
                )

                print("")
                print(
                    f"{ticker} | "
                    f"{timeframe}"
                )

                print(
                    f"Signal: "
                    f"{result['signal']}"
                )

                print(
                    f"Score: "
                    f"{result['score']}"
                )

                print(
                    f"Entry: "
                    f"{result['entry']:.2f}"
                )

                print(
                    f"Stop: "
                    f"{result['stop']:.2f}"
                )

                print(
                    f"Target: "
                    f"{result['target']:.2f}"
                )

                print(
                    f"Quantity: "
                    f"{result['quantity']}"
                )

                print(
                    f"Risk: "
                    f"€{result['risk_eur']:.2f}"
                )

            except Exception as exc:

                print(
                    f"{ticker} | "
                    f"{timeframe} | "
                    f"ERROR: {exc}"
                )

    print("")
    print("=" * 70)
    print(
        f"Signals found: {len(results)}"
    )
    print("=" * 70)
    print(
        "NO REAL ORDERS WERE PLACED."
    )
    print("")

    return results


if __name__ == "__main__":
    run_paper_scan()
