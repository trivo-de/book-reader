"""Logic chính: gửi trang theo ngày lịch (Ngày D tháng M)."""
from __future__ import annotations

import logging
import os
import re
from datetime import datetime
from zoneinfo import ZoneInfo

from .config import BOOKS_DIR, READ_BOOK_FOLDER, SCHEDULE
from .gdrive import upload
from .pdf import find_page_for_date, to_images
from .state import load, save
from .zalo import send_message, send_photo

log = logging.getLogger(__name__)
TZ = ZoneInfo("Asia/Ho_Chi_Minh")

_DATE_ARG = re.compile(r"^(\d{1,2})[-/](\d{1,2})$")  # MM-DD hoặc DD-MM? dùng MM-DD


def _parse_date_arg(arg: str | None) -> tuple[int, int]:
    """Trả về (month, day). None/'today' → hôm nay (VN). '09-08' → tháng 9 ngày 8."""
    now = datetime.now(TZ)
    if not arg or arg.lower() in {"today", "now"}:
        return now.month, now.day
    m = _DATE_ARG.match(arg.strip())
    if not m:
        raise ValueError(f"Ngày không hợp lệ: {arg!r} (dùng MM-DD, ví dụ 09-08)")
    a, b = int(m.group(1)), int(m.group(2))
    # 09-08 → tháng 9 ngày 8; nếu a<=12 và b>12 thì a=month; nếu a>12 thì a=day b=month
    if a > 12:
        return b, a  # DD-MM kiểu 25-09
    if b > 12:
        return a, b  # MM-DD với day>12 không xảy ra; MM-YY?
    # cả hai <=12: mặc định MM-DD như user ví dụ 09-08
    return a, b


def run_send(date_arg: str | None = None, force: bool = False):
    """Gửi đúng 1 trang khớp ngày lịch (title 'Ngày D tháng M')."""
    gdrive_folder = os.environ.get("GDRIVE_FOLDER_ID", "") or READ_BOOK_FOLDER
    if not gdrive_folder:
        log.error("Thiếu GDRIVE_FOLDER_ID trong .env")
        return

    month, day = _parse_date_arg(date_arg)
    date_key = f"{month:02d}-{day:02d}"
    title = f"Ngày {day} tháng {month}"

    state = load()
    BOOKS_DIR.mkdir(parents=True, exist_ok=True)
    books = sorted(BOOKS_DIR.glob("*.pdf"))
    if not books:
        log.warning("Không có PDF trong books/")
        return

    pdf_path = next((b for b in books if b.name == state.get("current_book")), None) or books[0]
    state["current_book"] = pdf_path.name

    if not force and state.get("last_sent_date") == date_key:
        log.info(f"Đã gửi {title} rồi, bỏ qua (dùng force để gửi lại)")
        return

    page, _ = find_page_for_date(pdf_path, month, day)
    if not page:
        log.error(f"Không tìm thấy trang cho {title}")
        send_message(f"❌ Không tìm thấy trang: {title}")
        return

    log.info(f"Gửi {title} → PDF trang {page} ({pdf_path.name})")
    imgs = to_images(pdf_path, page, 1)
    if not imgs:
        log.error("Không tạo được ảnh từ PDF")
        return

    img = imgs[0]
    photo_url = upload(img, gdrive_folder)
    if not photo_url:
        log.error("Upload GDrive thất bại (thiếu credentials/token?)")
        img.unlink(missing_ok=True)
        return

    caption = f"📖 {pdf_path.stem} — {title} (trang {page})"
    if not send_photo(photo_url, caption):
        log.error("Gửi Zalo thất bại")
        img.unlink(missing_ok=True)
        return

    state["last_sent_date"] = date_key
    state["last_sent_page"] = page
    state["last_sent_title"] = title
    save(state)
    log.info(f"Đã gửi Zalo: {caption}")
    send_message(f"✅ Đã gửi {title}")
    try:
        img.unlink(missing_ok=True)
    except OSError:
        pass


def main():
    """Chạy scheduler — mỗi slot gửi trang của ngày hôm nay (nếu chưa gửi)."""
    from apscheduler.schedulers.blocking import BlockingScheduler
    from apscheduler.triggers.cron import CronTrigger

    sched = BlockingScheduler(timezone=TZ)
    for h, m in SCHEDULE:
        sched.add_job(run_send, CronTrigger(hour=h, minute=m, timezone=TZ), id=f"send_{h}_{m}")
    log.info("Lịch gửi trang theo ngày: 8:00, 11:45, 17:00 (Asia/Ho_Chi_Minh)")
    sched.start()
