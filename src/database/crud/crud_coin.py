"""CRUD database operations"""

import sqlalchemy
from loguru import logger

from src.database.config import async_session
from src.database.models import UsersORM, CoinsORM
from src.schemas.crud_coin_schemas import NewUserCoinSchema


async def add_coin_for_user(coin_data: NewUserCoinSchema):
    """Add a new coin for a user identified by a username."""

    async with async_session() as session:
        try:
            result_query = await session.execute(
                sqlalchemy.select(UsersORM.id).where(UsersORM.username == coin_data.username)
            )

            user_id = result_query.scalar_one_or_none()
            if not user_id:
                logger.warning(f"Attempted to add a coin for non-existent user '{coin_data.username}'.")

            coin_query = CoinsORM(user_id=user_id, name=coin_data.coin_name, symbol=coin_data.coin_symbol)
            session.add(coin_query)
            await session.commit()

            logger.info(
                f"Coin '{coin_data.coin_name}' ({coin_data.coin_symbol}) successfully added for user '{coin_data.username}'."
            )
        except sqlalchemy.exc.IntegrityError as e:
            logger.error(
                f"Integrity error while adding coin '{coin_data.coin_name}' for user '{coin_data.username}': {e}"
            )


async def get_all_coins_for_user(username: str):
    """Retrieve all coins for a user identified by a username."""

    async with async_session() as session:
        try:
            coins_query = await session.execute(
                sqlalchemy.select(CoinsORM)
                .join(UsersORM, UsersORM.id == CoinsORM.user_id)
                .where(UsersORM.username == username)
            )
            all_coins = coins_query.scalars().all()
            if not all_coins:
                logger.warning(f"Attempted to get all coins for user '{username}', but no coins were found.")
                return []

            logger.info(f"Retrieved {len(all_coins)} coins for user '{username}'.")

        except Exception as e:
            logger.error(f"Error retrieving coins for user '{username}': {e}")
            return []


async def delete_coin_for_user(coin_data: NewUserCoinSchema):
    """Remove a user's coin from the database."""

    async with async_session() as session:
        try:
            result = await session.execute(
                sqlalchemy.delete(CoinsORM).where(
                    CoinsORM.user_id == sqlalchemy.select(UsersORM.id).where(UsersORM.username == coin_data.username),
                    CoinsORM.name == coin_data.coin_name,
                    CoinsORM.symbol == coin_data.coin_symbol,
                )
            )
            if result.rowcount == 0:
                logger.warning(
                    f"Coin '{coin_data.coin_name}' ({coin_data.coin_symbol}) not found for user '{coin_data.username}'."
                )
            await session.commit()

            logger.info(
                f"Coin '{coin_data.coin_name}' ({coin_data.coin_symbol}) successfully deleted for user '{coin_data.username}'."
            )
        except sqlalchemy.exc.IntegrityError as e:
            logger.error(
                f"Integrity error while deleting coin '{coin_data.coin_name}' for user '{coin_data.username}': {e}"
            )
