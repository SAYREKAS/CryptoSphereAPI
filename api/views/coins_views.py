"""Implementation of endpoints for working with coins in the user's portfolio"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.db_helper import db_helper
from api.schemas.crud_coins_schemas import UserCoinActionSchema, CoinInfoSchema, UserCoinsSchema
from api.crud.coins_crud import add_coin_for_user, get_all_coins_for_user, delete_coin_for_user

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=CoinInfoSchema)
async def add_coin_for_user_endpoint(
    coin_data: UserCoinActionSchema,
    session: AsyncSession = Depends(db_helper.session_getter),
) -> CoinInfoSchema:
    """Endpoint for adding a new user's coin"""
    return await add_coin_for_user(coin_data=coin_data, session=session)


@router.get("/", status_code=status.HTTP_200_OK, response_model=UserCoinsSchema)
async def get_all_coins_for_user_endpoint(
    username: str,
    session: AsyncSession = Depends(db_helper.session_getter),
) -> UserCoinsSchema:
    """Endpoint for getting all user's coins"""
    return await get_all_coins_for_user(username=username, session=session)


@router.delete("/", status_code=status.HTTP_200_OK, response_model=CoinInfoSchema)
async def delete_coin_for_user_endpoint(
    coin_data: UserCoinActionSchema,
    session: AsyncSession = Depends(db_helper.session_getter),
) -> CoinInfoSchema:
    """Endpoint for deleting a user's coin"""
    return await delete_coin_for_user(coin_data=coin_data, session=session)
