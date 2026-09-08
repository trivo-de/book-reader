# Book Reader

Bot Python gửi **đúng 1 trang sách mỗi ngày** lên Zalo, khớp title lịch trong PDF.

Ví dụ: hôm nay `09-08` → tìm trang có title **Ngày 8 tháng 9** → render PNG → upload Google Drive → gửi Zalo.

```
PDF (title "Ngày D tháng M")
        │
        ▼
   map MM-DD → trang
        │
        ▼
  render PNG (pypdfium2)
        │
        ▼
  upload Google Drive (public URL)
        │
        ▼
     gửi Zalo
```

## Tính năng

- Map tự động title `Ngày D tháng M` → số trang PDF (cache `data/date_map.json`)
- Gửi theo ngày lịch (`today`, `09-08`, …)
- Scheduler 3 lần/ngày (8:00, 11:45, 17:00 — `Asia/Ho_Chi_Minh`), không gửi trùng cùng ngày
- Không cần poppler (dùng `pypdfium2`)

## Cấu trúc

```
book-reader/
├── app.py
├── Dockerfile
├── docker-compose.yml
├── install.sh             # cài 1 lệnh (cần Docker)
├── requirements.txt
├── .env.example
├── .gitignore
├── books/                 # Đặt PDF của bạn vào đây (không commit)
├── data/
│   ├── credentials.example.json
│   ├── credentials.json   # gitignored
│   └── token.json         # gitignored
├── output/
├── scripts/
│   └── generate_token.py
└── src/
    ├── app.py
    ├── config.py
    ├── pdf.py
    ├── gdrive.py
    ├── zalo.py
    └── state.py
```

## Cách nhanh nhất (Docker)

Cần sẵn Docker + Docker Compose.

```bash
git clone https://github.com/trivo-de/book-reader.git
cd book-reader

cp .env.example .env
# sửa .env: ZALO_URL, ZALO_PHOTO_URL, ZALO_CHAT_ID, GDRIVE_FOLDER_ID

cp data/credentials.example.json data/credentials.json
# dán OAuth Desktop credentials từ Google Cloud vào file trên

# Tạo token lần đầu (máy có trình duyệt + Python):
pip install -r requirements.txt
python scripts/generate_token.py

# Thêm PDF
cp /path/to/book.pdf books/

chmod +x install.sh
./install.sh
```

Lệnh hữu ích:

```bash
docker compose logs -f
docker compose exec book-reader python app.py today force
docker compose down
```

## Cài bằng Python (không Docker)

```bash
git clone https://github.com/trivo-de/book-reader.git
cd book-reader
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 1. Cấu hình `.env`

```bash
cp .env.example .env
```

Điền:

| Biến | Mô tả |
|------|--------|
| `ZALO_URL` | Endpoint `sendMessage` của bot |
| `ZALO_PHOTO_URL` | Endpoint `sendPhoto` của bot |
| `ZALO_CHAT_ID` | ID chat/nhóm nhận tin |
| `GDRIVE_FOLDER_ID` | ID folder Google Drive chứa ảnh trang |

### 2. Google Drive OAuth

1. Tạo OAuth Client (Desktop) trên Google Cloud Console, bật Drive API
2. Tải `credentials.json` → đặt vào `data/credentials.json`  
   (xem mẫu `data/credentials.example.json`)
3. Chạy:

```bash
python scripts/generate_token.py
```

Trình duyệt mở → đăng nhập → tạo `data/token.json`.

### 3. Thêm sách

```bash
# Đặt file PDF vào books/
books/Your-Book.pdf
```

> PDF bản quyền **không** được đưa lên repo. Mỗi người tự thêm sách của mình.

## Chạy (Python)

```bash
python app.py today        # gửi trang hôm nay
python app.py 09-08        # gửi Ngày 8 tháng 9
python app.py 03-16 force  # gửi lại Ngày 16 tháng 3
python app.py              # chạy scheduler
```

## Bảo mật

Các file sau **không** được commit (xem `.gitignore`):

- `.env`
- `data/credentials.json`
- `data/token.json`
- `data/state.json`
- `data/date_map.json`
- `books/*.pdf`
- `output/`

Không hardcode token / chat ID / folder ID trong code.

## License

MIT — tự chịu trách nhiệm khi dùng với nội dung sách của bạn.
