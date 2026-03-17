from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=32, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(min_length=6, max_length=20)


class LoginRequest(BaseModel):
    account_code: str | None = Field(
        default=None,
        min_length=12,
        max_length=12,
        pattern=r"^(lghl\d{8}|admin\d{7})$",
    )
    username: str | None = Field(default=None, min_length=1, max_length=32)
    password: str = Field(min_length=1, max_length=64)
