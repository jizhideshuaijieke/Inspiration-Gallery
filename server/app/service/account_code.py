import secrets

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User

ACCOUNT_CODE_PREFIX = "lghl"
ACCOUNT_CODE_DIGITS = 8


def build_account_code(number: int) -> str:
    return f"{ACCOUNT_CODE_PREFIX}{number:0{ACCOUNT_CODE_DIGITS}d}"


def generate_account_code(db: Session) -> str:
    lower = 10 ** (ACCOUNT_CODE_DIGITS - 1)
    upper = (10**ACCOUNT_CODE_DIGITS) - 1

    while True:
        candidate = build_account_code(secrets.randbelow(upper - lower + 1) + lower)
        existed = db.scalar(select(User.id).where(User.account_code == candidate))
        if not existed:
            return candidate
