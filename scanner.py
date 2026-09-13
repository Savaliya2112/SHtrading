from __future__ import annotations

from typing import Optional

import config
from data_provider import download_history
from indicators import add_indicators
from strategy import generate_signal


def get_symbol_data(
    symbol: str,
    period: Optional[str] = None,
):
    """
    Download market data and calculate indicators
    for one symbol.
    """

    try:
        df = download_history(
            symbol,
            period or config.HISTORY_PERIOD,
            "1d",
        )

        if df is None or df.empty:
            return None

        indicators = add_indicators(df)

        if indicators is None or indicators.empty:
            return None

        return indicators

    except Exception as exc:
        print(
            f"[DATA ERROR] {symbol}: {exc}"
        )
        return None


def scan_symbol(
    symbol: str,
    period: Optional[str] = None,
):
    """
    Analyse the latest available data for one symbol.

    Returns a Signal when the configured conditions
    are satisfied, otherwise None.
    """

    symbol = str(symbol).strip().upper()

    if not symbol:
        return None

    data = get_symbol_data(
        symbol,
        period,
    )

    if data is None:
        return None

    try:
        return generate_signal(
            symbol,
            data,
            config.MIN_SCORE,
        )

    except Exception as exc:
        print(
            f"[SIGNAL ERROR] {symbol}: {exc}"
        )
        return None


def backward_scan(
    symbol: str,
    lookback_days: Optional[int] = None,
):
    """
    Analyse previous historical candles.

    This is useful for checking whether the strategy
    would have produced qualifying signals in the past.

    Returns a list of historical signals.
    """

    symbol = str(symbol).strip().upper()

    if not symbol:
        return []

    data = get_symbol_data(symbol)

    if data is None or data.empty:
        return []

    lookback = min(
        int(
            lookback_days
            if lookback_days is not None
            else config.LOOKBACK_DAYS
        ),
        len(data),
    )

    if lookback <= 0:
        return []

    start = max(
        0,
        len(data) - lookback,
    )

    results = []

    for index in range(start, len(data)):
        historical_data = data.iloc[: index + 1]

        # We need enough candles for the indicators.
        if len(historical_data) < 50:
            continue

        try:
            signal = generate_signal(
                symbol,
                historical_data,
                config.MIN_SCORE,
            )

            if signal is not None:
                results.append(
                    {
                        "date": str(
                            data.index[index]
                        ),
                        "signal": signal,
                    }
                )

        except Exception as exc:
            print(
                f"[BACKWARD ERROR] "
                f"{symbol} {index}: {exc}"
            )

    return results


# Keep the old function name available so
# existing code/tests do not break.
def backward_scan_symbol(
    symbol: str,
    lookback_days: Optional[int] = None,
):
    return backward_scan(
        symbol,
        lookback_days,
    )


def scan_universe(symbols):
    """
    Scan a supplied list of symbols.

    Returns:
        [
            (symbol, signal_or_none),
            ...
        ]
    """

    results = []

    for symbol in symbols:
        symbol = str(symbol).strip().upper()

        if not symbol:
            continue

        try:
            signal = scan_symbol(symbol)
            results.append(
                (
                    symbol,
                    signal,
                )
            )

        except Exception as exc:
            print(
                f"[SCAN ERROR] {symbol}: {exc}"
            )
            results.append(
                (
                    symbol,
                    None,
                )
            )

    return results


def scan_all():
    """
    Scan the complete configured market universe.
    """

    from universe import all_symbols

    symbols = all_symbols()

    return scan_universe(symbols)
