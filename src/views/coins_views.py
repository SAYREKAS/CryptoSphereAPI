"""Implementation of endpoints for working with coins in the user's portfolio"""

from fastapi import APIRouter

from src.schemas.crud_coin_schemas import NewUserCoinSchema, CoinInfoSchema, AllUserCoinsSchema
from src.database.crud.crud_coin import add_coin_for_user, get_all_coins_for_user, delete_coin_for_user

router = APIRouter()


@router.post("/")
async def add_coin_for_user_endpoint(coin_data: NewUserCoinSchema) -> CoinInfoSchema:
    """Endpoint for adding a new user's coin"""
    return await add_coin_for_user(coin_data=coin_data)


@router.get("/")
async def get_all_coins_for_user_endpoint(username: str) -> AllUserCoinsSchema:
    """Endpoint for getting all user's coins"""
    return await get_all_coins_for_user(username=username)


@router.delete("/")
async def delete_coin_for_user_endpoint(coin_data: NewUserCoinSchema) -> CoinInfoSchema:
    """Endpoint for deleting a user's coin"""
    return await delete_coin_for_user(coin_data=coin_data)
