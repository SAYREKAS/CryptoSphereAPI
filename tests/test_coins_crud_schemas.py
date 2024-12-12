import pytest
from api.schemas.coins_crud_schemas import UserCoinsSchema
from api.schemas.coins_crud_schemas import CommonFieldsValidator, CoinInfoSchema, CoinOperationSchema


def test_common_fields_username_lowercase():
    data = CommonFieldsValidator(username="TESTUSER")
    assert data.username == "testuser"


def test_common_fields_username_strip():
    data = CommonFieldsValidator(username="  user123  ")
    assert data.username == "user123"


def test_common_fields_coin_name_titlecase():
    data = CommonFieldsValidator(name="  bit coin  ")
    assert data.name == "Bit Coin"


def test_common_fields_coin_symbol_uppercase():
    data = CommonFieldsValidator(symbol=" btc ")
    assert data.symbol == "BTC"


def test_common_fields_coin_symbol_invalid():
    with pytest.raises(ValueError):
        CommonFieldsValidator(symbol="invalid symbol")


### Tests for `CoinOperationSchema`:
def test_operation_valid_buy_and_price():
    operation = CoinOperationSchema(buy=10, average_price=5)
    assert operation.paid == 50
    assert operation.average_price == 5


def test_operation_valid_sell_and_price():
    operation = CoinOperationSchema(sell=10, average_price=5)
    assert operation.paid == 50
    assert operation.average_price == 5


def test_operation_valid_buy_and_paid():
    operation = CoinOperationSchema(buy=10, paid=50)
    assert operation.average_price == 5
    assert operation.paid == 50


def test_operation_missing_price_and_paid():
    with pytest.raises(ValueError, match="Either 'paid' or 'average_price' must be provided."):
        CoinOperationSchema(buy=10)


def test_operation_both_price_and_paid():
    with pytest.raises(ValueError, match="There must be only one of 'paid' or 'average_price' provided, not both."):
        CoinOperationSchema(buy=10, paid=50, average_price=5)


def test_operation_invalid_buy_negative():
    with pytest.raises(ValueError):
        CoinOperationSchema(buy=-10, paid=50)


def test_operation_invalid_sell_negative():
    with pytest.raises(ValueError):
        CoinOperationSchema(sell=-5, average_price=5)


def test_operation_invalid_fee_negative():
    with pytest.raises(ValueError):
        CoinOperationSchema(buy=10, fee=-0.1)


### Tests for integration with `CoinInfoSchema`:
def test_coin_info_schema_valid_data():
    coin_info = CoinInfoSchema(username="TestUser", name="bitcoin", symbol="btc")
    assert coin_info.username == "testuser"
    assert coin_info.name == "Bitcoin"
    assert coin_info.symbol == "BTC"


def test_coin_info_schema_invalid_symbol():
    with pytest.raises(ValueError):
        CoinInfoSchema(symbol="bt c")


### Tests for borderline cases:
def test_operation_extreme_large_values():
    operation = CoinOperationSchema(buy=1e9, average_price=1e9)
    assert operation.paid == 1e18


def test_operation_zero_values():
    with pytest.raises(ValueError):
        CoinOperationSchema(buy=0, sell=0, average_price=0)


def test_operation_edge_case_buy_zero():
    operation = CoinOperationSchema(buy=0, sell=10, average_price=5)
    assert operation.paid == 50
    assert operation.average_price == 5


### Tests on collections (eg `UserCoinsSchema`):
def test_user_coins_schema_valid():
    user_coins = UserCoinsSchema(
        coins=[
            CoinInfoSchema(username="testuser", name="bitcoin", symbol="btc"),
            CoinInfoSchema(username="anotheruser", name="ethereum", symbol="eth"),
        ]
    )
    assert len(user_coins.coins) == 2
    assert user_coins.coins[0].symbol == "BTC"
    assert user_coins.coins[1].symbol == "ETH"


def test_user_coins_schema_invalid_coin_symbol():
    with pytest.raises(ValueError):
        UserCoinsSchema(coins=[CoinInfoSchema(username="user", name="bitcoin", symbol="bt c")])
