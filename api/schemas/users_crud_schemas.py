"""
Module containing Pydantic schemas for user validation and response handling.
"""

__all__ = [
    "reserved_names",
    "UserActionSchema",
    "UserInfoResponseSchema",
    "UserInfoResponseSchema",
    "AllUsersResponseSchema",
]

import re
import hashlib
from typing import Sequence
from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator, Field

reserved_names = {"admin", "root", "support", "help"}


class IdField(BaseModel):
    id: int = Field(ge=1)


class UsernameField(BaseModel):
    username: str = Field(min_length=3, max_length=50)

    @field_validator("username", mode="after")
    def validate_username(cls, value: str) -> str:
        """Validates the username according to specific rules"""

        value = value.strip().lower()

        if not re.fullmatch(r"^[a-zA-Z0-9._]+$", value):
            raise ValueError("Username can only contain letters, numbers, dots or underscores.")

        if value.startswith((".", "_")) or value.endswith((".", "_")):
            raise ValueError("Username can't start or end with a dot or underscore.")

        if value in reserved_names:
            raise ValueError("This username is reserved.")

        return value


class EmailField(BaseModel):
    email: EmailStr

    @field_validator("email", mode="after")
    def validate_email(cls, value: str) -> str:
        """Validates the email address according to specific rules"""
        return value.strip().lower()


class PasswordField(BaseModel):
    password: str

    @field_validator("password", mode="after")
    def validate_and_hash_password(cls, value: str) -> str:
        """Validates and hashes the password"""

        if not 8 < len(value) < 64:
            raise ValueError("Password must be at least eight characters long.")

        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter.")

        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter.")

        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one digit.")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Password must contain at least one special character.")

        return hashlib.sha256(value.encode()).hexdigest()


class RegisteredAtField(BaseModel):
    registered_at: datetime


class UserActionSchema(
    UsernameField,
    EmailField,
    PasswordField,
): ...


class UserInfoResponseSchema(
    IdField,
    UsernameField,
    EmailField,
    RegisteredAtField,
): ...


class AllUsersResponseSchema(BaseModel):
    users: Sequence[UserInfoResponseSchema] | list[UserInfoResponseSchema]
