from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.artwork import Artwork
from app.models.style import Style
from app.models.user import User
from app.router.common import error, ok

router = APIRouter(prefix="/hall", tags=["hall"])


@router.get("/feed")
def get_hall_feed(
    page: int = Query(default=1),
    size: int = Query(default=20),
    db: Session = Depends(get_db),
):
    if page < 1 or size < 1 or size > 50:
        return error(40001, "分页参数不合法", 400)

    base_query = select(Artwork).where(Artwork.visibility == "hall")
    total = db.scalar(select(func.count()).select_from(base_query.subquery())) or 0

    rows = db.scalars(
        base_query.order_by(Artwork.hall_published_at.desc(), Artwork.id.desc())
        .offset((page - 1) * size)
        .limit(size)
    ).all()

    items = []
    for artwork in rows:
        style = db.get(Style, artwork.style_id)
        author = db.get(User, artwork.author_id)
        items.append(
            {
                "id": artwork.id,
                "title": artwork.title,
                "result_image_url": artwork.result_image_url,
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
                "hall_published_at": artwork.hall_published_at.isoformat() if artwork.hall_published_at else None,
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
