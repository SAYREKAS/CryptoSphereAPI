import pytest
from fastapi import HTTPException, status

from tests.fixtures import session, new_test_user
from api.schemas import CoinActionSchema, UserCoinsListSchema
from api.crud.coins_crud import add_coin_for_user, get_all_coins_for_user, delete_coin_for_user


@pytest.mark.asyncio
async def test_add_coin_for_user_success(new_test_user, session):
    coin_data = CoinActionSchema(username=new_test_user.username, coin_name="  bitcoin  ", coin_symbol="  BtC  ")
    result = await add_coin_for_user(coin_data, session)

    assert result.coin_name == "Bitcoin"
    assert result.coin_symbol == "BTC"


@pytest.mark.asyncio
async def test_add_coin_for_user_user_not_found(new_test_user, session):
    coin_data = CoinActionSchema(username="nonexistentuser", coin_name="Bitcoin", coin_symbol="BTC")

    with pytest.raises(HTTPException) as exc_info:
        await add_coin_for_user(coin_data, session)

    assert exc_info.value.status_code == 404
    assert "User 'nonexistentuser' not found." in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_add_coin_for_user_integrity_error(new_test_user, session):
    coin_data = CoinActionSchema(username=new_test_user.username, coin_name="Bitcoin", coin_symbol="BTC")

    # Insert the coin once
    await add_coin_for_user(coin_data, session)

    # Try adding the same coin again
    with pytest.raises(HTTPException) as exc_info:
        await add_coin_for_user(coin_data, session)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Coin data is invalid or already exists." in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_get_all_coins_for_user_success(new_test_user, session):

    coin_data1 = CoinActionSchema(username=new_test_user.username, coin_name="Bitcoin", coin_symbol="BTC")
    coin_data2 = CoinActionSchema(username=new_test_user.username, coin_name="Ethereum", coin_symbol="ETH")

    # Add coins
    await add_coin_for_user(coin_data1, session)
    await add_coin_for_user(coin_data2, session)

    result = await get_all_coins_for_user(username=new_test_user.username, session=session)

    assert isinstance(result, UserCoinsListSchema)
    assert len(result.coins) == 2

    assert result.coins[0].coin_name == "Bitcoin"
    assert result.coins[0].coin_symbol == "BTC"

    assert result.coins[1].coin_name == "Ethereum"
    assert result.coins[1].coin_symbol == "ETH"


@pytest.mark.asyncio
async def test_get_all_coins_for_user_no_coins(new_test_user, session):

    result = await get_all_coins_for_user(username=new_test_user.username, session=session)

    assert isinstance(result, UserCoinsListSchema)
    assert len(result.coins) == 0


@pytest.mark.asyncio
async def test_get_all_coins_for_user_user_not_found(new_test_user, session):
    result = await get_all_coins_for_user("nonexistentuser", session)

    assert isinstance(result, UserCoinsListSchema)
    assert len(result.coins) == 0


@pytest.mark.asyncio
async def test_delete_coin_for_user_success(new_test_user, session):
    coin_data = CoinActionSchema(username=new_test_user.username, coin_name="Bitcoin", coin_symbol="BTC")

    # Add a coin
    await add_coin_for_user(coin_data, session)

    # Delete the coin
    result = await delete_coin_for_user(coin_data, session)

    assert result.coin_name == "Bitcoin"
    assert result.coin_symbol == "BTC"


@pytest.mark.asyncio
async def test_delete_coin_for_user_coin_not_found(new_test_user, session):

    coin_data = CoinActionSchema(username=new_test_user.username, coin_name="Bitcoin", coin_symbol="BTC")

    # Try deleting a non-existent coin
    with pytest.raises(HTTPException) as exc_info:
        await delete_coin_for_user(coin_data, session)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Coin 'Bitcoin' (BTC) not found for user 'testuser'." in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_delete_coin_for_user_user_not_found(session):
    coin_data = CoinActionSchema(username="nonexistentuser", coin_name="Bitcoin", coin_symbol="BTC")

    with pytest.raises(HTTPException) as exc_info:
        await delete_coin_for_user(coin_data, session)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Coin 'Bitcoin' (BTC) not found for user 'nonexistentuser'." in str(exc_info.value.detail)