from pydantic import BaseModel, Field


class CreateCommentRequest(BaseModel):
    content: str = Field(min_length=1, max_length=500)
    parent_id: int | None = Field(default=None, gt=0)
