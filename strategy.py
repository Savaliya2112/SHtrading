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


def _safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def generate_signal(
    ticker,
    timeframe,
    df,
    cfg,
):
    """
    Generate a technical BUY or SELL signal.

    This function ONLY analyses market data.
    It does not place broker orders.
    """

    if df is None or df.empty:
        return None

    enriched = compute_all_indicators(
        df,
        cfg,
    )

    # We need a complete latest candle.
    enriched = enriched.dropna(
        subset=[
            "sma_fast",
            "sma_slow",
            "ema_fast",
            "ema_slow",
            "rsi",
            "macd",
            "macd_signal",
            "macd_hist",
            "bb_upper",
            "bb_mid",
            "bb_lower",
            "atr",
            "vol_ratio",
        ]
    )

    if enriched.empty:
        return None

    row = enriched.iloc[-1]

    close = _safe_float(
        row["Close"]
    )

    atr_value = _safe_float(
        row["atr"]
    )

    if close is None or close <= 0:
        return None

    if atr_value is None or atr_value <= 0:
        return None

    buy_score = 0
    sell_score = 0

    buy_reasons = []
    sell_reasons = []

    # ========================================================
    # TREND — EMA
    # ========================================================

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

    # ========================================================
    # TREND — SMA
    # ========================================================

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

    # ========================================================
    # MOMENTUM — MACD
    # ========================================================

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

    # ========================================================
    # MOMENTUM — RSI
    # ========================================================

    rsi_value = _safe_float(
        row["rsi"]
    )

    if rsi_value is not None:

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

    # ========================================================
    # PRICE — BOLLINGER MIDPOINT
    # ========================================================

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

    # ========================================================
    # VOLUME CONFIRMATION
    # ========================================================

    volume_ratio_value = _safe_float(
        row["vol_ratio"]
    )

    if (
        volume_ratio_value is not None
        and volume_ratio_value
        >= cfg.VOLUME_SPIKE_MULTIPLIER
    ):

        if buy_score > sell_score:
            buy_score += 1
            buy_reasons.append(
                f"Volume confirmation "
                f"({volume_ratio_value:.1f}x)"
            )

        elif sell_score > buy_score:
            sell_score += 1
            sell_reasons.append(
                f"Volume confirmation "
                f"({volume_ratio_value:.1f}x)"
            )

    max_score = 6

    # ========================================================
    # FINAL SIGNAL
    # ========================================================

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

    # ========================================================
    # STOP / TARGET
    # ========================================================

    stop_distance = max(
        atr_value * cfg.ATR_STOP_MULTIPLIER,
        close * cfg.MIN_STOP_PCT,
    )

    reward_distance = (
        stop_distance
        * cfg.REWARD_RISK_RATIO
    )

    if direction == "BUY":

        stop_loss = (
            close
            - stop_distance
        )

        take_profit = (
            close
            + reward_distance
        )

    else:

        stop_loss = (
            close
            + stop_distance
        )

        take_profit = (
            close
            - reward_distance
        )

    if stop_loss <= 0:
        return None

    if take_profit <= 0:
        return None

    return Signal(
        ticker=str(ticker),
        timeframe=str(timeframe),
        direction=direction,
        score=int(score),
        max_score=max_score,
        close=round(close, 4),
        stop_loss=round(
            stop_loss,
            4,
        ),
        take_profit=round(
            take_profit,
            4,
        ),
        reasons=reasons,
    )
