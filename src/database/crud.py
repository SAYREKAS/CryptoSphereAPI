"""CRUD database operations"""

import sqlalchemy
from loguru import logger

from src.database.config import async_session
from src.schemas.api_schemas import UserSchema, CoinSchema
from src.database.models import UsersORM, CoinsORM


async def add_new_user(user_data: UserSchema) -> None:
    """Add a new user to the database."""

    async with async_session() as session:
        try:
            new_user = UsersORM(**user_data.model_dump())

            session.add(new_user)
            await session.commit()
            logger.info(f"Added new user {user_data.username} to database")

        except sqlalchemy.exc.IntegrityError as e:
            logger.error(f"User {user_data.username} already exists or other integrity issue.")


async def get_all_users() -> list[str]:
    """Retrieve all register users"""

    async with async_session() as session:
        users_query = await session.execute(sqlalchemy.select(UsersORM.username))
        users = users_query.scalars().all()
        return users


async def delete_user(username: str) -> None:
    """Delete a user from the database."""

    async with async_session() as session:
        try:
            user_query = await session.execute(sqlalchemy.select(UsersORM).where(UsersORM.username == username))
            user = user_query.scalar_one_or_none()

            if not user:
                logger.error(f"User {username} not found.")
                return

            await session.delete(user)
            await session.commit()
            logger.info(f"Deleted user {username} from database")

        except Exception as e:
            logger.error(f"Failed to delete user {username}: {e}")


async def add_coin_for_user(coin_data: CoinSchema) -> None:
    """Add a new coin for a user identified by a username."""

    async with async_session() as session:
        try:
            result_query = await session.execute(
                sqlalchemy.select(UsersORM).where(UsersORM.username == coin_data.username)
            )
            user = result_query.scalar_one_or_none()

            if not user:
                logger.error(f"User {coin_data.username} not found.")
                return

            coin_query = CoinsORM(user_id=user.id, name=coin_data.coin_name, symbol=coin_data.coin_symbol)

            session.add(coin_query)
            await session.commit()
            logger.info(f"Added new coin {coin_data.coin_name} ({coin_data.coin_symbol}) for user {coin_data.username}")

        except sqlalchemy.exc.IntegrityError as e:
            logger.error(f"Failed to add coin {coin_data.coin_name}: {e}")


async def get_all_coins_for_user(username: str) -> list[dict[str, str]]:
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
            return [{"name": coin.name, "symbol": coin.symbol} for coin in all_coins]

        except Exception as e:
            logger.error(f"Failed to get all coins for user {username}: {e}")


async def delete_coin_for_user(coin_data: CoinSchema) -> None:
    """Removes the user's coin from the database."""

    async with async_session() as session:
        try:
            user_query = await session.execute(
                sqlalchemy.select(UsersORM).where(UsersORM.username == coin_data.username)
            )
            user = user_query.scalar_one_or_none()

            if not user:
                logger.error(f"User {coin_data.username} not found.")
                return

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
                return

            await session.delete(coin)
            await session.commit()

            logger.info(
                f"Coin {coin_data.coin_name} ({coin_data.coin_symbol}) successfully deleted for user {coin_data.username}."
            )

        except sqlalchemy.exc.IntegrityError as e:
            logger.error(f"Integrity error while deleting coin for user {coin_data.username}: {e}")
