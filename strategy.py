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
    Generate a BUY or SELL signal from technical indicators.

    This function does NOT place trades.
    It only creates a research/paper-trading signal.
    """

    # Calculate indicators
    enriched = compute_all_indicators(
        df,
        cfg
    )

    # Remove rows where indicators are not ready
    enriched = enriched.dropna()

    if enriched.empty:
        return None

    row = enriched.iloc[-1]

    buy_score = 0
    sell_score = 0

    buy_reasons = []
    sell_reasons = []

    # --------------------------------------------------------
    # 1. EMA TREND
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
    # 2. SMA TREND
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
    # 3. MACD MOMENTUM
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
    # 4. RSI
    # --------------------------------------------------------

    rsi_value = float(
        row["rsi"]
    )

    # Avoid buying heavily overbought conditions
    if 50 <= rsi_value <= 68:
        buy_score += 1
        buy_reasons.append(
            f"RSI bullish ({rsi_value:.1f})"
        )

    # Avoid selling heavily oversold conditions
    elif 32 <= rsi_value < 50:
        sell_score += 1
        sell_reasons.append(
            f"RSI bearish ({rsi_value:.1f})"
        )

    # --------------------------------------------------------
    # 5. BOLLINGER MIDPOINT
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
    # 6. VOLUME CONFIRMATION
    # --------------------------------------------------------

    volume_ratio_value = float(
        row["vol_ratio"]
    )

    if (
        volume_ratio_value
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

    # Six maximum scoring categories
    max_score = 6

    # --------------------------------------------------------
    # SELECT SIGNAL
    # --------------------------------------------------------

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
        # No sufficiently strong setup
        return None

    # --------------------------------------------------------
    # PRICE / STOP / TARGET
    # --------------------------------------------------------

    close = float(
        row["Close"]
    )

    atr_value = float(
        row["atr"]
    )

    if close <= 0 or atr_value <= 0:
        return None

    # ATR based stop distance
    stop_distance = max(
        atr_value
        * cfg.ATR_STOP_MULTIPLIER,

        close
        * cfg.MIN_STOP_PCT
    )

    # Risk/reward target
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

    # Safety check
    if stop_loss <= 0:
        return None

    if take_profit <= 0:
        return None

    # --------------------------------------------------------
    # RETURN SIGNAL
    # --------------------------------------------------------

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
