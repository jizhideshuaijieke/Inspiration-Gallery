from pydantic import BaseModel, Field


class UpdateUserProfileRequest(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=32, pattern=r"^[a-zA-Z0-9_]+$")
    avatar_url: str | None = Field(default=None, max_length=255)
