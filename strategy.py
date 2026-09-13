"""
SHtrading multi-factor strategy.

The strategy combines:

- Trend
- Momentum
- RSI
- MACD
- Bollinger Bands
- Volume

It generates signals only.

It NEVER places a live order.
"""

from dataclasses import dataclass

from indicators import compute_all_indicators


@dataclass
class Signal:

    ticker: str

    timeframe: str

    direction: str

    score: int

    max_score: int

    close: float

    stop_loss: float

    take_profit: float

    reasons: list


def generate_signal(
    ticker,
    timeframe,
    df,
    cfg,
):
    """
    Generate a transparent trading signal.
    """

    enriched = compute_all_indicators(
        df,
        cfg
    )

    enriched = enriched.dropna()

    if enriched.empty:
        return None

    row = enriched.iloc[-1]

    buy_score = 0
    sell_score = 0

    buy_reasons = []
    sell_reasons = []

    # --------------------------------------------------------
    # TREND
    # --------------------------------------------------------

    if row["ema_fast"] > row["ema_slow"]:

        buy_score += 1

        buy_reasons.append(
            "EMA trend bullish"
        )

    elif row["ema_fast"] < row["ema_slow"]:

        sell_score += 1

        sell_reasons.append(
            "EMA trend bearish"
        )

    # --------------------------------------------------------
    # SMA TREND
    # --------------------------------------------------------

    if row["sma_fast"] > row["sma_slow"]:

        buy_score += 1

        buy_reasons.append(
            "SMA trend bullish"
        )

    elif row["sma_fast"] < row["sma_slow"]:

        sell_score += 1

        sell_reasons.append(
            "SMA trend bearish"
        )

    # --------------------------------------------------------
    # MACD
    # --------------------------------------------------------

    if row["macd_hist"] > 0:

        buy_score += 1

        buy_reasons.append(
            "MACD momentum positive"
        )

    elif row["macd_hist"] < 0:

        sell_score += 1

        sell_reasons.append(
            "MACD momentum negative"
        )

    # --------------------------------------------------------
    # RSI
    # --------------------------------------------------------

    rsi_value = row["rsi"]

    if 50 <= rsi_value <= 68:

        buy_score += 1

        buy_reasons.append(
            f"RSI bullish ({rsi_value:.1f})"
        )

    elif 32 <= rsi_value < 50:

        sell_score += 1

        sell_reasons.append(
            f"RSI bearish ({rsi_value:.1f})"
        )

    # --------------------------------------------------------
    # BOLLINGER
    # --------------------------------------------------------

    if row["Close"] > row["bb_mid"]:

        buy_score += 1

        buy_reasons.append(
            "Price above Bollinger midpoint"
        )

    elif row["Close"] < row["bb_mid"]:

        sell_score += 1

        sell_reasons.append(
            "Price below Bollinger midpoint"
        )

    # --------------------------------------------------------
    # VOLUME
    # --------------------------------------------------------

    volume_ratio = row["vol_ratio"]

    if volume_ratio >= cfg.VOLUME_SPIKE_MULTIPLIER:

        if buy_score > sell_score:

            buy_score += 1

            buy_reasons.append(
                f"Volume confirmation ({volume_ratio:.1f}x)"
            )

        elif sell_score > buy_score:

            sell_score += 1

            sell_reasons.append(
                f"Volume confirmation ({volume_ratio:.1f}x)"
            )

    # --------------------------------------------------------
    # FINAL SIGNAL
    # --------------------------------------------------------

    max_score = 6

    if (
        buy_score >= cfg.MIN_SIGNAL_SCORE
        and buy_score > sell_score
    ):

        direction = "BUY"

        score = buy_score

        reasons = buy_reasons

    elif (
        sell_score >= cfg.MIN_SIGNAL_SCORE
        and sell_score > buy_score
    ):

        direction = "SELL"

        score = sell_score

        reasons = sell_reasons

    else:

        return None

    # --------------------------------------------------------
    # STOP / TARGET
    # --------------------------------------------------------

    close = float(row["Close"])

    atr_value = float(row["atr"])

    stop_distance = max(
        atr_value *
        cfg.ATR_STOP_MULTIPLIER,

        close *
        cfg.MIN_STOP_PCT,
    )

    reward_distance = (
        stop_distance *
        cfg.REWARD_RISK_RATIO
    )

    if direction == "BUY":

        stop_loss = (
            close -
            stop_distance
        )

        take_profit = (
            close +
            reward_distance
        )

    else:

        stop_loss = (
            close +
            stop_distance
        )

        take_profit = (
            close -
            reward_distance
        )

    return Signal(
        ticker=ticker,
        timeframe=timeframe,
        direction=direction,
        score=score,
        max_score=max_score,
        close=close,
        stop_loss=stop_loss,
        take_profit=take_profit,
        reasons=reasons,
    )
