"""CRUD database operations"""

from loguru import logger
from pydantic import ValidationError
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.models import UsersORM
from api.schemas.users_crud_schemas import UserInfoSchema, AllUsersSchema


async def create_user(user_data: UserInfoSchema, session: AsyncSession) -> UserInfoSchema:
    """Add a new user to the database."""

    try:
        new_user = UsersORM(**user_data.model_dump())
        session.add(new_user)
        await session.commit()

        logger.info(f"User created: username='{user_data.username}', email='{user_data.email}'.")
        return UserInfoSchema(
            username=user_data.username,
            email=user_data.email,
        )
    except IntegrityError:
        logger.warning(f"Integrity error for user '{user_data.username}'.")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username or email already exists.")

    except ValidationError as e:
        logger.warning(f"Validation error for user '{user_data.username}': {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Validation error. Check input data.")


async def read_all_users(session: AsyncSession) -> AllUsersSchema:
    """Retrieve all registered users."""

    try:
        users_query = await session.execute(select(UsersORM.username))
        users = users_query.scalars().all()
        logger.info(f"Retrieved {len(users)} users.")
        return AllUsersSchema(users=users)

    except Exception as e:
        logger.error(f"Error retrieving users: {e}")
        return AllUsersSchema(users=[])


async def read_user_by_username(username: str, session: AsyncSession) -> UserInfoSchema:
    """Retrieve a user by their username."""

    user_query = await session.execute(select(UsersORM).where(UsersORM.username == username))

    user = user_query.scalar_one_or_none()
    if not user:
        logger.warning(f"User '{username}' not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User '{username}' not found.")

    logger.info(f"User '{username}' retrieved.")
    return UserInfoSchema(username=user.username, email=user.email)


async def delete_user_by_username(username: str, session: AsyncSession) -> UserInfoSchema:
    """Delete a user from the database."""

    try:
        result = await session.execute(
            delete(UsersORM).where(UsersORM.username == username).returning(UsersORM.username, UsersORM.email)
        )

        user = result.fetchone()
        if user is None:
            logger.warning(f"User '{username}' not found for deletion.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"User '{username}' not found for deletion."
            )

        await session.commit()

        name, email = user

        logger.info(f"User deleted: username='{name}', email='{email}'.")
        return UserInfoSchema(username=name, email=email)

    except Exception as e:
        logger.error(f"Error deleting user '{username}': {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="General error, try again later.")
