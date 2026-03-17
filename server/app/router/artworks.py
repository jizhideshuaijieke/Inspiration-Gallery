from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.artwork import Artwork
from app.models.generation_task import GenerationTask
from app.models.style import Style
from app.models.user import User
from app.router.common import error, ok
from app.schemas.artwork import CreateArtworkRequest, UpdateArtworkRequest
from app.service.auth_identity import resolve_user_from_auth_header
from app.service.media_store import (
    build_absolute_media_url,
    get_generated_image_path,
    get_generated_relative_path,
)

router = APIRouter(prefix="/artworks", tags=["artworks"])


@router.post("")
def create_artwork(
    payload: CreateArtworkRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    user = resolve_user_from_auth_header(request.headers.get("Authorization"), db)
    if not user:
        return error(40101, "未登录或token无效", 401)

    task = db.get(GenerationTask, payload.task_id)
    if not task:
        return error(40401, "任务不存在", 404)

    if task.user_id != user.id and user.role != "admin":
        return error(40301, "无权限", 403)

    if task.status != "success":
        return error(42201, "任务未完成，无法保存作品", 422)

    if task.output_artwork_id:
        return error(42201, "该任务已生成作品", 422)

    generated_image = get_generated_image_path(task.id)
    if not generated_image.exists():
        return error(42201, "生成图片不存在，请重新提交任务", 422)

    title = (payload.title or "").strip() or "未命名作品"
    artwork = Artwork(
        author_id=user.id,
        style_id=task.style_id,
        title=title,
        source_image_url=task.input_image_url,
        result_image_url=build_absolute_media_url(request, get_generated_relative_path(task.id)),
        visibility="private",
    )
    db.add(artwork)
    db.flush()

    task.output_artwork_id = artwork.id
    db.commit()
    db.refresh(artwork)

    return ok(
        {
            "artwork_id": artwork.id,
            "visibility": artwork.visibility,
            "created_at": artwork.created_at.isoformat() if artwork.created_at else None,
        }
    )


@router.get("/{artwork_id}")
def get_artwork(artwork_id: int, request: Request, db: Session = Depends(get_db)):
    user = resolve_user_from_auth_header(request.headers.get("Authorization"), db)
    artwork = db.get(Artwork, artwork_id)
    if not artwork:
        return error(40401, "作品不存在", 404)

    if artwork.visibility in {"private", "hidden"}:
        if not user or (user.id != artwork.author_id and user.role != "admin"):
            return error(42201, "作品不可见", 422)

    style = db.get(Style, artwork.style_id)
    author = db.get(User, artwork.author_id)

    return ok(
        {
            "id": artwork.id,
            "title": artwork.title,
            "source_image_url": artwork.source_image_url,
            "result_image_url": artwork.result_image_url,
            "visibility": artwork.visibility,
            "style": {
                "id": style.id if style else None,
                "code": style.code if style else None,
                "name": style.name if style else None,
            },
            "author": {
                "id": author.id if author else None,
                "username": author.username if author else None,
                "avatar_url": author.avatar_url if author else None,
            },
            "like_count": artwork.like_count,
            "comment_count": artwork.comment_count,
            "download_count": artwork.download_count,
            "created_at": artwork.created_at.isoformat() if artwork.created_at else None,
        }
    )


@router.patch("/{artwork_id}")
def update_artwork(
    artwork_id: int,
    payload: UpdateArtworkRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    user = resolve_user_from_auth_header(request.headers.get("Authorization"), db)
    if not user:
        return error(40101, "未登录或token无效", 401)

    artwork = db.get(Artwork, artwork_id)
    if not artwork:
        return error(40401, "作品不存在", 404)

    if artwork.author_id != user.id and user.role != "admin":
        return error(40301, "无权限", 403)

    if payload.title is None and payload.visibility is None:
        return error(40001, "至少提供一个可更新字段", 400)

    if payload.title is not None:
        title = payload.title.strip()
        if not title:
            return error(40001, "标题不能为空", 400)
        artwork.title = title

    if payload.visibility is not None:
        if artwork.visibility == "hidden" and user.role != "admin":
            return error(42201, "已下架作品不能自行修改可见性", 422)
        artwork.visibility = payload.visibility
        if payload.visibility == "hall":
            artwork.hall_published_at = datetime.now(timezone.utc).replace(tzinfo=None)
        elif artwork.hall_published_at is not None:
            artwork.hall_published_at = None

    db.commit()
    db.refresh(artwork)

    return ok(
        {
            "id": artwork.id,
            "title": artwork.title,
            "visibility": artwork.visibility,
            "updated_at": artwork.updated_at.isoformat() if artwork.updated_at else None,
        }
    )


@router.delete("/{artwork_id}")
def delete_artwork(artwork_id: int, request: Request, db: Session = Depends(get_db)):
    user = resolve_user_from_auth_header(request.headers.get("Authorization"), db)
    if not user:
        return error(40101, "未登录或token无效", 401)

    artwork = db.get(Artwork, artwork_id)
    if not artwork:
        return error(40401, "作品不存在", 404)

    if artwork.author_id != user.id and user.role != "admin":
        return error(40301, "无权限", 403)

    db.delete(artwork)
    db.commit()
    return ok({"id": artwork_id, "deleted": True})
