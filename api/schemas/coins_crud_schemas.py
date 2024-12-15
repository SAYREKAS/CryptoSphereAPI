__all__ = [
    "CoinInfoSchema",
    "UserCoinsListSchema",
    "CoinActionSchema",
    "OperationSchema",
]

from pydantic import BaseModel, field_validator, model_validator


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
    buy: float = 0.0
    sell: float = 0.0
    paid: float = 0.0
    average_price: float = 0.0
    fee: float = 0.0

    @model_validator(mode="after")
    def validate_paid_or_average_price(cls, values) -> dict:
        """Validates and calculates missing values for paid and average_price based on buy and sell."""

        buy, sell, paid, average_price, fee = values.buy, values.sell, values.paid, values.average_price, values.fee

        if buy <= 0 and sell <= 0:
            raise ValueError("Cannot calculate missing data. Both 'buy' and 'sell' are zero or negative.")

        if paid > 0 and average_price > 0:
            raise ValueError("There must be only one of 'paid' or 'average_price' provided, not both.")

        if paid == 0 and average_price == 0:
            raise ValueError("Either 'paid' or 'average_price' must be provided.")

        if fee < 0:
            raise ValueError("Fee must be greater than or equal to 0.")

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

        if fee > 0:
            paid = paid + fee

        # Update values
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
