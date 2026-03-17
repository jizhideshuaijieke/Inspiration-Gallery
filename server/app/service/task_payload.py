from app.models.generation_task import GenerationTask
from app.service.media_store import get_generated_image_path, get_generated_relative_path


def _build_absolute_url(base_url: str | None, relative_path: str) -> str | None:
    if not base_url:
        return None

    base = str(base_url).rstrip("/")
    rel = relative_path if relative_path.startswith("/") else f"/{relative_path}"
    return f"{base}{rel}"


def build_task_payload(task: GenerationTask, base_url: str | None = None) -> dict:
    preview_url = None
    if task.status == "success":
        generated = get_generated_image_path(task.id)
        if generated.exists():
            preview_url = _build_absolute_url(base_url, get_generated_relative_path(task.id))

    return {
        "id": task.id,
        "status": task.status,
        "error_msg": task.error_msg,
        "output_artwork_id": task.output_artwork_id,
        "preview_url": preview_url,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "started_at": task.started_at.isoformat() if task.started_at else None,
        "finished_at": task.finished_at.isoformat() if task.finished_at else None,
    }
