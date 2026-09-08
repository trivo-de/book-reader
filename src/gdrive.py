"""Upload ảnh lên Google Drive."""
from pathlib import Path

from .config import DATA_DIR, READ_BOOK_FOLDER


def upload(local_path: Path, folder_id: str | None = None) -> str | None:
    """Upload file, trả về URL public."""
    folder_id = folder_id or READ_BOOK_FOLDER
    creds_path = DATA_DIR / "credentials.json"
    token_path = DATA_DIR / "token.json"

    if not creds_path.exists():
        return None

    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    SCOPES = ["https://www.googleapis.com/auth/drive.file"]
    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if not creds:
        flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
        creds = flow.run_local_server(port=0)
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(token_path, "w") as f:
            f.write(creds.to_json())

    service = build("drive", "v3", credentials=creds)
    meta = {"name": local_path.name, "parents": [folder_id]}
    media = MediaFileUpload(str(local_path), mimetype="image/png")
    f = service.files().create(body=meta, media_body=media, fields="id").execute()
    service.permissions().create(fileId=f["id"], body={"type": "anyone", "role": "reader"}).execute()
    return f"https://drive.google.com/uc?export=view&id={f['id']}"
