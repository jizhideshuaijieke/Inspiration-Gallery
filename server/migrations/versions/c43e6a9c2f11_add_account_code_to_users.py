"""add_account_code_to_users

Revision ID: c43e6a9c2f11
Revises: a11412d549e0
Create Date: 2026-03-11 16:40:00.000000

"""
from typing import Sequence, Union
import secrets

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c43e6a9c2f11"
down_revision: Union[str, Sequence[str], None] = "a11412d549e0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ACCOUNT_CODE_PREFIX = "lghl"


def _build_random_account_code(existing_codes: set[str]) -> str:
    while True:
        candidate = f"{ACCOUNT_CODE_PREFIX}{secrets.randbelow(90000000) + 10000000}"
        if candidate not in existing_codes:
            existing_codes.add(candidate)
            return candidate


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("account_code", sa.String(length=12), nullable=True))

    connection = op.get_bind()
    rows = connection.execute(sa.text("SELECT id FROM users ORDER BY id")).fetchall()
    existing_codes: set[str] = set()

    for row in rows:
        account_code = _build_random_account_code(existing_codes)
        connection.execute(
            sa.text("UPDATE users SET account_code = :account_code WHERE id = :user_id"),
            {"account_code": account_code, "user_id": row.id},
        )

    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.alter_column(
            "account_code",
            existing_type=sa.String(length=12),
            nullable=False,
        )
        batch_op.create_index(batch_op.f("ix_users_account_code"), ["account_code"], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_users_account_code"))
        batch_op.drop_column("account_code")
