# SHtrading

Alert-only market scanner. It does **not** place broker orders.

Features:
- Nasdaq-100 universe with live Wikipedia refresh and safe fallback
- Nikkei 225 and TOPIX
- QQQ, QQQM, VOO, VTI, SPY, DIA, IWM, EFA, EEM
- Technical signals using SMA/EMA/RSI/MACD/ATR/volume
- Telegram notifications
- `python bot.py ask NVDA`
- `python bot.py ask news NVDA`

## Setup
1. Install `requirements.txt`.
2. Set Telegram environment variables.
3. Run `python bot.py`.
4. For a question: `python bot.py ask NVDA`.
5. For news: `python bot.py ask news NVDA`.

No live order execution is included.
