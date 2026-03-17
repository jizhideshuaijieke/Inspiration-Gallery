from fastapi import APIRouter, Depends, File, Query, Request, UploadFile, WebSocket, WebSocketDisconnect
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.db import SessionLocal, get_db
from app.models.admin_log import AdminLog
from app.models.artwork import Artwork
from app.models.comment import Comment
from app.models.follow import Follow
from app.models.style import Style
from app.models.user import User
from app.router.common import error, ok
from app.schemas.user import UpdateUserProfileRequest
from app.service.auth_identity import resolve_user_from_auth_header, resolve_user_from_token
from app.service.media_store import build_absolute_media_url, save_uploaded_image
from app.service.notice_ws_manager import notice_ws_manager

router = APIRouter(prefix="/users", tags=["users"])


def _validate_pagination(page: int, size: int):
    if page < 1 or size < 1 or size > 50:
        return error(40001, "分页参数不合法", 400)
    return None


def _build_admin_notice_from_user_log(log: AdminLog):
    if log.action == "block_user":
        return {
            "id": f"admin-{log.id}",
            "type": "admin",
            "action": log.action,
            "title": "账号已被管理员封禁",
            "body": "当前账号已被限制使用，请联系管理员处理。",
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }

    if log.action == "unblock_user":
        return {
            "id": f"admin-{log.id}",
            "type": "admin",
            "action": log.action,
            "title": "账号已解除封禁",
            "body": "账号状态已恢复，你现在可以继续正常使用。",
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }

    return None


def _build_admin_notice_from_artwork_log(log: AdminLog, artwork: Artwork):
    if log.action != "hide_artwork":
        return None

    reason = (log.reason or "").strip()
    body = f"原因：{reason}" if reason else "管理员已将这幅作品从大厅下架，请在仓库中修改后再处理。"

    return {
        "id": f"admin-{log.id}",
        "type": "admin",
        "action": log.action,
        "title": f"你的作品《{artwork.title or '未命名作品'}》已被管理员下架",
        "body": body,
        "created_at": log.created_at.isoformat() if log.created_at else None,
        "artwork_id": artwork.id,
        "action_label": "去仓库查看",
        "target_view": "me",
    }


def _build_admin_notice_from_comment_log(log: AdminLog, comment: Comment, artwork: Artwork | None):
    if log.action != "delete_comment":
        return None

    artwork_title = artwork.title if artwork and artwork.title else "未命名作品"
    reason = (log.reason or "").strip()
    body = f"原因：{reason}" if reason else f"评论内容：{comment.content}"

    return {
        "id": f"admin-{log.id}",
        "type": "admin",
        "action": log.action,
        "title": f"你在《{artwork_title}》下的评论已被管理员删除",
        "body": body,
        "created_at": log.created_at.isoformat() if log.created_at else None,
    }


@router.get("/me/notices")
def get_my_notices(
    request: Request,
    page: int = Query(default=1),
    size: int = Query(default=20),
    db: Session = Depends(get_db),
):
    bad = _validate_pagination(page, size)
    if bad:
        return bad

    user = resolve_user_from_auth_header(request.headers.get("Authorization"), db)
    if not user:
        return error(40101, "未登录或token无效", 401)

    notices_with_time: list[tuple[object, dict]] = []

    user_logs = db.scalars(
        select(AdminLog)
        .where(AdminLog.target_type == "user", AdminLog.target_id == user.id)
        .order_by(AdminLog.created_at.desc(), AdminLog.id.desc())
    ).all()
    for log in user_logs:
        item = _build_admin_notice_from_user_log(log)
        if item:
            notices_with_time.append((log.created_at, item))

    artwork_rows = db.execute(
        select(AdminLog, Artwork)
        .join(
            Artwork,
            and_(AdminLog.target_type == "artwork", AdminLog.target_id == Artwork.id),
        )
        .where(Artwork.author_id == user.id)
        .order_by(AdminLog.created_at.desc(), AdminLog.id.desc())
    ).all()
    for log, artwork in artwork_rows:
        item = _build_admin_notice_from_artwork_log(log, artwork)
        if item:
            notices_with_time.append((log.created_at, item))

    comment_rows = db.execute(
        select(AdminLog, Comment, Artwork)
        .join(
            Comment,
            and_(AdminLog.target_type == "comment", AdminLog.target_id == Comment.id),
        )
        .join(Artwork, Artwork.id == Comment.artwork_id)
        .where(Comment.user_id == user.id)
        .order_by(AdminLog.created_at.desc(), AdminLog.id.desc())
    ).all()
    for log, comment, artwork in comment_rows:
        item = _build_admin_notice_from_comment_log(log, comment, artwork)
        if item:
            notices_with_time.append((log.created_at, item))

    notices_with_time.sort(
        key=lambda item: (
            item[0].isoformat() if item[0] else "",
            item[1]["id"],
        ),
        reverse=True,
    )

    total = len(notices_with_time)
    start = (page - 1) * size
    end = start + size
    items = [item for _, item in notices_with_time[start:end]]

    return ok(
        {
            "list": items,
            "page": page,
            "size": size,
            "total": total,
            "has_more": end < total,
        }
    )


