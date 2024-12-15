import pytest_asyncio


DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def session():
    """Create an in-memory database for testing."""

    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
    from api.database.models import Base

    engine = create_async_engine(DATABASE_URL, future=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    # Creation of tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        yield session

    # Deleting tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def new_test_user(session):
    """Create a new test user for testing."""

    from api.crud.users_crud import create_user
    from api.schemas.users_crud_schemas import UserActionSchema

    user_data = UserActionSchema(username="testuser", email="test@example.com", password="StrongPassword12!")
    return await create_user(user_data, session)
