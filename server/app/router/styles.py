from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.style import Style
from app.router.common import ok

router = APIRouter(prefix="/styles", tags=["styles"])


@router.get("")
def get_styles(db: Session = Depends(get_db)):
    rows = db.scalars(
        select(Style).where(Style.is_active.is_(True)).order_by(Style.id.asc())
    ).all()
    return ok(
        {
            "list": [
                {
                    "id": row.id,
                    "code": row.code,
                    "name": row.name,
                }
                for row in rows
            ]
        }
    )
