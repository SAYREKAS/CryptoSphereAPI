from pydantic import BaseModel, field_validator

from src.schemas.common_schemas import ActionResult


class NewUserCoinSchema(BaseModel):
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

        value = value.capitalize().strip()
        return value

    @field_validator("coin_symbol", mode="after")
    def coin_symbol_validator(cls, value: str):
        """validate coin symbol"""

        value = value.strip().upper()
        return value


class CoinInfoSchema(ActionResult):
    coin_name: str
    coin_symbol: str


class AllUserCoinsSchema(BaseModel):
    coins: list[str]