@router.websocket("/ws/notices")
async def watch_my_notices(websocket: WebSocket):
    token = websocket.query_params.get("token")
    db = SessionLocal()

    try:
        user = resolve_user_from_token(token, db)
        if not user:
            await websocket.close(code=1008, reason="未登录或token无效")
            return

        await notice_ws_manager.connect(user.id, websocket)
        await websocket.send_json({"type": "connected"})
        db.close()

        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await notice_ws_manager.disconnect(user.id if "user" in locals() and user else 0, websocket)
        db.close()


@router.get("/{user_id}")
def get_user_profile(user_id: int, request: Request, db: Session = Depends(get_db)):
    target = db.get(User, user_id)
    if not target:
        return error(40401, "用户不存在", 404)

    viewer = resolve_user_from_auth_header(request.headers.get("Authorization"), db)

    visible_query = select(Artwork).where(Artwork.author_id == user_id)
    if not viewer or (viewer.id != user_id and viewer.role != "admin"):
        visible_query = visible_query.where(Artwork.visibility.in_(["profile", "hall"]))

    artworks_count = db.scalar(select(func.count()).select_from(visible_query.subquery())) or 0
    likes_received = db.scalar(
        select(func.coalesce(func.sum(Artwork.like_count), 0)).where(
            and_(Artwork.author_id == user_id, Artwork.visibility.in_(["profile", "hall"]))
        )
    ) or 0

    followers_count = db.scalar(
        select(func.count()).select_from(Follow).where(Follow.followee_id == user_id)
    ) or 0
    following_count = db.scalar(
        select(func.count()).select_from(Follow).where(Follow.follower_id == user_id)
    ) or 0

    is_following = False
    if viewer and viewer.id != user_id:
        relation = db.get(Follow, {"follower_id": viewer.id, "followee_id": user_id})
        is_following = relation is not None

    return ok(
        {
            "id": target.id,
            "account_code": target.account_code,
            "username": target.username,
            "avatar_url": target.avatar_url,
            "role": target.role,
            "status": target.status,
            "stats": {
                "followers_count": followers_count,
                "following_count": following_count,
                "artworks_count": artworks_count,
                "likes_received": int(likes_received),
            },
            "is_following": is_following,
            "created_at": target.created_at.isoformat() if target.created_at else None,
        }
    )


