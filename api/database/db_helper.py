"""
Database helper module for managing asynchronous database connections and sessions.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from api.config import settings


class DatabaseHelper:
    """Helper class for managing database connections."""

    def __init__(self, db_url: str, echo: bool = False, echo_pool=True, pool_size=5, max_overflow=1):
        """Initialize the database engine and session factory."""
        self.engine = create_async_engine(
            db_url,
            echo=echo,
            echo_pool=echo_pool,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )
        self.async_session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    async def dispose(self) -> None:
        """Dispose of the database engine."""
        await self.engine.dispose()

    async def session_getter(self) -> AsyncGenerator[AsyncSession, None]:
        """Give an async session generator."""
        async with self.async_session_factory() as session:
            yield session


db_helper = DatabaseHelper(
    str(settings.db.url),
    echo=settings.db.echo,
    echo_pool=settings.db.echo_pool,
    pool_size=settings.db.pool_size,
    max_overflow=settings.db.max_overflow,
)
