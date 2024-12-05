"""Implementing endpoints for working with user profiles"""

from fastapi import APIRouter, status

from src.database.crud.users_crud import create_user, read_all_users, delete_user_by_username, read_user_by_username
from src.schemas.crud_users_schemas import AllUsersSchema, NewUserSchema, UserInfoSchema

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(user_data: NewUserSchema) -> UserInfoSchema:
    """Endpoint to add a new user to the database."""
    return await create_user(user_data=user_data)


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all_users_endpoint() -> AllUsersSchema:
    """Endpoint to retrieve a list of usernames."""
    return await read_all_users()


@router.get("/{username}", status_code=status.HTTP_200_OK)
async def read_user_by_username_endpoint(username: str) -> UserInfoSchema:
    """Endpoint to retrieve user information by a username."""
    return await read_user_by_username(username=username)


@router.delete("/{username}", status_code=status.HTTP_200_OK)
async def delete_user_by_username_endpoint(username: str) -> UserInfoSchema:
    """Endpoint to remove a user from the database."""
    return await delete_user_by_username(username=username)
