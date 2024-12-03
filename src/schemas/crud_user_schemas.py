import hashlib

from pydantic import BaseModel, EmailStr, field_validator
from typing import List

from src.schemas.common_schemas import ActionResult


class NewUserInfoSchema(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("username", mode="after")
    def username_validator(cls, value):
        """validate username"""
        value = value.strip().lower()
        return value

    @field_validator("password", mode="after")
    def password_validator(cls, value):
        """validate password"""
        value = hashlib.sha256(value.encode()).hexdigest()
        return value


class AllUsersSchema(BaseModel):
    users: List[str]


class DeleteUserResultSchema(ActionResult):
    username: str


class UserInfoSchema(ActionResult):
    username: str | None = None
    email: EmailStr | None = None
