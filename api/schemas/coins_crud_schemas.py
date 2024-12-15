__all__ = [
    "CoinInfoSchema",
    "UserCoinsListSchema",
    "CoinActionSchema",
    "OperationSchema",
]

from pydantic import BaseModel, field_validator, model_validator, Field


class UsernameFieldValidator(BaseModel):
    username: str

    @field_validator("username", mode="after")
    def validate_username(cls, value: str) -> str:
        """Validates the username according to specific rules."""
        value = value.strip().lower()

        if not value:
            raise ValueError("Invalid username")

        return value


class CoinInfoFieldsValidator(BaseModel):
    coin_name: str
    coin_symbol: str

    @field_validator("coin_name", mode="after")
    def coin_name_validator(cls, value: str) -> str:
        """Validate coin name."""
        value = value.strip().title()

        if not value:
            raise ValueError("Invalid coin_name")

        return value

    @field_validator("coin_symbol", mode="after")
    def coin_symbol_validator(cls, value: str) -> str:
        """Validate coin symbol."""
        if len(value.split()) > 1:
            raise ValueError("Invalid coin symbol")

        value = value.strip().upper()

        if not value:
            raise ValueError("Invalid coin_symbol")

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
            raise ValueError("Only one of 'buy' or 'sell' can be greater than zero.")

        if buy == 0 and sell == 0:
            raise ValueError("Either 'buy' or 'sell' must be greater than zero.")

        if paid == 0 and average_price == 0:
            if fee == 0 and (buy > 0 or sell > 0):
                return values
            raise ValueError("Either 'paid' or 'average_price' must be set unless the transaction is free (fee=0).")

        if paid > 0 and average_price > 0:
            raise ValueError("Both 'paid' and 'average_price' cannot be set at the same time.")

        if paid == 0 and average_price > 0:
            total_units = buy if buy > 0 else sell
            paid = total_units * average_price - fee

            if paid < 0:
                paid = 0

        elif average_price == 0 and paid > 0:
            total_units = buy if buy > 0 else sell
            if total_units == 0:
                raise ValueError("Cannot calculate 'average_price' with zero units (buy or sell).")
            average_price = (paid + fee) / total_units

        values.paid, values.average_price = paid, average_price
        return values


class CoinInfoSchema(CoinInfoFieldsValidator):
    pass


class UserCoinsListSchema(BaseModel):
    coins: list[CoinInfoSchema]


class CoinActionSchema(UsernameFieldValidator, CoinInfoFieldsValidator):
    pass


class OperationSchema(CoinActionSchema, OperationFieldsValidator):
    pass
