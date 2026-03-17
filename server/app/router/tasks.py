from fastapi import APIRouter, Depends, File, Request, UploadFile, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import SessionLocal, get_db
from app.models.generation_task import GenerationTask
from app.models.style import Style
from app.router.common import error, ok
from app.schemas.task import StyleTransferRequest
from app.service.auth_identity import resolve_user_from_auth_header, resolve_user_from_token
from app.service.media_store import (
    build_absolute_media_url,
    get_input_image_path,
    save_uploaded_input_image,
)
from app.service.task_payload import build_task_payload
from app.service.task_executor import start_task_processing
from app.service.ws_manager import task_ws_manager

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/upload-input")
def upload_input_image(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    user = resolve_user_from_auth_header(request.headers.get("Authorization"), db)
    if not user:
        return error(40101, "未登录或token无效", 401)

    try:
        relative_url = save_uploaded_input_image(file)
    except ValueError as exc:
        return error(40001, str(exc), 400)

    return ok({"input_image_url": build_absolute_media_url(request, relative_url)})


@router.post("/style-transfer")
def create_style_transfer(
    payload: StyleTransferRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    user = resolve_user_from_auth_header(request.headers.get("Authorization"), db)
    if not user:
        return error(40101, "未登录或token无效", 401)

    style = db.scalar(select(Style).where(Style.id == payload.style_id, Style.is_active.is_(True)))
    if not style:
        return error(40401, "风格不存在", 404)

    try:
        get_input_image_path(payload.input_image_url)
    except ValueError as exc:
        return error(40001, str(exc), 400)

    task = GenerationTask(
        user_id=user.id,
        style_id=payload.style_id,
        input_image_url=payload.input_image_url,
        status="pending",
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    start_task_processing(task.id)
    return ok({"task_id": task.id, "status": task.status, "preview_url": None})


@router.get("/{task_id}")
def get_task(task_id: int, request: Request, db: Session = Depends(get_db)):
    user = resolve_user_from_auth_header(request.headers.get("Authorization"), db)
    if not user:
        return error(40101, "未登录或token无效", 401)

    task = db.get(GenerationTask, task_id)
    if not task:
        return error(40401, "任务不存在", 404)

    if task.user_id != user.id and user.role != "admin":
        return error(40301, "无权限", 403)

    return ok(build_task_payload(task, str(request.base_url).rstrip("/")))


@router.websocket("/ws/{task_id}")
async def watch_task(task_id: int, websocket: WebSocket):
    token = websocket.query_params.get("token")
    db = SessionLocal()

    try:
        user = resolve_user_from_token(token, db)
        if not user:
            await websocket.close(code=1008, reason="未登录或token无效")
            return

        task = db.get(GenerationTask, task_id)
        if not task:
            await websocket.close(code=1008, reason="任务不存在")
            return

        if task.user_id != user.id and user.role != "admin":
            await websocket.close(code=1008, reason="无权限")
            return

        await task_ws_manager.connect(task_id, websocket)
        await websocket.send_json(build_task_payload(task, task_ws_manager.get_base_url(task_id)))
        db.close()

        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await task_ws_manager.disconnect(task_id, websocket)
        db.close()
