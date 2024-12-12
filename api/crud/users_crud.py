"""CRUD database operations"""

from loguru import logger
from pydantic import ValidationError
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.models import UsersORM
from api.schemas.users_crud_schemas import UserInfoSchema, AllUsersSchema, UserActionSchema, FullUserInfoSchema


async def create_user(user_data: UserActionSchema, session: AsyncSession) -> UserInfoSchema:
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


async def read_user_by_username(username: str, session: AsyncSession) -> FullUserInfoSchema:
    """Retrieve a user by their username."""

    user_query = await session.execute(select(UsersORM).where(UsersORM.username == username))

    user = user_query.scalar_one_or_none()
    if not user:
        logger.warning(f"User '{username}' not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User '{username}' not found.")

    logger.info(f"User '{username}' retrieved.")
    return FullUserInfoSchema(
        id=user.id,
        username=user.username,
        email=user.email,
        hash_password=user.password,
        registered_at=user.registered_at,
    )


async def delete_user_by_username(user_data: UserActionSchema, session: AsyncSession) -> UserInfoSchema:
    """Delete a user from the database."""

    try:
        user_query = await session.execute(
            select(UsersORM).where(
                UsersORM.username == user_data.username,
                UsersORM.email == user_data.email,
                UsersORM.password == user_data.password,
            )
        )
        user = user_query.scalar_one_or_none()
        if user is None:
            logger.warning(
                f"User '{user_data.username}' with email '{user_data.email}' and provided password not found for deletion."
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with username '{user_data.username}' and the provided email and password not found for deletion.",
            )

        await session.execute(delete(UsersORM).where(UsersORM.id == user.id))
        await session.commit()

        logger.info(f"User deleted successfully: username='{user.username}', email='{user.email}'.")
        return UserInfoSchema(username=user.username, email=user.email)

    except HTTPException as e:
        logger.error(f"HTTP exception occurred: {e.detail}")
        raise

    except Exception as e:
        logger.error(f"Error deleting user '{user_data.username}': {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="General error occurred while trying to delete the user. Please try again later.",
        )
