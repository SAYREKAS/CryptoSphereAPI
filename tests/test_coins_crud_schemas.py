import pytest
from pydantic import ValidationError

from api.schemas.coins_crud_schemas import CoinActionSchema
from api.schemas.coins_crud_schemas import TransactionOperationSchema


def test_username_is_stripped_and_lowercase_and_title_and_upper():
    data = CoinActionSchema(username="  TESTUSER   ", coin_name="  bit COIN  ", coin_symbol="  BtC  ")

    assert data.username == "testuser"
    assert data.coin_name == "Bit Coin"
    assert data.coin_symbol == "BTC"


def test_invalid_coin_symbol_raises_validation_error():
    with pytest.raises(ValidationError):
        CoinActionSchema(username="  TESTUSER   ", coin_name="bit COIN", coin_symbol="invalid symbol")


### Tests for `CoinOperationSchema`:
def test_valid_buy_operation_calculates_paid_correctly():
    operation = TransactionOperationSchema(buy=10, average_price=5)
    assert operation.paid == 50
    assert operation.average_price == 5


def test_valid_buy_operation_with_paid_amount():
    operation = TransactionOperationSchema(buy=10, paid=50)
    assert operation.paid == 50
    assert operation.average_price == 5


def test_valid_sell_operation_calculates_paid_correctly():
    operation = TransactionOperationSchema(sell=10, average_price=5)
    assert operation.paid == 50
    assert operation.average_price == 5


def test_valid_sell_operation_with_paid_amount():
    operation = TransactionOperationSchema(sell=10, paid=50)
    assert operation.paid == 50
    assert operation.average_price == 5


def test_missing_price_or_paid_raises_validation_error():
    with pytest.raises(ValidationError, match="Either 'paid' or 'average_price' must be provided."):
        TransactionOperationSchema(buy=10)


def test_both_paid_and_average_price_raises_validation_error():
    with pytest.raises(
        ValidationError, match="There must be only one of 'paid' or 'average_price' provided, not both."
    ):
        TransactionOperationSchema(buy=10, paid=50, average_price=5)


def test_negative_buy_value_raises_error():
    with pytest.raises(ValueError):
        TransactionOperationSchema(buy=-10, paid=50)


def test_negative_sell_value_raises_error():
    with pytest.raises(ValueError):
        TransactionOperationSchema(sell=-5, average_price=5)


def test_negative_fee_value_raises_error():
    with pytest.raises(ValueError):
        TransactionOperationSchema(buy=10, fee=-0.1)


### Tests for integration with `CoinInfoSchema`:
def test_invalid_coin_symbol_raises_validation_error_in_coin_info():
    with pytest.raises(ValidationError):
        CoinActionSchema(username="  TESTUSER   ", coin_name="  bit COIN  ", coin_symbol="bt c")


### Tests for borderline cases:
def test_extreme_large_values_in_operation():
    operation = TransactionOperationSchema(buy=1e9, average_price=1e9)
    assert operation.paid == 1e18


def test_zero_values_in_operation_raises_error():
    with pytest.raises(ValueError):
        TransactionOperationSchema(buy=0, sell=0, average_price=0)


def test_buy_zero_value_is_handled_correctly():
    operation = TransactionOperationSchema(buy=0, sell=10, average_price=5)
    assert operation.paid == 50
    assert operation.average_price == 5
