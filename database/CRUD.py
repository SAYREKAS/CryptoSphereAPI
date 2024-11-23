"""CRUD database operations"""

import asyncpg
import sqlalchemy
from loguru import logger

from database.config import async_session
from schemas.api_schemas import AddUserSchema, AddCoinSchema
from database.models import UsersORM, CoinsORM


async def get_all_users() -> list[str]:
    async with async_session() as session:
        data = await session.execute(sqlalchemy.select(UsersORM.username))
        users = data.scalars().all()
        return users


async def add_new_user(user_data: AddUserSchema) -> None:
    """Add a new user to the database."""

    async with async_session() as session:
        try:
            user = UsersORM(**user_data.model_dump())
            session.add(user)

            await session.commit()
            logger.info(f"Added new user {user_data.username} to database")

        except sqlalchemy.exc.IntegrityError as e:
            logger.error(f"User {user_data.username} already exists or other integrity issue.")


async def delete_user(username: str) -> None:
    """Delete a user from the database."""

    async with async_session() as session:
        result = await session.execute(sqlalchemy.select(UsersORM).where(UsersORM.username == username))
        user = result.scalar_one_or_none()

        if user:
            await session.delete(user)
            await session.commit()
            logger.info(f"Deleted user {username} from database")

        else:
            logger.error(f"User {username} not found.")


async def add_coin_for_user_by_username(coin_data: AddCoinSchema) -> None:
    """Add a new coin for a user identified by a username."""

    async with async_session() as session:
        try:
            result = await session.execute(sqlalchemy.select(UsersORM).where(UsersORM.username == coin_data.username))
            user = result.scalar_one_or_none()

            if user:
                coin = CoinsORM(user_id=user.id, name=coin_data.coin_name, symbol=coin_data.coin_symbol)
                session.add(coin)
                await session.commit()
                logger.info(
                    f"Added new coin {coin_data.coin_name} ({coin_data.coin_symbol}) for user {coin_data.username}"
                )

            else:
                logger.error(f"User {coin_data.username} not found.")

        except sqlalchemy.exc.IntegrityError as e:
            logger.error(e)
