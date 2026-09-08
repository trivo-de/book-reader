"""Cấu hình paths và constants."""
import os
from pathlib import Path

ROOT = Path(os.environ.get("DATA_DIR", Path(__file__).resolve().parent.parent))
BOOKS_DIR = ROOT / "books"
OUTPUT_DIR = ROOT / "output"
DATA_DIR = ROOT / "data"  # credentials.json, token.json, state.json
STATE_FILE = DATA_DIR / "state.json"

# Lịch gửi trong ngày (giờ, phút) — Asia/Ho_Chi_Minh
SCHEDULE = [
    (8, 0),
    (11, 45),
    (17, 0),
]

# Bắt buộc set qua env / .env — không hardcode secret
READ_BOOK_FOLDER = os.environ.get("GDRIVE_FOLDER_ID", "")
