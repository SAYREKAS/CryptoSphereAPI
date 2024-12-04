from typing import List

from pydantic import BaseModel, Field, field_validator

from src.schemas.common_schemas import ActionResult


class UserActionCoinSchema(BaseModel):
    username: str
    coin_name: str
    coin_symbol: str

    @field_validator("username", mode="after")
    def username_validator(cls, value: str) -> str:
        """Validate username."""
        return value.strip().lower()

    @field_validator("coin_name", mode="after")
    def coin_name_validator(cls, value: str) -> str:
        """Validate coin name."""
        return value.strip().title()

    @field_validator("coin_symbol", mode="after")
    def coin_symbol_validator(cls, value: str) -> str:
        """Validate coin symbol."""
        return value.strip().upper()


class ActionCoinSchema(ActionResult):
    coin_name: str
    coin_symbol: str


class CoinSchema(BaseModel):
    coin_name: str
    coin_symbol: str


class UserCoinsSchema(BaseModel):
    coins: List[CoinSchema]


class NewTransactionSchema(BaseModel):
    coin_info: UserActionCoinSchema
    buy: float | None = Field(ge=0, default=0)
    sell: float | None = Field(ge=0, default=0)
    usd: float | None = Field(ge=0, default=0)
