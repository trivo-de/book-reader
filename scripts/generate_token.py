#!/usr/bin/env python3
"""Chạy trên máy có trình duyệt để tạo token.json (OAuth GDrive)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CREDS = DATA / "credentials.json"
TOKEN = DATA / "token.json"
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

def main():
    DATA.mkdir(parents=True, exist_ok=True)
    if not CREDS.exists():
        print(f"Thiếu {CREDS}")
        sys.exit(1)
    from google_auth_oauthlib.flow import InstalledAppFlow
    flow = InstalledAppFlow.from_client_secrets_file(str(CREDS), SCOPES)
    creds = flow.run_local_server(port=0)
    with open(TOKEN, "w") as f:
        f.write(creds.to_json())
    print(f"Đã lưu {TOKEN}")

if __name__ == "__main__":
    main()
