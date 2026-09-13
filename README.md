# SHtrading — alert-only market scanner

## What it does

- Scans the Nasdaq-100 universe.
- Scans Japan indexes (`^N225`, `^TOPX`).
- Includes major index ETFs such as QQQ/QQQM/SPY/DIA/IWM.
- Uses daily and 1-hour technical data.
- Sends Telegram alerts.
- Supports `ASK NVDA`, `ASK NEWS NVDA`, and `ASK MARKET`.
- Does not place broker orders.

## GitHub Actions secrets

Add:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

## Important

GitHub Actions is appropriate for scheduled scans, but it is not an always-on Telegram polling server. For instant ASK replies, run:

`python bot.py server`

on an always-on machine/server.

## Run locally

`pip install -r requirements.txt`

`pytest -q`

`python bot.py scan`

`python bot.py news`

`python bot.py server`
