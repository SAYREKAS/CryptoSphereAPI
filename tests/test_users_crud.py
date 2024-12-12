import hashlib

import pytest
from sqlalchemy import select
from fastapi import HTTPException

from api.database.models import UsersORM
from api.schemas.users_crud_schemas import UserActionSchema
from api.crud.users_crud import create_user, read_all_users, read_user_by_username, delete_user_by_username
from tests.async_session_fixture import session


@pytest.mark.asyncio
async def test_create_user(session):
    """Test user creation."""
    password = "StrongPassword12!"
    user_data = UserActionSchema(username="testuser", email="test@example.com", password=password)

    result = await create_user(user_data, session)
    assert user_data.username == result.username
    assert user_data.email == result.email
    assert user_data.password == hashlib.sha256(password.encode()).hexdigest()

    # Verify user exists in database
    query = await session.execute(select(UsersORM).where(UsersORM.username == user_data.username))
    user = query.scalar_one_or_none()
    assert user is not None
    assert user.username == user_data.username
    assert user.email == user_data.email
    assert user.password == user_data.password
    assert user.password == hashlib.sha256(password.encode()).hexdigest()


@pytest.mark.asyncio
async def test_create_user_duplicate(session):
    """Test user creation with duplicate username or email."""
    password = "StrongPassword1!"
    user_data = UserActionSchema(username="testuser", email="test@example.com", password=password)

    await create_user(user_data, session)

    with pytest.raises(HTTPException) as exc:
        await create_user(user_data, session)

    assert exc.value.status_code == 409
    assert exc.value.detail == "Username or email already exists."


@pytest.mark.asyncio
async def test_read_all_users(session):
    """Test retrieving all users."""
    users = [
        UserActionSchema(username="user1", email="user1@example.com", password="StrongPassword1!"),
        UserActionSchema(username="user2", email="user2@example.com", password="StrongPassword2!"),
        UserActionSchema(username="user3", email="user3@example.com", password="StrongPassword3!"),
    ]

    for user in users:
        await create_user(user, session)

    result = await read_all_users(session)
    assert len(result.users) == len(users)
    assert set(result.users) == {"user1", "user2", "user3"}


@pytest.mark.asyncio
async def test_read_user_by_username(session):
    """Test retrieving a user by username."""
    user_data = UserActionSchema(username="testuser", email="test@example.com", password="StrongPassword1!")
    await create_user(user_data, session)

    result = await read_user_by_username(user_data.username, session)
    assert result.username == user_data.username
    assert result.email == user_data.email


@pytest.mark.asyncio
async def test_read_user_by_username_not_found(session):
    """Test retrieving a user by username that does not exist."""

    with pytest.raises(HTTPException) as exc:
        await read_user_by_username("nonexistent", session)

    assert exc.value.status_code == 404
    assert exc.value.detail == "User 'nonexistent' not found."


@pytest.mark.asyncio
async def test_delete_user_by_username(session):
    """Test deleting a user by username."""
    user_data = UserActionSchema(username="testuser", email="test@example.com", password="StrongPassword1!")
    await create_user(user_data, session)

    result = await delete_user_by_username(user_data=user_data, session=session)
    assert result.username == user_data.username
    assert result.email == user_data.email

    # Verify user no longer exists
    query = await session.execute(select(UsersORM).where(UsersORM.username == user_data.username))
    user = query.scalar_one_or_none()
    assert user is None


@pytest.mark.asyncio
async def test_delete_user_by_username_not_found(session):
    """Test deleting a user by username that does not exist."""
    with pytest.raises(HTTPException) as exc:
        user_data = UserActionSchema(username="nonexistent", email="test@example.com", password="StrongPassword1!")
        await delete_user_by_username(user_data=user_data, session=session)

    assert exc.value.status_code == 404
    assert (
        exc.value.detail
        == "User with username 'nonexistent' and the provided email and password not found for deletion."
    )
