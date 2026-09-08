"""Quản lý state đọc sách."""
import json
from .config import STATE_FILE

DEFAULT = {
    "current_book": "",
    "last_sent_date": "",
    "last_sent_page": 0,
    "last_sent_title": "",
}


def load():
    if STATE_FILE.exists():
        with open(STATE_FILE, encoding="utf-8") as f:
            data = json.load(f)
        # merge defaults for old state files
        return {**DEFAULT, **data}
    return DEFAULT.copy()


def save(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
