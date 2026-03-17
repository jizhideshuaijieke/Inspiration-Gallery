from fastapi import APIRouter, Body, Depends, Query, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.admin_log import AdminLog
from app.models.artwork import Artwork
from app.models.comment import Comment
from app.models.follow import Follow
from app.models.style import Style
from app.models.user import User
from app.router.common import error, ok
from app.schemas.admin import AdminDeleteCommentRequest, AdminHideArtworkRequest
from app.service.artwork_ws_manager import artwork_ws_manager
from app.service.auth_identity import resolve_user_from_auth_header
from app.service.notice_ws_manager import notice_ws_manager

router = APIRouter(prefix="/admin", tags=["admin"])


def _require_admin(request: Request, db: Session):
    user = resolve_user_from_auth_header(request.headers.get("Authorization"), db)
    if not user:
        return None, error(40101, "未登录或token无效", 401)
    if user.role != "admin":
        return None, error(40301, "无权限", 403)
    return user, None


def _write_admin_log(
    db: Session,
    admin_id: int,
    target_type: str,
    target_id: int,
    action: str,
    reason: str | None,
):
    db.add(
        AdminLog(
            admin_id=admin_id,
            target_type=target_type,
            target_id=target_id,
            action=action,
            reason=reason,
        )
    )


@router.get("/users")
def get_admin_users(
    request: Request,
    page: int = Query(default=1),
    size: int = Query(default=20),
    keyword: str | None = Query(default=None),
    status: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    _, err = _require_admin(request, db)
    if err:
        return err

    if page < 1 or size < 1 or size > 50:
        return error(40001, "分页参数不合法", 400)

    query = select(User).where(User.role != "admin")
    if keyword:
        query = query.where(User.username.like(f"%{keyword.strip()}%"))
    if status:
        query = query.where(User.status == status)

    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    rows = db.scalars(
        query.order_by(User.created_at.desc(), User.id.desc())
        .offset((page - 1) * size)
        .limit(size)
    ).all()

    items = []
    for row in rows:
        followers_count = db.scalar(
            select(func.count()).select_from(Follow).where(Follow.followee_id == row.id)
        ) or 0
        following_count = db.scalar(
            select(func.count()).select_from(Follow).where(Follow.follower_id == row.id)
        ) or 0
        artworks_count = db.scalar(
            select(func.count()).select_from(Artwork).where(Artwork.author_id == row.id)
        ) or 0
        items.append(
            {
                "id": row.id,
                "account_code": row.account_code,
                "username": row.username,
                "role": row.role,
                "status": row.status,
                "avatar_url": row.avatar_url,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "updated_at": row.updated_at.isoformat() if row.updated_at else None,
                "followers_count": followers_count,
                "following_count": following_count,
                "artworks_count": artworks_count,
            }
        )

    return ok(
        {
            "list": items,
            "page": page,
            "size": size,
            "total": total,
            "has_more": page * size < total,
        }
    )


@router.patch("/users/{user_id}/block")
def block_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    admin, err = _require_admin(request, db)
    if err:
        return err

    user = db.get(User, user_id)
    if not user:
        return error(40401, "用户不存在", 404)

    if user.role == "admin":
        return error(42201, "管理员账号不可封禁", 422)

    if user.status == "blocked":
        return error(42201, "用户已被封禁", 422)

    user.status = "blocked"

    _write_admin_log(
        db,
        admin_id=admin.id,
        target_type="user",
        target_id=user.id,
        action="block_user",
        reason=None,
    )

    db.commit()
    db.refresh(user)
    notice_ws_manager.notify_refresh(user.id, "block_user")

    return ok(
        {
            "id": user.id,
            "status": user.status,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        }
    )


@router.patch("/users/{user_id}/unblock")
def unblock_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    admin, err = _require_admin(request, db)
    if err:
        return err

    user = db.get(User, user_id)
    if not user:
        return error(40401, "用户不存在", 404)

    if user.role == "admin":
        return error(42201, "管理员账号不可操作", 422)

    if user.status == "active":
        return error(42201, "用户当前未被封禁", 422)

    user.status = "active"

    _write_admin_log(
        db,
        admin_id=admin.id,
        target_type="user",
        target_id=user.id,
        action="unblock_user",
        reason=None,
    )

    db.commit()
    db.refresh(user)
    notice_ws_manager.notify_refresh(user.id, "unblock_user")

    return ok(
        {
            "id": user.id,
            "status": user.status,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        }
    )


@router.get("/artworks")
def get_admin_artworks(
    request: Request,
    page: int = Query(default=1),
    size: int = Query(default=20),
    visibility: str | None = Query(default=None),
    author_id: int | None = Query(default=None),
    keyword: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    _, err = _require_admin(request, db)
    if err:
        return err

    if page < 1 or size < 1 or size > 50:
        return error(40001, "分页参数不合法", 400)

    query = select(Artwork)
    if visibility:
        query = query.where(Artwork.visibility == visibility)
    if author_id:
        query = query.where(Artwork.author_id == author_id)
    if keyword:
        query = query.where(Artwork.title.like(f"%{keyword.strip()}%"))

    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    rows = db.scalars(
        query.order_by(Artwork.created_at.desc(), Artwork.id.desc())
        .offset((page - 1) * size)
        .limit(size)
    ).all()

    items = []
    for row in rows:
        author = db.get(User, row.author_id)
        style = db.get(Style, row.style_id)
        items.append(
            {
                "id": row.id,
                "title": row.title,
                "visibility": row.visibility,
                "author": {
                    "id": author.id if author else None,
                    "username": author.username if author else None,
                },
                "style": {
                    "id": style.id if style else None,
                    "name": style.name if style else None,
                },
                "like_count": row.like_count,
                "comment_count": row.comment_count,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "hall_published_at": row.hall_published_at.isoformat() if row.hall_published_at else None,
            }
        )

    return ok(
        {
            "list": items,
            "page": page,
            "size": size,
            "total": total,
            "has_more": page * size < total,
        }
    )


@router.patch("/artworks/{artwork_id}/hide")
def hide_artwork(
    artwork_id: int,
    payload: AdminHideArtworkRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    admin, err = _require_admin(request, db)
    if err:
        return err

    artwork = db.get(Artwork, artwork_id)
    if not artwork:
        return error(40401, "作品不存在", 404)

    if artwork.visibility == "hidden":
        return error(42201, "作品已下架", 422)

    artwork.visibility = "hidden"
    artwork.hall_published_at = None

    _write_admin_log(
        db,
        admin_id=admin.id,
        target_type="artwork",
        target_id=artwork.id,
        action="hide_artwork",
        reason=payload.reason,
    )

    db.commit()
    db.refresh(artwork)
    if artwork.author_id:
        notice_ws_manager.notify_refresh(artwork.author_id, "hide_artwork")

    return ok(
        {
            "id": artwork.id,
            "visibility": artwork.visibility,
            "updated_at": artwork.updated_at.isoformat() if artwork.updated_at else None,
        }
    )


@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    request: Request,
    payload: AdminDeleteCommentRequest | None = Body(default=None),
    db: Session = Depends(get_db),
):
    admin, err = _require_admin(request, db)
    if err:
        return err

    comment = db.get(Comment, comment_id)
    if not comment:
        return error(40401, "评论不存在", 404)

    if comment.status != "deleted":
        comment.status = "deleted"
        artwork = db.get(Artwork, comment.artwork_id)
        if artwork:
            artwork.comment_count = max((artwork.comment_count or 0) - 1, 0)

    _write_admin_log(
        db,
        admin_id=admin.id,
        target_type="comment",
        target_id=comment.id,
        action="delete_comment",
        reason=payload.reason if payload else None,
    )

    db.commit()
    db.refresh(comment)
    artwork = db.get(Artwork, comment.artwork_id)
    if artwork:
        artwork_ws_manager.notify_comments_refresh(
            artwork.id,
            "comment_delete",
            artwork.comment_count or 0,
        )
    if comment.user_id:
        notice_ws_manager.notify_refresh(comment.user_id, "delete_comment")

    return ok(
        {
            "id": comment.id,
            "status": comment.status,
            "updated_at": comment.updated_at.isoformat() if comment.updated_at else None,
        }
    )
