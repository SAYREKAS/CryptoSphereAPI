"""Models for interaction with the database"""

import asyncio
from datetime import datetime

from sqlalchemy import ForeignKey, func, UniqueConstraint
from sqlalchemy import Integer, String, Numeric, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.database.config import engine
from src.database.triggers import coin_statistics_trigger

CUSTOM_NUMERIC = Numeric(25, 10)


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)


class UsersORM(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(length=50), nullable=False, unique=True, index=True)
    email: Mapped[str] = mapped_column(String(length=70), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(length=64), nullable=False)

    registered_at: Mapped[datetime] = mapped_column(nullable=False, default=func.now())

    def __str__(self):
        return self.username


class CoinsORM(Base):
    __tablename__ = "coins"

    user_id: Mapped[int] = mapped_column(ForeignKey(UsersORM.id, ondelete="CASCADE"), index=True)

    name: Mapped[str] = mapped_column(String(length=100), nullable=False, index=True)
    symbol: Mapped[str] = mapped_column(String(length=100), nullable=False, index=True)
    date_added: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, default=func.now())

    __table_args__ = (UniqueConstraint("user_id", "name", "symbol", name="uix_user_coin_name_symbol"),)

    def __str__(self):
        return self.name + " " + self.symbol


class CoinTransactionsORM(Base):
    __tablename__ = "coin_transactions"

    user_id: Mapped[int] = mapped_column(ForeignKey(UsersORM.id, ondelete="CASCADE"))
    coin_id: Mapped[int] = mapped_column(ForeignKey(CoinsORM.id, ondelete="CASCADE"))

    buy: Mapped[float] = mapped_column(Numeric(20, 10), default=0)
    sell: Mapped[float] = mapped_column(Numeric(20, 10), default=0)
    usd: Mapped[float] = mapped_column(Numeric(20, 10), default=0)
    date_added: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, default=func.now())


class CoinStatisticsORM(Base):
    __tablename__ = "coin_statistics"

    user_id: Mapped[int] = mapped_column(ForeignKey(UsersORM.id, ondelete="CASCADE"), nullable=False)
    coin_id: Mapped[int] = mapped_column(ForeignKey(CoinsORM.id, ondelete="CASCADE"), nullable=False)

    total_buy: Mapped[float] = mapped_column(CUSTOM_NUMERIC, nullable=False, default=0)
    total_invested: Mapped[float] = mapped_column(CUSTOM_NUMERIC, nullable=False, default=0)
    total_invested_avg: Mapped[float] = mapped_column(CUSTOM_NUMERIC, nullable=False, default=0)

    total_sell: Mapped[float] = mapped_column(CUSTOM_NUMERIC, nullable=False, default=0)
    total_realized: Mapped[float] = mapped_column(CUSTOM_NUMERIC, nullable=False, default=0)
    total_realized_avg: Mapped[float] = mapped_column(CUSTOM_NUMERIC, nullable=False, default=0)

    holdings: Mapped[float] = mapped_column(CUSTOM_NUMERIC, nullable=False, default=0)
    transaction_count: Mapped[int] = mapped_column(nullable=False, default=0)
    last_updated: Mapped[datetime] = mapped_column(nullable=False, default=func.now())


async def recreate_tables():
    """Видаляє та створює всі таблиці."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        await coin_statistics_trigger(conn)


if __name__ == "__main__":
    asyncio.run(recreate_tables())
