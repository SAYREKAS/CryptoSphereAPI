"""CRUD database operations"""

import sqlalchemy
from loguru import logger
from pydantic import EmailStr

from database.models import UsersORM
from database.config import async_session
from schemas.api_schemas import AddUserSchema


async def add_new_user(username: str, email: EmailStr, password: str) -> None:
    """Add a new user to the database."""

    async with async_session() as session:
        try:
            serializer = AddUserSchema(username=username, email=email, password=password)
            user = UsersORM(**serializer.model_dump())
            session.add(user)

            await session.commit()
            logger.info(f"Added new user {username} to database")

        except sqlalchemy.exc.IntegrityError as e:
            logger.error(f"User {serializer.username} already exists or other integrity issue.")


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
