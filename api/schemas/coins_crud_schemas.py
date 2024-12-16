"""
Schemas for validating and handling user, coin and transaction data using Pydantic models.
"""

__all__ = [
    "CoinActionSchema",
    "OperationActionSchema",
    "CoinInfoResponseSchema",
    "UserCoinsResponseSchema",
]

from typing import Sequence

from pydantic import BaseModel, field_validator, model_validator, Field


class UsernameFieldValidator(BaseModel):
    username: str = Field(min_length=3, max_length=50)

    @field_validator("username", mode="after")
    def validate_username(cls, value: str) -> str:
        """Validates the username according to specific rules."""
        value = value.strip().lower()

        if not value:
            raise ValueError("Invalid username")
        return value


class CoinInfoFieldsValidator(BaseModel):
    coin_name: str = Field(min_length=1, max_length=100)
    coin_symbol: str = Field(min_length=1, max_length=100)

    @field_validator("coin_name", mode="after")
    def coin_name_validator(cls, value: str) -> str:
        """Validate coin name."""
        value = value.strip().title()

        if not value:
            raise ValueError("Invalid coin name")
        return value

    @field_validator("coin_symbol", mode="after")
    def coin_symbol_validator(cls, value: str) -> str:
        """Validate coin symbol."""
        value = value.strip().upper()

        if not value or " " in value:
            raise ValueError("Invalid coin symbol")
        return value


class OperationFieldsValidator(BaseModel):
    buy: float = Field(ge=0, default=0)
    sell: float = Field(ge=0, default=0)
    paid: float = Field(ge=0, default=0)
    average_price: float = Field(ge=0, default=0)
    fee: float = Field(ge=0, default=0)

    @model_validator(mode="after")
    def validate_paid_or_average_price(cls, values) -> dict:
        """Validates and calculates missing values."""

        buy, sell, paid, average_price, fee = (values.buy, values.sell, values.paid, values.average_price, values.fee)

        if buy > 0 and sell > 0:
            raise ValueError("Only one of 'buys' or 'sell' can be greater than zero.")

        if buy == 0 and sell == 0:
            raise ValueError("Either 'buy' or 'sell' must be greater than zero.")

        if paid == 0 and average_price == 0:
            if fee == 0 and (buy > 0 or sell > 0):
                return values
            raise ValueError("Either 'paid' or 'average_price' must be set unless the transaction is free (fee=0).")

        if paid > 0 and average_price > 0:
            raise ValueError("Both 'paid' and 'average_price' can't be set at the same time.")

        total_units = buy if buy > 0 else sell

        if paid == 0 and average_price > 0:
            paid = total_units * average_price - fee
            if paid < 0:
                paid = 0

        elif average_price == 0 and paid > 0:
            if total_units == 0:
                raise ValueError("Can't calculate 'average_price' with zero units (buy or sell).")
            average_price = (paid + fee) / total_units

        values.paid, values.average_price = paid, average_price
        return values


class CoinActionSchema(
    UsernameFieldValidator,
    CoinInfoFieldsValidator,
): ...


class OperationActionSchema(
    UsernameFieldValidator,
    CoinInfoFieldsValidator,
    OperationFieldsValidator,
): ...


class CoinInfoResponseSchema(
    CoinInfoFieldsValidator,
): ...


class UserCoinsResponseSchema(BaseModel):
    coins: list[CoinInfoResponseSchema] | Sequence[CoinInfoResponseSchema]
