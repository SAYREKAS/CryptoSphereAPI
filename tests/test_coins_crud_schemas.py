import pytest
from pydantic import ValidationError
from api.schemas import OperationSchema, CoinActionSchema, UserCoinsListSchema, CoinInfoSchema
from api.schemas.coins_crud_schemas import UsernameFieldValidator, CoinInfoFieldsValidator, OperationFieldsValidator


class TestUsernameFieldValidator:
    def test_valid_username(self):
        schema = UsernameFieldValidator(username="validUser123")
        assert schema.username == "validuser123"

    def test_empty_username(self):
        with pytest.raises(ValidationError):
            UsernameFieldValidator(username="  ")

    def test_username_strip_and_lower(self):
        schema = UsernameFieldValidator(username="  User_Name  ")
        assert schema.username == "user_name"


class TestCoinInfoFieldsValidator:
    def test_valid_coin_name_and_symbol(self):
        schema = CoinInfoFieldsValidator(coin_name="Bitcoin", coin_symbol="BTC")
        assert schema.coin_name == "Bitcoin"
        assert schema.coin_symbol == "BTC"

    def test_invalid_coin_name(self):
        with pytest.raises(ValidationError):
            CoinInfoFieldsValidator(coin_name="  ", coin_symbol="BTC")

    def test_invalid_coin_symbol(self):
        with pytest.raises(ValidationError):
            CoinInfoFieldsValidator(coin_name="Bitcoin", coin_symbol="B TC")

    def test_coin_symbol_strip_and_upper(self):
        schema = CoinInfoFieldsValidator(coin_name="bitcoin", coin_symbol="  btc  ")
        assert schema.coin_symbol == "BTC"


class TestOperationFieldsValidator:
    def test_valid_buy_with_paid(self):
        schema = OperationFieldsValidator(buy=100, paid=2000)
        assert schema.average_price == 20  # average_price = paid / buy
        assert schema.paid == 2000

    def test_valid_sell_with_paid(self):
        schema = OperationFieldsValidator(sell=50, paid=1000)
        assert schema.average_price == 20  # average_price = paid / sell
        assert schema.paid == 1000

    def test_valid_buy_with_average_price(self):
        schema = OperationFieldsValidator(buy=100, average_price=25)
        assert schema.paid == 2500  # paid = buy * average_price
        assert schema.average_price == 25

    def test_valid_sell_with_average_price(self):
        schema = OperationFieldsValidator(sell=50, average_price=30)
        assert schema.paid == 1500  # paid = sell * average_price
        assert schema.average_price == 30

    def test_valid_buy_with_paid_and_fee(self):
        schema = OperationFieldsValidator(buy=100, paid=2000, fee=20)
        assert schema.average_price == 20.2  # average_price = (paid + fee) / buy
        assert schema.paid == 2000

    def test_valid_sell_with_paid_and_fee(self):
        schema = OperationFieldsValidator(sell=100, paid=2000, fee=20)
        assert schema.average_price == 20.2  # average_price = (paid + fee) / sell
        assert schema.paid == 2000

    def test_valid_buy_with_average_price_and_fee(self):
        schema = OperationFieldsValidator(buy=100, average_price=20.2, fee=20)
        assert schema.paid == 2000  # paid = buy * average_price - fee
        assert schema.average_price == 20.2

    def test_valid_sell_with_average_price_and_fee(self):
        schema = OperationFieldsValidator(sell=100, average_price=20.2, fee=20)
        assert schema.paid == 2000  # paid = sell * average_price - fee
        assert schema.average_price == 20.2

    def test_free_buy_transaction(self):
        schema = OperationFieldsValidator(buy=100, paid=0, average_price=0, fee=0)
        assert schema.paid == 0
        assert schema.average_price == 0

    def test_free_sell_transaction(self):
        schema = OperationFieldsValidator(sell=100, paid=0, average_price=0, fee=0)
        assert schema.paid == 0
        assert schema.average_price == 0

    def test_invalid_both_buy_and_sell_set(self):
        with pytest.raises(ValidationError):
            OperationFieldsValidator(buy=100, sell=50, paid=2000)

    def test_invalid_both_paid_and_average_price_set(self):
        with pytest.raises(ValidationError):
            OperationFieldsValidator(buy=100, paid=2000, average_price=20)

    def test_invalid_no_buy_or_sell(self):
        with pytest.raises(ValidationError):
            OperationFieldsValidator(paid=2000, average_price=20)

    def test_invalid_negative_values(self):
        with pytest.raises(ValidationError):
            OperationFieldsValidator(buy=-100, paid=2000)

        with pytest.raises(ValidationError):
            OperationFieldsValidator(sell=-50, average_price=20)

        with pytest.raises(ValidationError):
            OperationFieldsValidator(buy=100, paid=-2000)

        with pytest.raises(ValidationError):
            OperationFieldsValidator(sell=50, average_price=-20)

        with pytest.raises(ValidationError):
            OperationFieldsValidator(buy=100, fee=-5)

    def test_invalid_free_transaction_with_fee(self):
        with pytest.raises(ValidationError):
            OperationFieldsValidator(buy=100, paid=0, average_price=0, fee=10)

        with pytest.raises(ValidationError):
            OperationFieldsValidator(sell=50, paid=0, average_price=0, fee=5)

    def test_invalid_calculated_average_price_division_by_zero(self):
        with pytest.raises(ValidationError):
            OperationFieldsValidator(paid=2000, buy=0, sell=0)
