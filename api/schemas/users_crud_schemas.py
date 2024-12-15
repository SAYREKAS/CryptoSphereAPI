__all__ = [
    "reserved_names",
    "UserActionSchema",
    "UserInfoSchema",
    "FullUserInfoSchema",
    "AllUsersSchema",
]

import re
import hashlib
from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator

reserved_names = {"admin", "root", "support", "help"}


class UsernameFieldValidator(BaseModel):
    username: str

    @field_validator("username", mode="after")
    def validate_username(cls, value: str) -> str:
        """Validates the username according to specific rules"""

        value = value.strip().lower()

        if not re.fullmatch(r"^[a-zA-Z0-9._]{3,30}$", value):
            raise ValueError("Username can only contain letters, numbers, dots, or underscores.")

        if value.startswith((".", "_")) or value.endswith((".", "_")):
            raise ValueError("Username cannot start or end with a dot or underscore.")

        if value in reserved_names:
            raise ValueError("This username is reserved.")

        return value


class EmailFieldValidator(BaseModel):
    email: EmailStr

    @field_validator("email", mode="after")
    def validate_email(cls, value: str) -> str:
        """Validates the email address according to specific rules"""
        return value.strip().lower()


class PasswordFieldValidator(BaseModel):
    password: str

    @field_validator("password", mode="after")
    def validate_and_hash_password(cls, value: str) -> str:
        """Validates and hashes the password"""

        if not 8 < len(value) < 64:
            raise ValueError("Password must be at least 8 characters long.")

        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter.")

        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter.")

        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one digit.")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Password must contain at least one special character.")

        return hashlib.sha256(value.encode()).hexdigest()


class UserActionSchema(UsernameFieldValidator, EmailFieldValidator, PasswordFieldValidator):
    pass


class UserInfoSchema(UsernameFieldValidator, EmailFieldValidator):
    pass


class FullUserInfoSchema(UsernameFieldValidator, EmailFieldValidator):
    id: int
    hash_password: str
    registered_at: datetime


class AllUsersSchema(BaseModel):
    users: list[str]
