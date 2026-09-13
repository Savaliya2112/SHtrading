import config as cfg

from data_provider import get_ohlcv
from risk import build_risk_plan
from strategy import generate_signal


def scan_paper(
    ticker,
    timeframe="1d",
):
    """
    Generate a paper-trading signal.

    IMPORTANT:
    This function NEVER sends an order to a broker.
    """

    if timeframe == "1d":
        period = cfg.DAILY_PERIOD
    else:
        period = cfg.INTRADAY_PERIOD

    # Get market data
    df = get_ohlcv(
        ticker=ticker,
        period=period,
        interval=timeframe,
    )

    # Generate technical signal
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

    # Calculate position size
    risk_plan = build_risk_plan(
        entry=signal.close,
        stop=signal.stop_loss,
        account_eur=cfg.ACCOUNT_BALANCE_EUR,
        risk_pct=cfg.RISK_PER_TRADE_PCT,
        max_position_pct=cfg.MAX_POSITION_PCT,
    )

    return {
        "ticker": ticker,
        "timeframe": timeframe,
        "signal": signal.direction,
        "score": (
            f"{signal.score}/"
            f"{signal.max_score}"
        ),
        "entry": round(
            signal.close,
            4,
        ),
        "stop": round(
            signal.stop_loss,
            4,
        ),
        "target": round(
            signal.take_profit,
            4,
        ),
        "quantity": risk_plan.quantity,
        "risk_eur": risk_plan.risk_eur,
        "notional_eur": risk_plan.notional_eur,
        "reasons": signal.reasons,
    }


def run_paper_scan():
    """
    Scan the entire watchlist in paper mode.
    """

    print("")
    print("=" * 60)
    print("SHtrading PAPER TRADING SCAN")
    print("=" * 60)
    print("")

    results = []

    for ticker in cfg.WATCHLIST:

        try:

            result = scan_paper(
                ticker=ticker,
                timeframe=cfg.SWING_TIMEFRAME,
            )

            if result.get("signal"):

                results.append(
                    result
                )

                print("")
                print(
                    f"{ticker}: "
                    f"{result['signal']}"
                )

                print(
                    f"Score: "
                    f"{result['score']}"
                )

                print(
                    f"Entry: "
                    f"{result['entry']}"
                )

                print(
                    f"Stop: "
                    f"{result['stop']}"
                )

                print(
                    f"Target: "
                    f"{result['target']}"
                )

                print(
                    f"Quantity: "
                    f"{result['quantity']}"
                )

                print(
                    f"Risk: €"
                    f"{result['risk_eur']:.2f}"
                )

            else:

                print(
                    f"{ticker}: "
                    "No qualifying signal"
                )

        except Exception as exc:

            print(
                f"{ticker}: ERROR - {exc}"
            )

    print("")
    print("=" * 60)
    print(
        f"Qualified paper signals: "
        f"{len(results)}"
    )
    print("=" * 60)
    print("")
    print(
        "NO REAL ORDERS WERE PLACED."
    )
    print("")

    return results


if __name__ == "__main__":

    run_paper_scan()
