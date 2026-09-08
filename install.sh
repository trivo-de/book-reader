#!/usr/bin/env bash
# Cài nhanh Book Reader bằng Docker Compose.
set -euo pipefail

cd "$(dirname "$0")"

red()  { printf '\033[31m%s\033[0m\n' "$*"; }
ok()   { printf '\033[32m%s\033[0m\n' "$*"; }
info() { printf '\033[36m%s\033[0m\n' "$*"; }

need() {
  if ! command -v "$1" >/dev/null 2>&1; then
    red "Thiếu lệnh: $1"
    exit 1
  fi
}

need docker
if ! docker compose version >/dev/null 2>&1; then
  red "Cần Docker Compose (docker compose)"
  exit 1
fi

mkdir -p books data output

if [[ ! -f .env ]]; then
  cp .env.example .env
  red "Đã tạo .env từ .env.example — hãy điền ZALO_* và GDRIVE_FOLDER_ID rồi chạy lại:"
  red "  nano .env && ./install.sh"
  exit 1
fi

if [[ ! -f data/credentials.json ]]; then
  red "Thiếu data/credentials.json"
  info "1) Copy mẫu: cp data/credentials.example.json data/credentials.json"
  info "2) Dán OAuth Desktop credentials từ Google Cloud"
  info "3) Chạy trên máy có trình duyệt: python scripts/generate_token.py"
  info "   (hoặc: docker compose run --rm book-reader python scripts/generate_token.py"
  info "    — chỉ khi đã map port/browser được)"
  exit 1
fi

if [[ ! -f data/token.json ]]; then
  red "Thiếu data/token.json — tạo OAuth token trước:"
  info "  pip install -r requirements.txt"
  info "  python scripts/generate_token.py"
  exit 1
fi

if ! ls books/*.pdf >/dev/null 2>&1; then
  red "Chưa có PDF trong books/ — hãy copy file .pdf vào đó rồi chạy lại."
  exit 1
fi

info ">>> Build & start..."
docker compose up -d --build

ok "Đã chạy. Xem log:"
info "  docker compose logs -f"
info "Gửi thử trang hôm nay:"
info "  docker compose exec book-reader python app.py today force"
info "Dừng:"
info "  docker compose down"
