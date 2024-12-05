import re
import hashlib
from typing import List

from pydantic import BaseModel, EmailStr, Field, field_validator


class NewUserSchema(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)

    @field_validator("username", mode="after")
    def validate_username(cls, value: str) -> str:
        """
        Validates the username according to specific rules:
        - Must contain only letters, numbers, dots, or underscores.
        - Length must be between 3 and 30 characters.
        - Cannot start or end with a dot or underscore.
        - Cannot match reserved names (e.g., 'admin', 'root', etc.).

        Args:
            value (str): The username to validate.

        Returns:
            str: The validated and normalized username (converted to lowercase).

        Raises:
            ValueError: If the username fails any of the validation rules.
        """

        if not re.fullmatch(r"^[a-zA-Z0-9._]{3,30}$", value):
            raise ValueError("Username can only contain letters, numbers, dots, or underscores.")

        if value.startswith((".", "_")) or value.endswith((".", "_")):
            raise ValueError("Username cannot start or end with a dot or underscore.")

        reserved_names = {"admin", "root", "support", "help"}
        if value in reserved_names:
            raise ValueError("This username is reserved.")

        return value.strip().lower()

    @field_validator("password", mode="after")
    def validate_and_hash_password(cls, value: str) -> str:
        """
        Validates and hashes the password:
        - Must include at least one uppercase letter.
        - Must include at least one lowercase letter.
        - Must include at least one digit.
        - Must include at least one special character.
        - Converts the password to its SHA-256 hash for secure storage.

        Args:
            value (str): The password to validate and hash.

        Returns:
            str: The hashed password.

        Raises:
            ValueError: If the password fails any of the validation rules.
        """

        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter.")

        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter.")

        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one digit.")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Password must contain at least one special character.")

        return hashlib.sha256(value.encode()).hexdigest()


class AllUsersSchema(BaseModel):
    users: List[str]


class UserInfoSchema(BaseModel):
    username: str
    email: str
