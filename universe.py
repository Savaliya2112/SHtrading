from __future__ import annotations

import pandas as pd


# ============================================================
# NASDAQ-100 FALLBACK
# ============================================================

NASDAQ100_FALLBACK = [
    "ADBE", "AMD", "ABNB", "ALNY", "AMAT", "APP", "ARM", "ASML",
    "AVGO", "AXON", "BKNG", "BKR", "CCEP", "CDNS", "CEG", "CHTR",
    "CMCSA", "COST", "CPRT", "CRWD", "CSCO", "CSGP", "CSX", "CTAS",
    "CTSH", "DASH", "DDOG", "DXCM", "EA", "EXC", "FANG", "FAST",
    "FER", "FTNT", "GEHC", "GILD", "GOOG", "GOOGL", "HON", "IDXX",
    "INSM", "INTC", "INTU", "ISRG", "KDP", "KHC", "KLAC", "LIN",
    "LRCX", "MAR", "MCHP", "MDB", "MDLZ", "MELI", "META", "MNST",
    "MPWR", "MRVL", "MSFT", "MSTR", "MU", "NFLX", "NVDA", "NXPI",
    "ODFL", "ON", "ORLY", "PANW", "PAYX", "PCAR", "PDD", "PEP",
    "PLTR", "PYPL", "QCOM", "REGN", "ROP", "ROST", "SBUX", "SHOP",
    "SNPS", "TEAM", "TMUS", "TRGP", "TSLA", "TTWO", "TXN", "VRSK",
    "VRTX", "WBD", "WDAY", "WDC", "WMT", "XEL", "ZS"
]


# ============================================================
# JAPAN
# ============================================================

JAPAN_INDEXES = [
    "^N225",   # Nikkei 225
    "^TOPX",   # TOPIX
]


# ============================================================
# INDEX FUNDS
# ============================================================

INDEX_FUNDS = [
    "QQQ",
    "QQQM",
    "VOO",
    "VTI",
    "SPY",
    "DIA",
    "IWM",
    "EFA",
    "EEM",
]


# ============================================================
# DOWNLOAD CURRENT NASDAQ-100 CONSTITUENTS
# ============================================================

def get_nasdaq100() -> list[str]:
    """
    Try to obtain the current Nasdaq-100 constituents.

    If the online table cannot be downloaded, use the
    built-in fallback list so scanning can continue.
    """

    try:
        tables = pd.read_html(
            "https://en.wikipedia.org/wiki/Nasdaq-100"
        )

        for table in tables:

            columns = {
                str(column).strip().lower(): column
                for column in table.columns
            }

            ticker_column = None

            for name, column in columns.items():

                if (
                    "ticker" in name
                    or "symbol" in name
                ):
                    ticker_column = column
                    break

            if ticker_column is None:
                continue

            values = []

            for value in table[ticker_column].dropna():

                symbol = (
                    str(value)
                    .strip()
                    .upper()
                    .replace(".", "-")
                )

                if symbol:
                    values.append(symbol)

            # Nasdaq-100 should contain roughly 100 constituents.
            # Reject an obviously incomplete table.
            if len(set(values)) >= 80:

                return sorted(
                    set(values)
                )

    except Exception as exc:

        print(
            "[UNIVERSE] Could not refresh "
            f"Nasdaq-100 list: {exc}"
        )

    print(
        "[UNIVERSE] Using Nasdaq-100 "
        "fallback list."
    )

    return sorted(
        set(NASDAQ100_FALLBACK)
    )


# ============================================================
# COMPLETE MONITORING UNIVERSE
# ============================================================

def all_symbols() -> list[str]:
    """
    Return the complete monitoring universe.

    Includes:
      - Nasdaq-100 constituents
      - Nikkei 225
      - TOPIX
      - Selected major index ETFs
    """

    symbols:
