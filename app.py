#!/usr/bin/env python3
"""Book Reader - Entry point. PDF → ảnh → GDrive → Zalo (theo ngày lịch)."""
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)

from src.app import main, run_send

if __name__ == "__main__":
    # python app.py              → scheduler
    # python app.py today        → gửi hôm nay
    # python app.py 09-08        → gửi Ngày 8 tháng 9
    # python app.py 09-08 force  → gửi lại dù đã gửi
    if len(sys.argv) > 1:
        args = [a for a in sys.argv[1:] if a.lower() != "force"]
        force = any(a.lower() == "force" for a in sys.argv[1:])
        run_send(args[0] if args else "today", force=force)
    else:
        main()
