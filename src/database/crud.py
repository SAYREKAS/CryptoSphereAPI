"""CRUD database operations"""

import sqlalchemy
from loguru import logger

from src.database.config import async_session
from src.database.models import UsersORM, CoinsORM
from src.schemas.common_schemas import ActionResult
from src.schemas.crud_schemas import CoinBasicInfoSchema
from src.schemas.api_schemas import UserCredentialsSchema, UserCoinSchema


async def add_new_user(user: UserCredentialsSchema) -> ActionResult:
    """Add a new user to the database."""

    async with async_session() as session:
        try:
            new_user = UsersORM(**user.model_dump())

            session.add(new_user)
            await session.commit()
            logger.info(f"Added new user {user.username} to database")
            return ActionResult(success=True, message=f"Added new user {user.username} to database")

        except sqlalchemy.exc.IntegrityError as e:
            logger.error(str(e))
            return ActionResult(success=False, message=f"User {user.username} already exists or other integrity issue.")


async def get_all_users() -> list[str]:
    """Retrieve all register users"""

    async with async_session() as session:
        users_query = await session.execute(sqlalchemy.select(UsersORM.username))
        users = users_query.scalars().all()
        return users


async def delete_user(username: str) -> ActionResult:
    """Delete a user from the database."""

    async with async_session() as session:
        try:
            user_query = await session.execute(sqlalchemy.select(UsersORM).where(UsersORM.username == username))
            user = user_query.scalar_one_or_none()

            if not user:
                logger.error(f"User {username} not found.")
                return ActionResult(success=False, message=f"User {username} not found.")

            await session.delete(user)
            await session.commit()
            logger.info(f"Deleted user {username} from database")
            return ActionResult(success=True, message=f"Deleted user {username} from database")

        except Exception as e:
            logger.error(f"Failed to delete user {username}: {e}")
            return ActionResult(success=False, message=f"Failed to delete user {username}")


async def add_coin_for_user(coin_data: UserCoinSchema) -> ActionResult:
    """Add a new coin for a user identified by a username."""

    async with async_session() as session:
        try:
            result_query = await session.execute(
                sqlalchemy.select(UsersORM).where(UsersORM.username == coin_data.username)
            )
            user = result_query.scalar_one_or_none()

            if not user:
                logger.error(f"User {coin_data.username} not found.")
                return ActionResult(success=False, message=f"User {coin_data.username} not found.")

            coin_query = CoinsORM(user_id=user.id, name=coin_data.coin_name, symbol=coin_data.coin_symbol)
            session.add(coin_query)
            await session.commit()

            logger.info(f"Added new coin {coin_data.coin_name} ({coin_data.coin_symbol}) for user {coin_data.username}")
            return ActionResult(
                success=True, message=f"Added new coin {coin_data.coin_name} for user {coin_data.username}"
            )
        except sqlalchemy.exc.IntegrityError as e:
            logger.error(f"Failed to add coin {coin_data.coin_name}: {e}")
            return ActionResult(success=False, message=f"Failed to add coin {coin_data.coin_name}")


async def get_all_coins_for_user(username: str) -> list[CoinBasicInfoSchema]:
    """Retrieve all coins for a user identified by a username."""

    async with async_session() as session:
        try:
            user_query = await session.execute(sqlalchemy.select(UsersORM).where(UsersORM.username == username))
            user = user_query.scalar_one_or_none()

            if not user:
                logger.error(f"User {username} not found.")
                return []

            coins_query = await session.execute(sqlalchemy.select(CoinsORM).where(CoinsORM.user_id == user.id))
            all_coins = coins_query.scalars().all()
            return [CoinBasicInfoSchema(name=coin.name, symbol=coin.symbol) for coin in all_coins]

        except Exception as e:
            logger.error(f"Failed to get all coins for user {username}: {e}")


async def delete_coin_for_user(coin_data: UserCoinSchema) -> ActionResult:
    """Removes the user's coin from the database."""

    async with async_session() as session:
        try:
            user_query = await session.execute(
                sqlalchemy.select(UsersORM).where(UsersORM.username == coin_data.username)
            )
            user = user_query.scalar_one_or_none()

            if not user:
                logger.error(f"User {coin_data.username} not found.")
                return ActionResult(success=False, message=f"User {coin_data.username} not found.")

            coin_query = await session.execute(
                sqlalchemy.select(CoinsORM).where(
                    CoinsORM.user_id == user.id,
                    CoinsORM.name == coin_data.coin_name,
                    CoinsORM.symbol == coin_data.coin_symbol,
                )
            )
            coin = coin_query.scalar_one_or_none()

            if not coin:
                logger.error(
                    f"Coin {coin_data.coin_name} ({coin_data.coin_symbol}) not found for user {coin_data.username}."
                )
                return ActionResult(
                    success=False,
                    message=f"Coin {coin_data.coin_name} ({coin_data.coin_symbol}) not found for user {coin_data.username}.",
                )

            await session.delete(coin)
            await session.commit()

            logger.info(
                f"Coin {coin_data.coin_name} ({coin_data.coin_symbol}) successfully deleted for user {coin_data.username}."
            )
            return ActionResult(
                success=True,
                message=f"Coin {coin_data.coin_name} ({coin_data.coin_symbol}) successfully deleted for user {coin_data.username}.",
            )

        except sqlalchemy.exc.IntegrityError as e:
            logger.error(f"Integrity error while deleting coin for user {coin_data.username}: {e}")
            return ActionResult(success=False, message=f"Error while deleting coin for user {coin_data.username}")
