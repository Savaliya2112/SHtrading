from __future__ import annotations

import json
import os
import time
from pathlib import Path


def load_state(path: str):
    p = Path(path)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(path: str, state: dict):
    p = Path(path)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2), encoding="utf-8")
    tmp.replace(p)


def signal_key(signal):
    return f"{signal.ticker}|{signal.timeframe}|{signal.direction}"


def should_alert(state, signal, cooldown_minutes):
    key = signal_key(signal)
    now = time.time()
    previous = float(state.get(key, 0))
    return now - previous >= cooldown_minutes * 60


def mark_alerted(state, signal):
    state[signal_key(signal)] = time.time()
