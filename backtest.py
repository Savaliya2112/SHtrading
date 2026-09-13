"""
SHtrading historical backtester.

This module is for research only.
It does NOT place real trades.

Features:
- Entry on the next candle
- Stop-loss handling
- Take-profit handling
- Position sizing
- Transaction costs
- Equity curve
- Maximum drawdown
- Win rate
- Profit factor
- Average win/loss
- Consecutive losses
"""

import argparse

import config as cfg

from data_provider import get_ohlcv
from risk import build_risk_plan
from strategy import generate_signal


def calculate_max_drawdown(equity_curve):
    """Calculate maximum percentage drawdown."""

    if not equity_curve:
        return 0.0

    peak = equity_curve[0]
    max_drawdown = 0.0

    for equity in equity_curve:

        if equity > peak:
            peak = equity

        if peak > 0:

            drawdown = (
                (equity - peak)
                / peak
                * 100
            )

            max_drawdown = min(
                max_drawdown,
                drawdown,
            )

    return abs(max_drawdown)


def calculate_max_losing_streak(trades):
    """Calculate maximum consecutive losing trades."""

    current = 0
    maximum = 0

    for pnl in trades:

        if pnl < 0:

            current += 1

            maximum = max(
                maximum,
                current,
            )

        else:

            current = 0

    return maximum


