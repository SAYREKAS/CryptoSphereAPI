import pytest
from pydantic import ValidationError
from api.schemas import OperationSchema, CoinActionSchema, UserCoinsListSchema, CoinInfoSchema


class TestCoinInfoSchema:
    """Test cases for CoinInfoSchema"""

    def test_valid_data(self):
        schema = CoinInfoSchema(coin_name=" bitcoin ", coin_symbol=" btc ")
        assert schema.coin_name == "Bitcoin"
        assert schema.coin_symbol == "BTC"

    def test_empty_coin_name(self):
        with pytest.raises(ValidationError):
            CoinInfoSchema(coin_name="", coin_symbol="BTC")

    def test_empty_coin_symbol(self):
        with pytest.raises(ValidationError):
            CoinInfoSchema(coin_name="Bitcoin", coin_symbol="")

    def test_coin_symbol_with_spaces(self):
        with pytest.raises(ValidationError):
            CoinInfoSchema(coin_name="Bitcoin", coin_symbol="B T C")

    def test_invalid_coin_name(self):
        with pytest.raises(ValidationError):
            CoinInfoSchema(coin_name="   ", coin_symbol="BTC")

    def test_coin_symbol_with_extra_spaces(self):
        schema = CoinInfoSchema(coin_name="Bitcoin", coin_symbol=" btc ")
        assert schema.coin_symbol == "BTC"

    def test_coin_name_with_extra_spaces(self):
        schema = CoinInfoSchema(coin_name="   bitcoin  ", coin_symbol="BTC")
        assert schema.coin_name == "Bitcoin"

    def test_uppercase_coin_symbol(self):
        schema = CoinInfoSchema(coin_name="Bitcoin", coin_symbol="btc")
        assert schema.coin_symbol == "BTC"

    def test_title_case_coin_name(self):
        schema = CoinInfoSchema(coin_name=" bitCOIN ", coin_symbol="BTC")
        assert schema.coin_name == "Bitcoin"

    def test_coin_name_and_symbol_are_valid(self):
        schema = CoinInfoSchema(coin_name="Ethereum", coin_symbol="ETH")
        assert schema.coin_name == "Ethereum"
        assert schema.coin_symbol == "ETH"


class TestUserCoinsListSchema:
    """Test cases for CoinsListSchema."""

    def test_valid_data(self):
        schema = UserCoinsListSchema(
            coins=[
                CoinInfoSchema(coin_name="Bitcoin", coin_symbol="BTC"),
                CoinInfoSchema(coin_name="Ethereum", coin_symbol="ETH"),
            ]
        )
        assert len(schema.coins) == 2
        assert schema.coins[0].coin_name == "Bitcoin"
        assert schema.coins[0].coin_symbol == "BTC"
        assert schema.coins[1].coin_name == "Ethereum"
        assert schema.coins[1].coin_symbol == "ETH"

    def test_empty_coins_list(self):
        schema = UserCoinsListSchema(coins=[])
        assert len(schema.coins) == 0

    def test_invalid_coin_schema(self):
        with pytest.raises(ValidationError):
            UserCoinsListSchema(
                coins=[
                    {"coin_name": "Bitcoin", "coin_symbol": "BTC"},
                    {"coin_name": "Ethereum"},  # Missing required "coin_symbol"
                ]
            )

    def test_non_list_input(self):
        with pytest.raises(ValidationError):
            UserCoinsListSchema(coins="not_a_list")

    def test_list_with_invalid_elements(self):
        with pytest.raises(ValidationError):
            UserCoinsListSchema(
                coins=[
                    CoinInfoSchema(coin_name="Bitcoin", coin_symbol="BTC"),
                    "invalid_element",  # Not a valid CoinInfoSchema
                ]
            )

    def test_partial_invalid_list(self):
        with pytest.raises(ValidationError):
            UserCoinsListSchema(
                coins=[
                    {"coin_name": "Bitcoin", "coin_symbol": "BTC"},
                    {"coin_name": "InvalidCoin"},  # Missing coin_symbol
                ]
            )

    def test_extra_fields_in_coin(self):
        schema = UserCoinsListSchema(
            coins=[
                {"coin_name": "Bitcoin", "coin_symbol": "BTC", "extra_field": "ignored"},
                {"coin_name": "Ethereum", "coin_symbol": "ETH"},
            ]
        )
        assert len(schema.coins) == 2
        assert schema.coins[0].coin_name == "Bitcoin"
        assert schema.coins[0].coin_symbol == "BTC"
        assert schema.coins[1].coin_name == "Ethereum"
        assert schema.coins[1].coin_symbol == "ETH"

    def test_nested_schema_validation(self):
        with pytest.raises(ValidationError):
            UserCoinsListSchema(coins=[{"coin_name": "Bitcoin", "coin_symbol": "B T C"}])  # Invalid symbol


