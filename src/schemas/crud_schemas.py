from pydantic import BaseModel


class CoinBasicInfoSchema(BaseModel):
    name: str
    symbol: str
