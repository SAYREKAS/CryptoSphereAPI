import re
import hashlib
from typing import Sequence

from pydantic import BaseModel, EmailStr, Field, field_validator

reserved_names = {"admin", "root", "support", "help"}


class CommonFieldsValidator(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    email: EmailStr
    password: str | None = None

    @field_validator("username", mode="after")
    def validate_username(cls, value: str) -> str:
        """Validates the username according to specific rules"""

        if not re.fullmatch(r"^[a-zA-Z0-9._]{3,30}$", value):
            raise ValueError("Username can only contain letters, numbers, dots, or underscores.")

        if value.startswith((".", "_")) or value.endswith((".", "_")):
            raise ValueError("Username cannot start or end with a dot or underscore.")

        if value in reserved_names:
            raise ValueError("This username is reserved.")

        return value.strip().lower()

    @field_validator("password", mode="after")
    def validate_and_hash_password(cls, value: str) -> str:
        """Validates and hashes the password"""

        if value:

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

        return value


class AllUsersSchema(BaseModel):
    users: Sequence[str]


class UserInfoSchema(CommonFieldsValidator):
    pass
