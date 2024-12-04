"""CRUD database operations"""

import sqlalchemy
from loguru import logger

from src.database.config import async_session
from src.database.models import UsersORM, CoinsORM
from src.schemas.crud_coins_schemas import UserActionCoinSchema, ActionCoinSchema, UserCoinsSchema, CoinSchema


async def add_coin_for_user(coin_data: UserActionCoinSchema) -> ActionCoinSchema:
    """Add a new coin for a user identified by a username."""

    async with async_session() as session:
        try:
            result_query = await session.execute(
                sqlalchemy.select(UsersORM.id).where(UsersORM.username == coin_data.username)
            )

            user_id = result_query.scalar_one_or_none()
            if not user_id:
                logger.warning(f"Attempted to add a coin for non-existent user '{coin_data.username}'.")

                return ActionCoinSchema(
                    success=False,
                    message=f"User '{coin_data.username}' does not exist. Please check the username and try again.",
                    coin_name=coin_data.coin_name,
                    coin_symbol=coin_data.coin_symbol,
                )

            coin_query = CoinsORM(user_id=user_id, name=coin_data.coin_name, symbol=coin_data.coin_symbol)
            session.add(coin_query)
            await session.commit()

            logger.info(
                f"Coin '{coin_data.coin_name}' ({coin_data.coin_symbol}) successfully added for user '{coin_data.username}'."
            )

            return ActionCoinSchema(
                success=True,
                message=f"Coin '{coin_data.coin_name}' ({coin_data.coin_symbol}) successfully added for user '{coin_data.username}'.",
                coin_name=coin_data.coin_name,
                coin_symbol=coin_data.coin_symbol,
            )

        except sqlalchemy.exc.IntegrityError as e:
            logger.warning(
                f"Integrity error while adding coin '{coin_data.coin_name}' for user '{coin_data.username}': {e}"
            )

            return ActionCoinSchema(
                success=False,
                message="There was a problem adding the coin. Please ensure the coin details are valid and try again.",
                coin_name=coin_data.coin_name,
                coin_symbol=coin_data.coin_symbol,
            )

        except Exception as e:
            logger.error(
                f"Unexpected error while adding coin '{coin_data.coin_name}' for user '{coin_data.username}': {e}"
            )

            return ActionCoinSchema(
                success=False,
                message="An unexpected error occurred while adding the coin. Please try again later.",
                coin_name=coin_data.coin_name,
                coin_symbol=coin_data.coin_symbol,
            )


async def get_all_coins_for_user(username: str) -> UserCoinsSchema:
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
                return UserCoinsSchema(coins=[])

            logger.info(f"Retrieved {len(all_coins)} coins for user '{username}'.")
            return UserCoinsSchema(
                coins=[CoinSchema(coin_name=coin.name, coin_symbol=coin.symbol) for coin in all_coins]
            )

        except Exception as e:
            logger.error(f"Error retrieving coins for user '{username}': {e}")
            return UserCoinsSchema(coins=[])


async def delete_coin_for_user(coin_data: UserActionCoinSchema) -> ActionCoinSchema:
    """Remove a user's coin from the database."""

    async with async_session() as session:
        try:
            user_id_subquery = (
                sqlalchemy.select(UsersORM.id).where(UsersORM.username == coin_data.username).scalar_subquery()
            )

            result = await session.execute(
                sqlalchemy.delete(CoinsORM).where(
                    CoinsORM.user_id == user_id_subquery,
                    CoinsORM.name == coin_data.coin_name,
                    CoinsORM.symbol == coin_data.coin_symbol,
                )
            )
            if result.rowcount == 0:
                logger.warning(
                    f"Attempted to delete non-existent coin '{coin_data.coin_name}' ({coin_data.coin_symbol}) for user '{coin_data.username}'."
                )

                return ActionCoinSchema(
                    success=False,
                    message=f"The coin '{coin_data.coin_name}' ({coin_data.coin_symbol}) for user '{coin_data.username}' was not found.",
                    coin_name=coin_data.coin_name,
                    coin_symbol=coin_data.coin_symbol,
                )

            await session.commit()

            logger.info(
                f"Coin '{coin_data.coin_name}' ({coin_data.coin_symbol}) successfully deleted for user '{coin_data.username}'."
            )

            return ActionCoinSchema(
                success=True,
                message=f"Coin '{coin_data.coin_name}' ({coin_data.coin_symbol}) successfully removed for user '{coin_data.username}'.",
                coin_name=coin_data.coin_name,
                coin_symbol=coin_data.coin_symbol,
            )

        except sqlalchemy.exc.IntegrityError as e:
            logger.error(
                f"Integrity error while deleting coin '{coin_data.coin_name}' for user '{coin_data.username}': {e}"
            )

            return ActionCoinSchema(
                success=False,
                message="There was a problem removing the coin. Please try again later.",
                coin_name=coin_data.coin_name,
                coin_symbol=coin_data.coin_symbol,
            )

        except Exception as e:
            logger.error(
                f"Unexpected error while deleting coin '{coin_data.coin_name}' for user '{coin_data.username}': {e}"
            )

            return ActionCoinSchema(
                success=False,
                message="An unexpected error occurred while removing the coin. Please try again later.",
                coin_name=coin_data.coin_name,
                coin_symbol=coin_data.coin_symbol,
            )
