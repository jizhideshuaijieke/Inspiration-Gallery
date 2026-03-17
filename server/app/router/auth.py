from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.router.common import error, ok
from app.schemas.auth import LoginRequest, RegisterRequest
from app.service.account_code import generate_account_code
from app.service.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existed = db.scalar(select(User).where(User.username == payload.username))
    if existed:
        return error(40901, "用户名已存在", 409)

    user = User(
        account_code=generate_account_code(db),
        username=payload.username,
        password_hash=hash_password(payload.password),
        role="user",
        status="active",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id, user.role)
    return ok(
        {
            "user": {
                "id": user.id,
                "account_code": user.account_code,
                "username": user.username,
                "role": user.role,
            },
            "token": token,
        }
    )


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = None
    if payload.account_code:
        user = db.scalar(select(User).where(User.account_code == payload.account_code))
    elif payload.username:
        user = db.scalar(select(User).where(User.username == payload.username))
    else:
        return error(40001, "请提供账号编号或用户名", 400)

    if not user or not verify_password(payload.password, user.password_hash):
        return error(40101, "账号编号/用户名或密码错误", 401)

    if user.status != "active":
        return error(40301, "账号被禁用", 403)

    token = create_access_token(user.id, user.role)
    return ok(
        {
            "user": {
                "id": user.id,
                "account_code": user.account_code,
                "username": user.username,
                "role": user.role,
            },
            "token": token,
        }
    )
