"""CRUD database operations"""

import sqlalchemy
from loguru import logger

from src.database.config import async_session
from src.database.models import UsersORM
from src.schemas.crud_user_schemas import UserInfoSchema, NewUserInfoSchema, AllUsersSchema, DeleteUserResultSchema


async def create_user(user_data: NewUserInfoSchema) -> UserInfoSchema:
    """Add a new user to the database."""
    async with async_session() as session:
        try:
            new_user = UsersORM(**user_data.model_dump())
            session.add(new_user)
            await session.commit()

            logger.info(f"User created: username='{user_data.username}', email='{user_data.email}'.")
            return UserInfoSchema(
                success=True,
                message=f"User '{user_data.username}' successfully created.",
                username=user_data.username,
                email=user_data.email,
            )
        except sqlalchemy.exc.IntegrityError as e:
            logger.error(f"Integrity error for user '{user_data.username}': {e}")
            return UserInfoSchema(
                success=False,
                message="Username or email already exists.",
                username=user_data.username,
                email=user_data.email,
            )


async def read_all_users() -> AllUsersSchema:
    """Retrieve all registered users."""
    async with async_session() as session:
        try:
            users_query = await session.execute(sqlalchemy.select(UsersORM.username))
            users = users_query.scalars().all()
            logger.info(f"Retrieved {len(users)} users.")
            return AllUsersSchema(users=users)
        except Exception as e:
            logger.error(f"Error retrieving users: {e}")
            return AllUsersSchema(users=[])


async def read_user_by_username(username: str) -> UserInfoSchema:
    """Retrieve a user by their username."""
    async with async_session() as session:
        user_query = await session.execute(sqlalchemy.select(UsersORM).where(UsersORM.username == username))
        user = user_query.scalar_one_or_none()
        if not user:
            logger.warning(f"User '{username}' not found.")
            return UserInfoSchema(
                success=False,
                message=f"User '{username}' not found.",
            )
        logger.info(f"User '{username}' retrieved.")
        return UserInfoSchema(
            success=True,
            message=f"User '{username}' found.",
            username=user.username,
            email=user.email,
        )


async def delete_user_by_username(username: str) -> DeleteUserResultSchema:
    """Delete a user from the database."""
    async with async_session() as session:
        try:
            result = await session.execute(sqlalchemy.delete(UsersORM).where(UsersORM.username == username))
            if result.rowcount == 0:
                logger.warning(f"User '{username}' not found for deletion.")
                return DeleteUserResultSchema(
                    success=False,
                    message=f"User '{username}' not found.",
                    username=username,
                )
            await session.commit()
            logger.info(f"User '{username}' deleted.")
            return DeleteUserResultSchema(
                success=True,
                message=f"User '{username}' deleted successfully.",
                username=username,
            )
        except Exception as e:
            logger.error(f"Error deleting user '{username}': {e}")
            return DeleteUserResultSchema(
                success=False,
                message="An error occurred while deleting the user.",
                username=username,
            )
