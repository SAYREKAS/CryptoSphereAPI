import hashlib
from typing import List

from pydantic import BaseModel, EmailStr, Field, field_validator

from src.schemas.common_schemas import ActionResult


class NewUserInfoSchema(BaseModel):
    username: str = Field(max_length=50)
    email: EmailStr = Field(max_length=70)
    password: str = Field(min_length=8, max_length=64)

    @field_validator("username", mode="after")
    def validate_username(cls, value: str) -> str:
        """Ensure the username is lowercase and stripped of spaces."""
        return value.strip().lower()

    @field_validator("password", mode="after")
    def hash_password(cls, value: str) -> str:
        """Hash the user's password using SHA-256."""
        return hashlib.sha256(value.encode()).hexdigest()


class AllUsersSchema(BaseModel):
    users: List[str]


class DeleteUserResultSchema(ActionResult):
    username: str


class UserInfoSchema(ActionResult):
    username: str | None = None
    email: EmailStr | None = None
