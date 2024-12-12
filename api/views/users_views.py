"""Implementing endpoints for working with user profiles"""

from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud.users_crud import create_user, read_all_users, delete_user_by_username, read_user_by_username
from api.schemas.users_crud_schemas import (
    AllUsersSchema,
    UserActionSchema,
    UserInfoSchema,
    FullUserInfoSchema,
    DeleteUserSchema,
)
from api.database.db_helper import db_helper

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserInfoSchema)
async def create_user_endpoint(
    user_data: UserActionSchema, session: AsyncSession = Depends(db_helper.session_getter)
):
    """Endpoint to add a new user to the database."""
    return await create_user(user_data=user_data, session=session)


@router.get("/", status_code=status.HTTP_200_OK, response_model=AllUsersSchema)
async def read_all_users_endpoint(session: AsyncSession = Depends(db_helper.session_getter)):
    """Endpoint to retrieve a list of usernames."""
    return await read_all_users(session=session)


@router.get("/{username}", status_code=status.HTTP_200_OK, response_model=FullUserInfoSchema)
async def read_user_by_username_endpoint(username: str, session: AsyncSession = Depends(db_helper.session_getter)):
    """Endpoint to retrieve user information by a username."""
    return await read_user_by_username(username=username, session=session)


@router.delete("/", status_code=status.HTTP_200_OK, response_model=UserInfoSchema)
async def delete_user_by_username_endpoint(
    user_data: UserActionSchema, session: AsyncSession = Depends(db_helper.session_getter)
):
    """Endpoint to remove a user from the database."""
    return await delete_user_by_username(user_data=user_data, session=session)
