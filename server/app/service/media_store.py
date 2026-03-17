from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4

from fastapi import Request, UploadFile

# Project root: .../Graduation Project
PROJECT_ROOT = Path(__file__).resolve().parents[3]
MEDIA_ROOT = PROJECT_ROOT / "server" / "media"
UPLOADS_DIR = MEDIA_ROOT / "uploads"
GENERATED_DIR = MEDIA_ROOT / "generated"

ALLOWED_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def ensure_media_dirs() -> None:
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)


def _normalize_media_path(url_or_path: str) -> str:
    parsed = urlparse(url_or_path)
    path = parsed.path if parsed.scheme else url_or_path
    return path.split("?", 1)[0]


def build_absolute_media_url(request: Request, relative_path: str) -> str:
    base = str(request.base_url).rstrip("/")
    rel = relative_path if relative_path.startswith("/") else f"/{relative_path}"
    return f"{base}{rel}"


def save_uploaded_image(file: UploadFile) -> str:
    ensure_media_dirs()
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise ValueError("仅支持 jpg/jpeg/png/webp/bmp 图片格式")

    filename = f"{uuid4().hex}{suffix}"
    dest = UPLOADS_DIR / filename
    file.file.seek(0)
    with dest.open("wb") as f:
        f.write(file.file.read())
    return f"/media/uploads/{filename}"


def save_uploaded_input_image(file: UploadFile) -> str:
    return save_uploaded_image(file)


def get_input_image_path(input_image_url: str) -> Path:
    path = _normalize_media_path(input_image_url)
    if not path.startswith("/media/uploads/"):
        raise ValueError("input_image_url 必须是 /media/uploads/ 下的图片地址")
    filename = Path(path).name
    target = UPLOADS_DIR / filename
    if not target.exists():
        raise ValueError("输入图片不存在或已失效")
    return target


def get_generated_relative_path(task_id: int) -> str:
    return f"/media/generated/task-{task_id}.png"


def get_generated_image_path(task_id: int) -> Path:
    ensure_media_dirs()
    return GENERATED_DIR / f"task-{task_id}.png"
