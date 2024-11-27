"""Schemas for API"""

import hashlib
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator


class UserCredentialsSchema(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("username", mode="after")
    def username_validator(cls, value: str):
        """validate username"""

        value = value.strip().lower()
        return value

    @field_validator("password", mode="after")
    def password_validator(cls, value: str):
        """validate password"""

        value = hashlib.sha256(value.encode()).hexdigest()
        return value


class UserCoinSchema(BaseModel):
    username: str
    coin_name: str
    coin_symbol: str

    @field_validator("username", mode="after")
    def username_validator(cls, value: str):
        """validate username"""

        value = value.strip().lower()
        return value

    @field_validator("coin_name", mode="after")
    def coin_name_validator(cls, value: str):
        """validate coin_name"""

        value = value.strip()
        return value

    @field_validator("coin_symbol", mode="after")
    def coin_symbol_validator(cls, value: str):
        """validate coin symbol"""

        value = value.strip().upper()
        return value
