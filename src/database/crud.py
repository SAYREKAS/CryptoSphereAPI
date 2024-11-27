"""CRUD database operations"""

import sqlalchemy
from loguru import logger

from src.database.config import async_session
from src.database.models import UsersORM, CoinsORM
from src.schemas.common_schemas import ActionResult
from src.schemas.crud_schemas import CoinBasicInfoSchema
from src.schemas.api_schemas import UserSchema, UserCoinSchema


async def add_new_user(user: UserSchema) -> ActionResult:
    """Add a new user to the database."""

    async with async_session() as session:
        try:
            new_user = UsersORM(**user.model_dump())
            session.add(new_user)
            await session.commit()
            logger.info(f"New user '{user.username}' successfully added to the database.")
            return ActionResult(success=True, message=f"User '{user.username}' was successfully registered.")

        except sqlalchemy.exc.IntegrityError as e:
            logger.error(f"Integrity error while adding user '{user.username}': {e}")
            return ActionResult(success=False, message=f"User '{user.username}' already exists or invalid data.")


async def get_all_users() -> list[str]:
    """Retrieve all registered users."""

    async with async_session() as session:
        try:
            users_query = await session.execute(sqlalchemy.select(UsersORM.username))
            users = users_query.scalars().all()
            logger.info(f"Retrieved {len(users)} users from the database.")
            return users

        except Exception as e:
            logger.error(f"Error retrieving user list: {e}")
            return []


async def delete_user(username: str) -> ActionResult:
    """Delete a user from the database."""

    async with async_session() as session:
        try:
            result = await session.execute(sqlalchemy.delete(UsersORM).where(UsersORM.username == username))
            if result.rowcount == 0:
                logger.warning(f"Attempted to delete non-existent user '{username}'.")
                return ActionResult(success=False, message=f"User '{username}' does not exist.")

            await session.commit()
            logger.info(f"User '{username}' successfully deleted from the database.")
            return ActionResult(success=True, message=f"User '{username}' was successfully deleted.")

        except Exception as e:
            logger.error(f"Error while deleting user '{username}': {e}")
            return ActionResult(success=False, message=f"An error occurred while deleting user '{username}'.")


async def add_coin_for_user(coin_data: UserCoinSchema) -> ActionResult:
    """Add a new coin for a user identified by a username."""

    async with async_session() as session:
        try:
            result_query = await session.execute(
                sqlalchemy.select(UsersORM.id).where(UsersORM.username == coin_data.username)
            )

            user_id = result_query.scalar_one_or_none()
            if not user_id:
                logger.warning(f"Attempted to add a coin for non-existent user '{coin_data.username}'.")
                return ActionResult(success=False, message=f"User '{coin_data.username}' does not exist.")

            coin_query = CoinsORM(user_id=user_id, name=coin_data.coin_name, symbol=coin_data.coin_symbol)
            session.add(coin_query)
            await session.commit()

            logger.info(
                f"Coin '{coin_data.coin_name}' ({coin_data.coin_symbol}) successfully added for user '{coin_data.username}'."
            )
            return ActionResult(
                success=True,
                message=f"Coin '{coin_data.coin_name}' was successfully added for user '{coin_data.username}'.",
            )
        except sqlalchemy.exc.IntegrityError as e:
            logger.error(
                f"Integrity error while adding coin '{coin_data.coin_name}' for user '{coin_data.username}': {e}"
            )
            return ActionResult(
                success=False,
                message=f"Could not add coin '{coin_data.coin_name}'. Possible duplicate or invalid data.",
            )


async def get_all_coins_for_user(username: str) -> list[CoinBasicInfoSchema]:
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
            return [CoinBasicInfoSchema(name=coin.name, symbol=coin.symbol) for coin in all_coins]

        except Exception as e:
            logger.error(f"Error retrieving coins for user '{username}': {e}")
            return []


async def delete_coin_for_user(coin_data: UserCoinSchema) -> ActionResult:
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
                return ActionResult(
                    success=False, message=f"Coin '{coin_data.coin_name}' not found for user '{coin_data.username}'."
                )
            await session.commit()

            logger.info(
                f"Coin '{coin_data.coin_name}' ({coin_data.coin_symbol}) successfully deleted for user '{coin_data.username}'."
            )
            return ActionResult(
                success=True,
                message=f"Coin '{coin_data.coin_name}' was successfully deleted for user '{coin_data.username}'.",
            )
        except sqlalchemy.exc.IntegrityError as e:
            logger.error(
                f"Integrity error while deleting coin '{coin_data.coin_name}' for user '{coin_data.username}': {e}"
            )
            return ActionResult(
                success=False,
                message=f"An error occurred while deleting coin '{coin_data.coin_name}' for user '{coin_data.username}'.",
            )
