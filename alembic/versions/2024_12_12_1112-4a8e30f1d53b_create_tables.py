"""Create tables

Revision ID: 4a8e30f1d53b
Revises: 
Create Date: 2024-12-12 11:12:38.346407

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4a8e30f1d53b"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=70), nullable=False),
        sa.Column("password", sa.String(length=64), nullable=False),
        sa.Column("registered_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("id"),
    )
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    op.create_table(
        "coins",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("symbol", sa.String(length=100), nullable=False),
        sa.Column("date_added", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
        sa.UniqueConstraint("user_id", "name", "symbol", name="uix_user_coin_name_symbol"),
    )
    op.create_index(op.f("ix_coins_name"), "coins", ["name"], unique=False)
    op.create_index(op.f("ix_coins_symbol"), "coins", ["symbol"], unique=False)
    op.create_index(op.f("ix_coins_user_id"), "coins", ["user_id"], unique=False)

    op.create_table(
        "coin_statistics",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("coin_id", sa.Integer(), nullable=False),
        sa.Column("total_buy", sa.Numeric(precision=25, scale=10), nullable=False),
        sa.Column("total_invested", sa.Numeric(precision=25, scale=10), nullable=False),
        sa.Column("total_invested_avg", sa.Numeric(precision=25, scale=10), nullable=False),
        sa.Column("total_sell", sa.Numeric(precision=25, scale=10), nullable=False),
        sa.Column("total_realized", sa.Numeric(precision=25, scale=10), nullable=False),
        sa.Column("total_realized_avg", sa.Numeric(precision=25, scale=10), nullable=False),
        sa.Column("holdings", sa.Numeric(precision=25, scale=10), nullable=False),
        sa.Column("total_fee", sa.Numeric(precision=25, scale=10), nullable=False),
        sa.Column("transaction_count", sa.Integer(), nullable=False),
        sa.Column("last_updated", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["coin_id"], ["coins.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )
    op.create_index(op.f("ix_coin_statistics_coin_id"), "coin_statistics", ["coin_id"], unique=False)
    op.create_index(op.f("ix_coin_statistics_user_id"), "coin_statistics", ["user_id"], unique=False)

    op.create_table(
        "coin_transactions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("coin_id", sa.Integer(), nullable=False),
        sa.Column("buy", sa.Numeric(precision=25, scale=10), nullable=False),
        sa.Column("sell", sa.Numeric(precision=25, scale=10), nullable=False),
        sa.Column("paid", sa.Numeric(precision=25, scale=10), nullable=False),
        sa.Column("average_price", sa.Numeric(precision=25, scale=10), nullable=False),
        sa.Column("fee", sa.Numeric(precision=25, scale=10), nullable=False),
        sa.Column("date_added", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["coin_id"], ["coins.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )
    op.create_index(op.f("ix_coin_transactions_coin_id"), "coin_transactions", ["coin_id"], unique=False)
    op.create_index(op.f("ix_coin_transactions_user_id"), "coin_transactions", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_coin_transactions_user_id"), table_name="coin_transactions")
    op.drop_index(op.f("ix_coin_transactions_coin_id"), table_name="coin_transactions")
    op.drop_table("coin_transactions")
    op.drop_index(op.f("ix_coin_statistics_user_id"), table_name="coin_statistics")
    op.drop_index(op.f("ix_coin_statistics_coin_id"), table_name="coin_statistics")
    op.drop_table("coin_statistics")
    op.drop_index(op.f("ix_coins_user_id"), table_name="coins")
    op.drop_index(op.f("ix_coins_symbol"), table_name="coins")
    op.drop_index(op.f("ix_coins_name"), table_name="coins")
    op.drop_table("coins")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_table("users")
