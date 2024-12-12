from pydantic import BaseModel, field_validator, model_validator, Field
from typing import List


class CommonFieldsValidator(BaseModel):
    username: str | None = None
    name: str | None = None
    symbol: str | None = None

    @field_validator("username", mode="after")
    def validate_username(cls, value: str) -> str:
        """Validates the username according to specific rules."""
        if value:
            return value.strip().lower()
        return value

    @field_validator("name", mode="after")
    def coin_name_validator(cls, value: str) -> str:
        """Validate coin name."""
        if value:
            return value.strip().title()
        return value

    @field_validator("symbol", mode="after")
    def coin_symbol_validator(cls, value: str) -> str:
        """Validate coin symbol."""
        if value:
            if len(value.split()) > 1:
                raise ValueError("Invalid coin symbol")
            return value.strip().upper()
        return value


class CoinInfoSchema(CommonFieldsValidator):
    pass


class UserCoinsSchema(BaseModel):
    coins: List[CoinInfoSchema]


class CoinOperationSchema(BaseModel):
    buy: float = Field(ge=0, default=0.0)
    sell: float = Field(ge=0, default=0.0)
    paid: float = Field(ge=0, default=0.0)
    average_price: float = Field(ge=0, default=0.0)
    fee: float = Field(ge=0, default=0.0)

    @model_validator(mode="after")
    def validate_paid_or_average_price(cls, values) -> dict:
        """Validates and calculates missing values for paid and average_price based on buy and sell."""

        buy, sell, paid, average_price = values.buy, values.sell, values.paid, values.average_price

        # Basic validations
        if buy == 0 and sell == 0:
            raise ValueError("Cannot calculate missing data. Both 'buy' and 'sell' are zero.")
        if paid > 0 and average_price > 0:
            raise ValueError("There must be only one of 'paid' or 'average_price' provided, not both.")
        if paid == 0 and average_price == 0:
            raise ValueError("Either 'paid' or 'average_price' must be provided.")

        # Calculate missing fields
        if paid == 0 and average_price > 0:
            paid = (buy or sell) * average_price
        elif average_price == 0 and paid > 0:
            average_price = paid / (buy or sell)

        # Final validation
        if paid == 0 or average_price == 0:
            raise ValueError(
                f"Cannot calculate missing data. Invalid values: "
                f"buy={buy}, sell={sell}, paid={paid}, average_price={average_price}."
            )

        # Update values
        values.paid, values.average_price = paid, average_price
        return values


class TransactionSchema(BaseModel):
    coin: CoinInfoSchema
    operation: CoinOperationSchema
