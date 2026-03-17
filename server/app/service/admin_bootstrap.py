from sqlalchemy import select

from app.db import SessionLocal
from app.models.user import User
from app.service.security import hash_password

DEFAULT_ADMIN_ACCOUNT_CODE = "admin1433223"
DEFAULT_ADMIN_PASSWORD = "admin1433223"
DEFAULT_ADMIN_USERNAME = "admin001"


def ensure_default_admin() -> None:
    with SessionLocal() as db:
        admin = db.scalar(select(User).where(User.account_code == DEFAULT_ADMIN_ACCOUNT_CODE))

        if admin is None:
            admin = db.scalar(select(User).where(User.role == "admin").order_by(User.id.asc()))

        if admin is None:
            username = DEFAULT_ADMIN_USERNAME
            suffix = 1
            while db.scalar(select(User.id).where(User.username == username)) is not None:
                suffix += 1
                username = f"{DEFAULT_ADMIN_USERNAME}_{suffix}"

            admin = User(
                account_code=DEFAULT_ADMIN_ACCOUNT_CODE,
                username=username,
                password_hash=hash_password(DEFAULT_ADMIN_PASSWORD),
                role="admin",
                status="active",
            )
            db.add(admin)
        else:
            admin.account_code = DEFAULT_ADMIN_ACCOUNT_CODE
            admin.role = "admin"
            admin.status = "active"
            admin.password_hash = hash_password(DEFAULT_ADMIN_PASSWORD)

        db.commit()
