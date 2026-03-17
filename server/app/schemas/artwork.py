from typing import Literal

from pydantic import BaseModel, Field


class CreateArtworkRequest(BaseModel):
    task_id: int = Field(gt=0)
    title: str | None = Field(default=None, max_length=100)


class UpdateArtworkRequest(BaseModel):
    title: str | None = Field(default=None, max_length=100)
    visibility: Literal["private", "profile", "hall"] | None = None