class TestCoinActionSchema:
    """Test cases for CoinActionSchema."""

    def test_valid_data(self):
        schema = CoinActionSchema(username="TestUser ", coin_name=" bitcoin ", coin_symbol=" btc ")
        assert schema.username == "testuser"
        assert schema.coin_name == "Bitcoin"
        assert schema.coin_symbol == "BTC"

    def test_invalid_username_empty(self):
        with pytest.raises(ValidationError):
            CoinActionSchema(username="   ", coin_name="Bitcoin", coin_symbol="BTC")

    def test_invalid_coin_name_empty(self):
        with pytest.raises(ValidationError):
            CoinActionSchema(username="testuser", coin_name="   ", coin_symbol="BTC")

    def test_invalid_coin_symbol_empty(self):
        with pytest.raises(ValidationError):
            CoinActionSchema(username="testuser", coin_name="Bitcoin", coin_symbol="   ")

    def test_invalid_coin_symbol_spaces(self):
        with pytest.raises(ValidationError):
            CoinActionSchema(username="testuser", coin_name="Bitcoin", coin_symbol="BTC ETH")

    def test_username_trimming_and_lowercase(self):
        schema = CoinActionSchema(username="  TestUser ", coin_name="Bitcoin", coin_symbol="BTC")
        assert schema.username == "testuser"

    def test_coin_name_trimming_and_title_case(self):
        schema = CoinActionSchema(username="testuser", coin_name="  bitCOin ", coin_symbol="BTC")
        assert schema.coin_name == "Bitcoin"

    def test_coin_symbol_trimming_and_uppercase(self):
        schema = CoinActionSchema(username="testuser", coin_name="Bitcoin", coin_symbol="  btc ")
        assert schema.coin_symbol == "BTC"


