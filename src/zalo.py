"""Gửi ảnh và text qua Zalo (API trực tiếp hoặc adapter)."""
from __future__ import annotations

import os
from pathlib import Path

import requests

_ROOT = Path(__file__).resolve().parent.parent


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


# Ưu tiên .env trong thư mục app; fallback .env ở thư mục cha (monorepo)
_load_dotenv(_ROOT / ".env")
_load_dotenv(_ROOT.parent / ".env")


def _chat_id(chat_id: str | None = None) -> str:
    return chat_id or os.environ.get("ZALO_CHAT_ID", "")


def _photo_api() -> str | None:
    return (os.environ.get("ZALO_PHOTO_URL") or "").strip() or None


def _message_api() -> str | None:
    return (os.environ.get("ZALO_URL") or "").strip() or None


def _adapter_url() -> str:
    return os.environ.get("ZALO_ADAPTER_URL", "http://localhost:8080").rstrip("/")


def send_message(text: str, chat_id: str | None = None) -> bool:
    """Gửi text qua Zalo API hoặc adapter."""
    chat_id = _chat_id(chat_id)
    if not chat_id:
        return False
    api = _message_api()
    try:
        if api:
            r = requests.post(api, json={"chat_id": chat_id, "text": text}, timeout=10)
            return r.ok
        r = requests.post(
            _adapter_url() + "/send-message",
            json={"chat_id": chat_id, "text": text},
            timeout=10,
        )
        return r.ok
    except Exception:
        return False


def send_photo(photo_url: str, caption: str, chat_id: str | None = None) -> bool:
    """Gửi ảnh qua Zalo API hoặc adapter."""
    chat_id = _chat_id(chat_id)
    if not chat_id:
        return False
    api = _photo_api()
    try:
        if api:
            r = requests.post(
                api,
                json={"chat_id": chat_id, "photo": photo_url, "caption": caption[:2000]},
                timeout=30,
            )
            return r.ok
        r = requests.post(
            _adapter_url() + "/send-photo",
            json={"chat_id": chat_id, "photo": photo_url, "caption": caption},
            timeout=30,
        )
        return r.ok
    except Exception:
        return False