@router.post("/me/avatar")
def upload_my_avatar(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    user = resolve_user_from_auth_header(request.headers.get("Authorization"), db)
    if not user:
        return error(40101, "未登录或token无效", 401)

    try:
        relative_url = save_uploaded_image(file)
    except ValueError as exc:
        return error(40001, str(exc), 400)

    return ok({"avatar_url": build_absolute_media_url(request, relative_url)})


@router.patch("/me")
def update_my_profile(
    payload: UpdateUserProfileRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    user = resolve_user_from_auth_header(request.headers.get("Authorization"), db)
    if not user:
        return error(40101, "未登录或token无效", 401)

    if payload.username is None and payload.avatar_url is None:
        return error(40001, "至少提供一个可更新字段", 400)

    if payload.username is not None:
        username = payload.username.strip()
        if not username:
            return error(40001, "用户名不能为空", 400)
        if username != user.username:
            existed = db.scalar(select(User).where(User.username == username))
            if existed:
                return error(40901, "用户名已存在", 409)
        user.username = username

    if payload.avatar_url is not None:
        avatar_url = payload.avatar_url.strip()
        user.avatar_url = avatar_url or None

    db.commit()
    db.refresh(user)

    return ok(
        {
            "id": user.id,
            "account_code": user.account_code,
            "username": user.username,
            "avatar_url": user.avatar_url,
            "role": user.role,
            "status": user.status,
        }
    )


@router.get("/{user_id}/artworks")
def get_user_artworks(
    user_id: int,
    request: Request,
    page: int = Query(default=1),
    size: int = Query(default=20),
    db: Session = Depends(get_db),
):
    bad = _validate_pagination(page, size)
    if bad:
        return bad

    target = db.get(User, user_id)
    if not target:
        return error(40401, "用户不存在", 404)

    viewer = resolve_user_from_auth_header(request.headers.get("Authorization"), db)

    query = select(Artwork).where(Artwork.author_id == user_id)
    if not viewer or (viewer.id != user_id and viewer.role != "admin"):
        query = query.where(Artwork.visibility.in_(["profile", "hall"]))

    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    rows = db.scalars(
        query.order_by(Artwork.created_at.desc(), Artwork.id.desc())
        .offset((page - 1) * size)
        .limit(size)
    ).all()

    items = []
    for artwork in rows:
        style = db.get(Style, artwork.style_id)
        items.append(
            {
                "id": artwork.id,
                "title": artwork.title,
                "result_image_url": artwork.result_image_url,
                "visibility": artwork.visibility,
                "style": {
                    "id": style.id if style else None,
                    "code": style.code if style else None,
                    "name": style.name if style else None,
                },
                "like_count": artwork.like_count,
                "comment_count": artwork.comment_count,
                "download_count": artwork.download_count,
                "created_at": artwork.created_at.isoformat() if artwork.created_at else None,
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


@router.get("/{user_id}/followers")
def get_user_followers(
    user_id: int,
    page: int = Query(default=1),
    size: int = Query(default=20),
    db: Session = Depends(get_db),
):
    bad = _validate_pagination(page, size)
    if bad:
        return bad

    target = db.get(User, user_id)
    if not target:
        return error(40401, "用户不存在", 404)

    query = select(Follow).where(Follow.followee_id == user_id)
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    rows = db.scalars(
        query.order_by(Follow.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    ).all()

    items = []
    for relation in rows:
        follower = db.get(User, relation.follower_id)
        items.append(
            {
                "id": follower.id if follower else relation.follower_id,
                "username": follower.username if follower else None,
                "avatar_url": follower.avatar_url if follower else None,
                "followed_at": relation.created_at.isoformat() if relation.created_at else None,
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


@router.get("/{user_id}/following")
def get_user_following(
    user_id: int,
    page: int = Query(default=1),
    size: int = Query(default=20),
    db: Session = Depends(get_db),
):
    bad = _validate_pagination(page, size)
    if bad:
        return bad

    target = db.get(User, user_id)
    if not target:
        return error(40401, "用户不存在", 404)

    query = select(Follow).where(Follow.follower_id == user_id)
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    rows = db.scalars(
        query.order_by(Follow.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    ).all()

    items = []
    for relation in rows:
        followee = db.get(User, relation.followee_id)
        items.append(
            {
                "id": followee.id if followee else relation.followee_id,
                "username": followee.username if followee else None,
                "avatar_url": followee.avatar_url if followee else None,
                "followed_at": relation.created_at.isoformat() if relation.created_at else None,
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