class TestOperationSchema:
    """Test cases for OperationSchema."""

    def test_valid_buy_and_average_price(self):
        schema = OperationSchema(
            username="  testuser  ", coin_name="  bitcoin  ", coin_symbol="  btc  ", buy=10, average_price=5
        )
        assert schema.username == "testuser"
        assert schema.coin_name == "Bitcoin"
        assert schema.coin_symbol == "BTC"
        assert schema.paid == 50
        assert schema.average_price == 5

    def test_valid_buy_and_paid(self):
        schema = OperationSchema(username="user", coin_name="Bitcoin", coin_symbol="BTC", buy=10, paid=50)
        assert schema.paid == 50
        assert schema.average_price == 5

    def test_valid_sell_and_average_price(self):
        schema = OperationSchema(username="user", coin_name="Bitcoin", coin_symbol="BTC", sell=10, average_price=5)
        assert schema.paid == 50
        assert schema.average_price == 5

    def test_valid_sell_and_paid(self):
        schema = OperationSchema(username="user", coin_name="Bitcoin", coin_symbol="BTC", sell=10, paid=50)
        assert schema.paid == 50
        assert schema.average_price == 5

    def test_missing_price_and_paid(self):
        with pytest.raises(ValidationError):
            OperationSchema(username="user", coin_name="Bitcoin", coin_symbol="BTC", buy=10)

    def test_both_price_and_paid(self):
        with pytest.raises(
            ValidationError, match="There must be only one of 'paid' or 'average_price' provided, not both."
        ):
            OperationSchema(username="user", coin_name="Bitcoin", coin_symbol="BTC", buy=10, paid=50, average_price=5)

    def test_invalid_username_format(self):
        schema = OperationSchema(
            username="  TestUSER  ", coin_name="Bitcoin", coin_symbol="BTC", buy=10, average_price=5
        )
        assert schema.username == "testuser"

    def test_invalid_coin_name_format(self):
        schema = OperationSchema(username="user", coin_name="  bit COIN  ", coin_symbol="BTC", buy=10, average_price=5)
        assert schema.coin_name == "Bit Coin"

    def test_invalid_coin_symbol_format(self):
        schema = OperationSchema(username="user", coin_name="Bitcoin", coin_symbol="  btc  ", buy=10, average_price=5)
        assert schema.coin_symbol == "BTC"

    def test_coin_symbol_invalid_multiple_words(self):
        with pytest.raises(ValidationError):
            OperationSchema(username="user", coin_name="Bitcoin", coin_symbol="bt c", buy=10, average_price=5)

    def test_negative_buy_value(self):
        with pytest.raises(
            ValidationError, match="Cannot calculate missing data. Both 'buy' and 'sell' are zero or negative."
        ):
            OperationSchema(username="user", coin_name="Bitcoin", coin_symbol="BTC", buy=-10, average_price=5)

    def test_negative_sell_value(self):
        with pytest.raises(
            ValidationError, match="Cannot calculate missing data. Both 'buy' and 'sell' are zero or negative."
        ):
            OperationSchema(username="user", coin_name="Bitcoin", coin_symbol="BTC", sell=-5, average_price=5)

    def test_negative_fee_value(self):
        with pytest.raises(ValidationError):
            OperationSchema(username="user", coin_name="Bitcoin", coin_symbol="BTC", buy=10, average_price=5, fee=-0.1)

    def test_calculated_paid_from_average_price(self):
        schema = OperationSchema(username="user", coin_name="Bitcoin", coin_symbol="BTC", buy=10, average_price=5)
        assert schema.paid == 50

    def test_calculated_average_price_from_paid(self):
        schema = OperationSchema(username="user", coin_name="Bitcoin", coin_symbol="BTC", buy=10, paid=50)
        assert schema.average_price == 5

    def test_extreme_large_values(self):
        schema = OperationSchema(username="user", coin_name="Bitcoin", coin_symbol="BTC", buy=1e9, average_price=1e9)
        assert schema.paid == 1e18
        assert schema.average_price == 1e9

    def test_zero_buy_and_sell(self):
        with pytest.raises(ValidationError):
            OperationSchema(username="user", coin_name="Bitcoin", coin_symbol="BTC", buy=0, sell=0, paid=50)

    def test_zero_paid_and_average_price(self):
        with pytest.raises(ValidationError):
            OperationSchema(username="user", coin_name="Bitcoin", coin_symbol="BTC", buy=10)

    def test_calculation_with_sell_instead_of_buy(self):
        schema = OperationSchema(username="user", coin_name="Bitcoin", coin_symbol="BTC", sell=5, average_price=10)
        assert schema.paid == 50
        assert schema.average_price == 10

    def test_fee_included_in_paid_calculation(self):
        schema = OperationSchema(
            username="user", coin_name="Bitcoin", coin_symbol="BTC", buy=10, average_price=5, fee=1
        )
        assert schema.paid == 51  # 10 * 5 + 1
        assert schema.average_price == 5
        assert schema.fee == 1

    def test_no_fee_in_paid_calculation(self):
        schema = OperationSchema(username="user", coin_name="Bitcoin", coin_symbol="BTC", buy=10, average_price=5)
        assert schema.paid == 50  # 10 * 5
        assert schema.fee == 0
