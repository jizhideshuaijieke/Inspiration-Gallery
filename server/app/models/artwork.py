from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Artwork(Base):
    __tablename__ = "artworks"
    __table_args__ = (
        CheckConstraint(
            "visibility in ('private','profile','hall','hidden')",
            name="ck_artworks_visibility",
        ),
        CheckConstraint("like_count >= 0", name="ck_artworks_like_count"),
        CheckConstraint("comment_count >= 0", name="ck_artworks_comment_count"),
        CheckConstraint("download_count >= 0", name="ck_artworks_download_count"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    style_id: Mapped[int] = mapped_column(ForeignKey("styles.id"), nullable=False, index=True)

    title: Mapped[str] = mapped_column(String(100), nullable=False, server_default="Untitled")
    source_image_url: Mapped[str] = mapped_column(String(255), nullable=False)
    result_image_url: Mapped[str] = mapped_column(String(255), nullable=False)
    visibility: Mapped[str] = mapped_column(String(16), nullable=False, server_default="private")

    like_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    comment_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    download_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")

    hall_published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
