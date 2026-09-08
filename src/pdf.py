"""PDF: render ảnh + map Ngày/tháng → số trang."""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from .config import DATA_DIR, OUTPUT_DIR

log = logging.getLogger(__name__)

DATE_MAP_FILE = DATA_DIR / "date_map.json"
# "Ngày 8 tháng 9" → (day=8, month=9)
_DATE_RE = re.compile(r"Ngày\s+(\d{1,2})\s+tháng\s+(\d{1,2})", re.IGNORECASE)


def _open(pdf_path: Path):
    import pypdfium2 as pdfium

    return pdfium.PdfDocument(str(pdf_path))


def to_images(pdf_path: Path, start_page: int, num_pages: int = 1) -> list[Path]:
    """PDF → PNG (1-based page). DPI ~200, autocontrast."""
    from PIL import ImageEnhance, ImageOps

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    doc = _open(pdf_path)
    paths: list[Path] = []
    try:
        last = min(start_page + num_pages - 1, len(doc))
        scale = 200 / 72
        for pg in range(start_page, last + 1):
            page = doc[pg - 1]
            img = page.render(scale=scale).to_pil()
            try:
                img = ImageOps.autocontrast(img, cutoff=2)
                img = ImageEnhance.Contrast(img).enhance(1.15)
                out = OUTPUT_DIR / f"page_{pg}.png"
                img.save(str(out))
                paths.append(out)
            finally:
                img.close()
    finally:
        doc.close()
    return paths


def build_date_map(pdf_path: Path, force: bool = False) -> dict[str, int]:
    """
    Map MM-DD → PDF page (1-based).
    Bỏ qua mục lục: chỉ lấy từ lần xuất hiện 'Ngày 1 tháng 1' trở đi.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    stamp = f"{pdf_path.name}:{pdf_path.stat().st_mtime_ns}"
    if DATE_MAP_FILE.exists() and not force:
        cached = json.loads(DATE_MAP_FILE.read_text(encoding="utf-8"))
        if cached.get("_source") == stamp and cached.get("pages"):
            return {k: v for k, v in cached["pages"].items()}

    doc = _open(pdf_path)
    pages: dict[str, int] = {}
    started = False
    try:
        for i in range(len(doc)):
            text = doc[i].get_textpage().get_text_bounded() or ""
            m = _DATE_RE.search(text)
            if not m:
                continue
            day, month = int(m.group(1)), int(m.group(2))
            key = f"{month:02d}-{day:02d}"
            if key == "01-01":
                started = True
            if not started:
                continue
            if key not in pages:
                pages[key] = i + 1
    finally:
        doc.close()

    DATE_MAP_FILE.write_text(
        json.dumps({"_source": stamp, "pages": pages}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    log.info(f"Đã map {len(pages)} ngày → trang từ {pdf_path.name}")
    return pages


def find_page_for_date(pdf_path: Path, month: int, day: int) -> tuple[int | None, str]:
    """Trả về (pdf_page, title) cho ngày lịch. title ví dụ 'Ngày 8 tháng 9'."""
    key = f"{month:02d}-{day:02d}"
    title = f"Ngày {day} tháng {month}"
    pages = build_date_map(pdf_path)
    return pages.get(key), title
