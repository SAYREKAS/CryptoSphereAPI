"""
Module for managing user coin data: adding, retrieving, and deleting user coins.
"""

from loguru import logger
from sqlalchemy import select, delete
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.models import UsersORM, CoinsORM
from api.schemas.coins_crud_schemas import CoinActionSchema, UserCoinsResponseSchema, CoinInfoResponseSchema


async def add_coin_for_user(coin_data: CoinActionSchema, session: AsyncSession) -> CoinInfoResponseSchema:
    """Add a new coin for a user identified by a username."""

    try:
        query = await session.execute(select(UsersORM.id).where(UsersORM.username == coin_data.username))

        user_id = query.scalar_one_or_none()
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User '{coin_data.username}' not found.",
            )

        new_coin = CoinsORM(user_id=user_id, name=coin_data.coin_name, symbol=coin_data.coin_symbol)
        session.add(new_coin)
        await session.commit()

        logger.info(
            f"Coin '{new_coin.name}' ({new_coin.symbol}) successfully added for user '{coin_data.username}'.",
        )
        return CoinInfoResponseSchema(
            coin_name=new_coin.name,
            coin_symbol=new_coin.symbol,
        )

    except IntegrityError as e:
        logger.warning(
            f"Integrity error while adding coin '{coin_data.coin_name}' for user '{coin_data.username}': {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coin data is invalid or already exists.",
        )

    except HTTPException:
        logger.warning(f"Attempted to add a coin for non-existent user '{coin_data.username}'.")
        raise

    except Exception as e:
        logger.error(f"Unexpected error while adding coin '{coin_data.coin_name}' for user '{coin_data.username}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while adding the coin.",
        )


async def get_all_coins_for_user(username: str, session: AsyncSession) -> UserCoinsResponseSchema:
    """Retrieve all coins for a user identified by a username."""

    try:
        coins_query = await session.execute(
            select(CoinsORM).join(UsersORM, UsersORM.id == CoinsORM.user_id).where(UsersORM.username == username)
        )

        all_coins = coins_query.scalars().all()
        if not all_coins:
            logger.warning(f"Attempted to get all coins for user '{username}', but no coins were found.")
            return UserCoinsResponseSchema(coins=[])

        logger.info(f"Retrieved {len(all_coins)} coins for user '{username}'.")
        return UserCoinsResponseSchema(
            coins=[CoinInfoResponseSchema(coin_name=coin.name, coin_symbol=coin.symbol) for coin in all_coins]
        )

    except Exception as e:
        logger.error(f"Error retrieving coins for user '{username}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error occurred while retrieving coins for user '{username}': {str(e)}",
        )


async def delete_coin_for_user(coin_data: CoinActionSchema, session: AsyncSession) -> CoinInfoResponseSchema:
    """Remove a user's coin from the database."""

    try:
        user_id_subquery = select(UsersORM.id).where(UsersORM.username == coin_data.username).scalar_subquery()

        result = await session.execute(
            delete(CoinsORM).where(
                CoinsORM.user_id == user_id_subquery,
                CoinsORM.name == coin_data.coin_name,
                CoinsORM.symbol == coin_data.coin_symbol,
            )
        )
        if result.rowcount == 0:
            logger.warning(
                f"Attempted to delete non-existent coin '{coin_data.coin_name}' ({coin_data.coin_symbol}) for user '{coin_data.username}'."
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Coin '{coin_data.coin_name}' ({coin_data.coin_symbol}) not found for user '{coin_data.username}'.",
            )

        await session.commit()

        logger.info(
            f"Coin '{coin_data.coin_name}' ({coin_data.coin_symbol}) successfully deleted for user '{coin_data.username}'."
        )
        return CoinInfoResponseSchema(
            coin_name=coin_data.coin_name,
            coin_symbol=coin_data.coin_symbol,
        )

    except IntegrityError as e:
        logger.error(
            f"Integrity error while deleting coin '{coin_data.coin_name}' for user '{coin_data.username}': {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Integrity error while deleting coin '{coin_data.coin_name}' for user '{coin_data.username}': {str(e)}",
        )
    except HTTPException:
        raise

    except Exception as e:
        logger.error(
            f"Unexpected error while deleting coin '{coin_data.coin_name}' for user '{coin_data.username}': {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error occurred while deleting coin '{coin_data.coin_name}' for user '{coin_data.username}': {str(e)}",
        )
