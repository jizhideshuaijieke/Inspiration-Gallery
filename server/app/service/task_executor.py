from datetime import datetime, timezone
from threading import Semaphore, Thread

from app.config import settings
from app.db import SessionLocal
from app.models.generation_task import GenerationTask
from app.models.style import Style
from app.service.task_payload import build_task_payload
from app.service.style_transfer import run_style_transfer
from app.service.ws_manager import task_ws_manager


def _utcnow_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


_MAX_PARALLEL = max(settings.max_concurrency, 1)
_INFER_SEM = Semaphore(_MAX_PARALLEL)


def start_task_processing(task_id: int) -> None:
    Thread(target=_process_task, args=(task_id,), daemon=True).start()


def _process_task(task_id: int) -> None:
    with _INFER_SEM:
        db = SessionLocal()
        try:
            task = db.get(GenerationTask, task_id)
            if not task or task.status != "pending":
                return

            style = db.get(Style, task.style_id)
            if not style or not style.is_active:
                raise RuntimeError("风格不存在或未启用")

            task.status = "running"
            task.started_at = _utcnow_naive()
            task.error_msg = None
            db.commit()
            task_ws_manager.notify(task.id, build_task_payload(task, task_ws_manager.get_base_url(task.id)))

            run_style_transfer(task.id, task.input_image_url, style.code)

            task = db.get(GenerationTask, task_id)
            if not task:
                return
            task.status = "success"
            task.error_msg = None
            task.finished_at = _utcnow_naive()
            db.commit()
            task_ws_manager.notify(task.id, build_task_payload(task, task_ws_manager.get_base_url(task.id)))
        except Exception as exc:
            db.rollback()
            task = db.get(GenerationTask, task_id)
            if task:
                task.status = "failed"
                task.error_msg = str(exc)[:255]
                task.finished_at = _utcnow_naive()
                db.commit()
                task_ws_manager.notify(task.id, build_task_payload(task, task_ws_manager.get_base_url(task.id)))
        finally:
            db.close()
