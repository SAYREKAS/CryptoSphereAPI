"""Implementing endpoints for working with user profiles"""

from fastapi import APIRouter

from src.database.crud.crud_user import create_user, read_all_users, delete_user_by_username, read_user_by_username
from src.schemas.crud_user_schemas import AllUsersSchema, DeleteUserResultSchema, NewUserInfoSchema, UserInfoSchema

router = APIRouter()


@router.post("/")
async def create_user_endpoint(user_data: NewUserInfoSchema) -> UserInfoSchema:
    """Endpoint to add a new user to the database."""
    return await create_user(user_data=user_data)


@router.get("/")
async def read_all_users_endpoint() -> AllUsersSchema:
    """Endpoint to retrieve a list of usernames."""
    return await read_all_users()


@router.get("/{username}")
async def read_user_by_username_endpoint(username: str) -> UserInfoSchema:
    """Endpoint to retrieve a list of usernames."""
    return await read_user_by_username(username)


@router.delete("/{username}")
async def delete_user_by_username_endpoint(username: str) -> DeleteUserResultSchema:
    """Endpoint to remove a user from the database."""
    return await delete_user_by_username(username)
