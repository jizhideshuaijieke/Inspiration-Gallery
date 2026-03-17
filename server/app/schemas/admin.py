from pydantic import BaseModel, Field


class AdminHideArtworkRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=200)


class AdminDeleteCommentRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=200)