def run_backtest(
    ticker,
    period="2y",
    interval="1d",
):
    """Run historical backtest."""

    df = get_ohlcv(
        ticker,
        period=period,
        interval=interval,
    )

    starting_equity = (
        cfg.ACCOUNT_BALANCE_EUR
    )

    equity = starting_equity

    trades = []

    equity_curve = [
        equity
    ]

    warmup = max(
        cfg.SMA_SLOW,
        cfg.BB_PERIOD,
        cfg.VOLUME_LOOKBACK,
        cfg.ATR_PERIOD,
    ) + 5

    i = warmup

    while i < len(df) - 1:

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

            i += 1

            equity_curve.append(
                equity
            )

            continue

        # ----------------------------------------------------
        # ENTRY
        # ----------------------------------------------------

        entry_index = i + 1

        entry_price = float(
            df["Open"].iloc[
                entry_index
            ]
        )

        # Recalculate risk based on actual
        # next-candle entry price.

        if signal.direction == "BUY":

            stop_distance = (
                signal.close
                - signal.stop_loss
            )

            stop_price = (
                entry_price
                - stop_distance
            )

            target_distance = (
                stop_distance
                * cfg.REWARD_RISK_RATIO
            )

            target_price = (
                entry_price
                + target_distance
            )

        else:

            stop_distance = (
                signal.stop_loss
                - signal.close
            )

            stop_price = (
                entry_price
                + stop_distance
            )

            target_distance = (
                stop_distance
                * cfg.REWARD_RISK_RATIO
            )

            target_price = (
                entry_price
                - target_distance
            )

        # ----------------------------------------------------
        # POSITION SIZE
        # ----------------------------------------------------

        plan = build_risk_plan(
            entry_price,
            stop_price,
            equity,
            cfg.RISK_PER_TRADE_PCT,
            cfg.MAX_POSITION_PCT,
        )

        if plan.quantity <= 0:

            i += 1

            continue

        # ----------------------------------------------------
        # FIND EXIT
        # ----------------------------------------------------

        exit_price = None
        exit_reason = None
        exit_index = entry_index

        for j in range(
            entry_index,
            len(df),
        ):

            candle_high = float(
                df["High"].iloc[j]
            )

            candle_low = float(
                df["Low"].iloc[j]
            )

            if signal.direction == "BUY":

                stop_hit = (
                    candle_low
                    <= stop_price
                )

                target_hit = (
                    candle_high
                    >= target_price
                )

                # Conservative assumption:
                # if both are hit in the same candle,
                # assume stop was hit first.

                if (
                    stop_hit
                    and target_hit
                ):

                    exit_price = (
                        stop_price
                    )

                    exit_reason = (
                        "STOP_AND_TARGET_SAME_CANDLE"
                    )

                    exit_index = j

                    break

                if stop_hit:

                    exit_price = (
                        stop_price
                    )

                    exit_reason = "STOP"

                    exit_index = j

                    break

                if target_hit:

                    exit_price = (
                        target_price
                    )

                    exit_reason = "TARGET"

                    exit_index = j

                    break

            else:

                stop_hit = (
                    candle_high
                    >= stop_price
                )

                target_hit = (
                    candle_low
                    <= target_price
                )

                if (
                    stop_hit
                    and target_hit
                ):

                    exit_price = (
                        stop_price
                    )

                    exit_reason = (
                        "STOP_AND_TARGET_SAME_CANDLE"
                    )

                    exit_index = j

                    break

                if stop_hit:

                    exit_price = (
                        stop_price
                    )

                    exit_reason = "STOP"

                    exit_index = j

                    break

                if target_hit:

                    exit_price = (
                        target_price
                    )

                    exit_reason = "TARGET"

                    exit_index = j

                    break

        # ----------------------------------------------------
        # FORCE EXIT AT LAST CLOSE
        # ----------------------------------------------------

        if exit_price is None:

            exit_index = len(df) - 1

            exit_price = float(
                df["Close"].iloc[
                    exit_index
                ]
            )

            exit_reason = (
                "END_OF_DATA"
            )

        # ----------------------------------------------------
        # P&L
        # ----------------------------------------------------

        if signal.direction == "BUY":

            gross_pnl = (
                exit_price
                - entry_price
            ) * plan.quantity

        else:

            gross_pnl = (
                entry_price
                - exit_price
            ) * plan.quantity

        entry_cost = (
            entry_price
            * plan.quantity
            * cfg.TRANSACTION_COST_PCT
            / 100
        )

        exit_cost = (
            exit_price
            * plan.quantity
            * cfg.TRANSACTION_COST_PCT
            / 100
        )

        total_cost = (
            entry_cost
            + exit_cost
        )

        net_pnl = (
            gross_pnl
            - total_cost
        )

        equity += net_pnl

        trades.append(
            net_pnl
        )

        equity_curve.append(
            equity
        )

        # Jump to the candle after exit.
        i = exit_index + 1

    # ========================================================
    # STATISTICS
    # ========================================================

    winning_trades = [
        pnl
        for pnl in trades
        if pnl > 0
    ]

    losing_trades = [
        pnl
        for pnl in trades
        if pnl < 0
    ]

    trade_count = len(
        trades
    )

    win_rate = (
        len(winning_trades)
        / trade_count
        * 100
        if trade_count
        else 0
    )

    gross_profit = sum(
        winning_trades
    )

    gross_loss = abs(
        sum(losing_trades)
    )

    if gross_loss > 0:

        profit_factor = (
            gross_profit
            / gross_loss
        )

    else:

        profit_factor = None

    average_win = (
        gross_profit
        / len(winning_trades)
        if winning_trades
        else 0
    )

    average_loss = (
        gross_loss
        / len(losing_trades)
        if losing_trades
        else 0
    )

    maximum_drawdown = (
        calculate_max_drawdown(
            equity_curve
        )
    )

    maximum_losing_streak = (
        calculate_max_losing_streak(
            trades
        )
    )

    total_return = (
        (
            equity
            / starting_equity
        )
        - 1
    ) * 100

    return {
        "ticker": ticker,

        "period": period,

        "interval": interval,

        "starting_equity":
            round(
                starting_equity,
                2,
            ),

        "final_equity":
            round(
                equity,
                2,
            ),

        "return_pct":
            round(
                total_return,
                2,
            ),

        "trades":
            trade_count,

        "winning_trades":
            len(winning_trades),

        "losing_trades":
            len(losing_trades),

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

        "average_win_eur":
            round(
                average_win,
                2,
            ),

        "average_loss_eur":
            round(
                average_loss,
                2,
            ),

        "max_drawdown_pct":
            round(
                maximum_drawdown,
                2,
            ),

        "max_losing_streak":
            maximum_losing_streak,
    }


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description=(
            "Run SHtrading historical backtest"
        )
    )

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

    print()
    print(
        "================================"
    )
    print(
        "       SHtrading BACKTEST"
    )
    print(
        "================================"
    )

    for key, value in result.items():

        print(
            f"{key}: {value}"
        )

    print(
        "================================"
    )
