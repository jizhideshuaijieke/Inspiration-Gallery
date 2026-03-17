from fastapi import APIRouter, Depends, Query, Request, WebSocket, WebSocketDisconnect
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.db import SessionLocal, get_db
from app.models.artwork import Artwork
from app.models.artwork_like import ArtworkLike
from app.models.comment import Comment
from app.models.follow import Follow
from app.models.user import User
from app.router.common import error, ok
from app.schemas.comment import CreateCommentRequest
from app.service.artwork_ws_manager import artwork_ws_manager
from app.service.auth_identity import resolve_user_from_auth_header, resolve_user_from_token
from app.service.notice_ws_manager import notice_ws_manager

artwork_router = APIRouter(prefix="/artworks", tags=["social"])
user_router = APIRouter(prefix="/users", tags=["social"])


def _ensure_artwork_visible_to_user(artwork: Artwork, user: User | None):
    if artwork.visibility in {"private", "hidden"}:
        if not user or (user.id != artwork.author_id and user.role != "admin"):
            return error(42201, "作品不可见", 422)
    return None


@artwork_router.post("/{artwork_id}/like")
def like_artwork(artwork_id: int, request: Request, db: Session = Depends(get_db)):
    user = resolve_user_from_auth_header(request.headers.get("Authorization"), db)
    if not user:
        return error(40101, "未登录或token无效", 401)

    artwork = db.get(Artwork, artwork_id)
    if not artwork:
        return error(40401, "作品不存在", 404)
    err = _ensure_artwork_visible_to_user(artwork, user)
    if err:
        return err

    existed = db.get(ArtworkLike, {"artwork_id": artwork_id, "user_id": user.id})
    if existed:
        return error(40901, "重复点赞", 409)

    db.add(ArtworkLike(artwork_id=artwork_id, user_id=user.id))
    artwork.like_count = (artwork.like_count or 0) + 1
    db.commit()
    db.refresh(artwork)
    if artwork.author_id and artwork.author_id != user.id:
        notice_ws_manager.notify_refresh(artwork.author_id, "like")
    return ok({"artwork_id": artwork.id, "liked": True, "like_count": artwork.like_count})


@artwork_router.delete("/{artwork_id}/like")
def unlike_artwork(artwork_id: int, request: Request, db: Session = Depends(get_db)):
    user = resolve_user_from_auth_header(request.headers.get("Authorization"), db)
    if not user:
        return error(40101, "未登录或token无效", 401)

    artwork = db.get(Artwork, artwork_id)
    if not artwork:
        return error(40401, "作品不存在", 404)
    err = _ensure_artwork_visible_to_user(artwork, user)
    if err:
        return err

    existed = db.get(ArtworkLike, {"artwork_id": artwork_id, "user_id": user.id})
    if existed:
        db.delete(existed)
        artwork.like_count = max((artwork.like_count or 0) - 1, 0)
        db.commit()
        db.refresh(artwork)
        if artwork.author_id and artwork.author_id != user.id:
            notice_ws_manager.notify_refresh(artwork.author_id, "unlike")

    return ok({"artwork_id": artwork.id, "liked": False, "like_count": artwork.like_count})


