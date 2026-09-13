"""
Basic historical backtest.

This is a research tool.

It does NOT guarantee future performance.
"""

import argparse

import config as cfg

from data_provider import get_ohlcv

from risk import build_risk_plan

from strategy import generate_signal


def run_backtest(
    ticker,
    period="2y",
    interval="1d",
):
    df = get_ohlcv(
        ticker,
        period=period,
        interval=interval,
    )

    equity = cfg.ACCOUNT_BALANCE_EUR

    trades = []

    warmup = max(
        cfg.SMA_SLOW,
        cfg.BB_PERIOD,
        cfg.VOLUME_LOOKBACK,
        cfg.ATR_PERIOD,
    ) + 5

    for i in range(
        warmup,
        len(df) - 1,
    ):

        window = df.iloc[
            : i + 1
        ]

        signal = generate_signal(
            ticker,
            interval,
            window,
            cfg,
        )

        if signal is None:
            continue

        plan = build_risk_plan(
            signal.close,
            signal.stop_loss,
            equity,
            cfg.RISK_PER_TRADE_PCT,
            cfg.MAX_POSITION_PCT,
        )

        if plan.quantity <= 0:
            continue

        next_close = float(
            df["Close"].iloc[i + 1]
        )

        if signal.direction == "BUY":

            if next_close <= signal.stop_loss:

                exit_price = signal.stop_loss

            elif next_close >= signal.take_profit:

                exit_price = signal.take_profit

            else:

                exit_price = next_close

            pnl = (
                exit_price -
                signal.close
            ) * plan.quantity

        else:

            if next_close >= signal.stop_loss:

                exit_price = signal.stop_loss

            elif next_close <= signal.take_profit:

                exit_price = signal.take_profit

            else:

                exit_price = next_close

            pnl = (
                signal.close -
                exit_price
            ) * plan.quantity

        transaction_cost = (
            abs(
                exit_price *
                plan.quantity
            )
            * cfg.TRANSACTION_COST_PCT
            / 100
        )

        pnl -= transaction_cost

        equity += pnl

        trades.append(
            pnl
        )

    winning_trades = [
        pnl
        for pnl in trades
        if pnl > 0
    ]

    losing_trades = [
        pnl
        for pnl in trades
        if pnl <= 0
    ]

    gross_profit = sum(
        winning_trades
    )

    gross_loss = abs(
        sum(losing_trades)
    )

    trade_count = len(trades)

    win_rate = (
        len(winning_trades)
        / trade_count
        * 100
        if trade_count
        else 0
    )

    profit_factor = (
        gross_profit /
        gross_loss
        if gross_loss
        else None
    )

    return {
        "ticker":
            ticker,

        "trades":
            trade_count,

        "starting_equity":
            cfg.ACCOUNT_BALANCE_EUR,

        "final_equity":
            round(equity, 2),

        "return_pct":
            round(
                (
                    equity /
                    cfg.ACCOUNT_BALANCE_EUR
                    - 1
                ) * 100,
                2,
            ),

        "win_rate_pct":
            round(
                win_rate,
                2,
            ),

        "profit_factor":
            round(
                profit_factor,
                2,
            )
            if profit_factor is not None
            else None,
    }


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "ticker"
    )

    parser.add_argument(
        "--period",
        default="2y",
    )

    parser.add_argument(
        "--interval",
        default="1d",
    )

    args = parser.parse_args()

    result = run_backtest(
        args.ticker,
        args.period,
        args.interval,
    )

    print(
        "\nBACKTEST RESULT"
    )

    for key, value in result.items():

        print(
            f"{key}: {value}"
        )