@artwork_router.get("/{artwork_id}/comments")
def get_comments(
    artwork_id: int,
    request: Request,
    page: int = Query(default=1),
    size: int = Query(default=20),
    db: Session = Depends(get_db),
):
    if page < 1 or size < 1 or size > 50:
        return error(40001, "分页参数不合法", 400)

    artwork = db.get(Artwork, artwork_id)
    if not artwork:
        return error(40401, "作品不存在", 404)
    viewer = resolve_user_from_auth_header(request.headers.get("Authorization"), db)
    err = _ensure_artwork_visible_to_user(artwork, viewer)
    if err:
        return err

    query = select(Comment).where(
        and_(Comment.artwork_id == artwork_id, Comment.status == "visible")
    )
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    rows = db.scalars(
        query.order_by(Comment.created_at.asc(), Comment.id.asc())
        .offset((page - 1) * size)
        .limit(size)
    ).all()

    items = []
    for row in rows:
        author = db.get(User, row.user_id)
        items.append(
            {
                "id": row.id,
                "content": row.content,
                "status": row.status,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "user": {
                    "id": author.id if author else None,
                    "username": author.username if author else None,
                    "avatar_url": author.avatar_url if author else None,
                },
                "parent_id": row.parent_id,
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


@artwork_router.websocket("/{artwork_id}/comments/ws")
async def watch_comments(artwork_id: int, websocket: WebSocket):
    token = websocket.query_params.get("token")
    db = SessionLocal()

    try:
        viewer = resolve_user_from_token(token, db) if token else None
        artwork = db.get(Artwork, artwork_id)
        if not artwork:
            await websocket.close(code=1008, reason="作品不存在")
            return

        if artwork.visibility in {"private", "hidden"}:
            if not viewer or (viewer.id != artwork.author_id and viewer.role != "admin"):
                await websocket.close(code=1008, reason="作品不可见")
                return

        await artwork_ws_manager.connect(artwork_id, websocket)
        await websocket.send_json(
            {
                "type": "connected",
                "artwork_id": artwork_id,
                "comment_count": artwork.comment_count or 0,
            }
        )
        db.close()

        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await artwork_ws_manager.disconnect(artwork_id, websocket)
        db.close()


@artwork_router.post("/{artwork_id}/comments")
def post_comment(
    artwork_id: int,
    payload: CreateCommentRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    user = resolve_user_from_auth_header(request.headers.get("Authorization"), db)
    if not user:
        return error(40101, "未登录或token无效", 401)

    artwork = db.get(Artwork, artwork_id)
    if not artwork:
        return error(40401, "作品不存在", 404)
    err = _ensure_artwork_visible_to_user(artwork, user)
    if err:
        return err

    if payload.parent_id is not None:
        parent = db.get(Comment, payload.parent_id)
        if not parent or parent.artwork_id != artwork_id:
            return error(42201, "父评论不存在或不属于该作品", 422)

    comment = Comment(
        artwork_id=artwork_id,
        user_id=user.id,
        parent_id=payload.parent_id,
        content=payload.content,
        status="visible",
    )
    db.add(comment)
    artwork.comment_count = (artwork.comment_count or 0) + 1
    db.commit()
    db.refresh(comment)
    db.refresh(artwork)
    artwork_ws_manager.notify_comments_refresh(
        artwork.id,
        "comment_post",
        artwork.comment_count or 0,
    )
    if artwork.author_id and artwork.author_id != user.id:
        notice_ws_manager.notify_refresh(artwork.author_id, "comment")

    return ok(
        {
            "id": comment.id,
            "artwork_id": comment.artwork_id,
            "user_id": comment.user_id,
            "parent_id": comment.parent_id,
            "content": comment.content,
            "status": comment.status,
            "created_at": comment.created_at.isoformat() if comment.created_at else None,
        }
    )


@user_router.post("/{user_id}/follow")
def follow_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    user = resolve_user_from_auth_header(request.headers.get("Authorization"), db)
    if not user:
        return error(40101, "未登录或token无效", 401)

    target = db.get(User, user_id)
    if not target:
        return error(40401, "用户不存在", 404)

    if user.id == user_id:
        return error(40901, "不能关注自己", 409)

    existed = db.get(Follow, {"follower_id": user.id, "followee_id": user_id})
    if existed:
        return error(40901, "重复关注", 409)

    db.add(Follow(follower_id=user.id, followee_id=user_id))
    db.commit()

    followers_count = db.scalar(
        select(func.count()).select_from(Follow).where(Follow.followee_id == user_id)
    ) or 0
    return ok({"user_id": user_id, "followed": True, "followers_count": followers_count})


@user_router.delete("/{user_id}/follow")
def unfollow_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    user = resolve_user_from_auth_header(request.headers.get("Authorization"), db)
    if not user:
        return error(40101, "未登录或token无效", 401)

    target = db.get(User, user_id)
    if not target:
        return error(40401, "用户不存在", 404)

    relation = db.get(Follow, {"follower_id": user.id, "followee_id": user_id})
    if relation:
        db.delete(relation)
        db.commit()

    followers_count = db.scalar(
        select(func.count()).select_from(Follow).where(Follow.followee_id == user_id)
    ) or 0
    return ok({"user_id": user_id, "followed": False, "followers_count": followers_count})
