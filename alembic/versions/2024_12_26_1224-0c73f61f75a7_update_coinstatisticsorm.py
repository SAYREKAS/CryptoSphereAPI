"""Update CoinStatisticsORM

Revision ID: 0c73f61f75a7
Revises: 4a8e30f1d53b
Create Date: 2024-12-26 12:24:33.597632

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0c73f61f75a7"
down_revision: Union[str, None] = "4a8e30f1d53b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("coin_statistics", sa.Column("buy_total", sa.Numeric(precision=25, scale=10), nullable=False))
    op.add_column("coin_statistics", sa.Column("invested_total", sa.Numeric(precision=25, scale=10), nullable=False))
    op.add_column("coin_statistics", sa.Column("invested_avg", sa.Numeric(precision=25, scale=10), nullable=False))
    op.add_column("coin_statistics", sa.Column("sell_total", sa.Numeric(precision=25, scale=10), nullable=False))
    op.add_column("coin_statistics", sa.Column("realized_total", sa.Numeric(precision=25, scale=10), nullable=False))
    op.add_column("coin_statistics", sa.Column("realized_avg", sa.Numeric(precision=25, scale=10), nullable=False))
    op.add_column("coin_statistics", sa.Column("fee_total", sa.Numeric(precision=25, scale=10), nullable=False))
    op.add_column("coin_statistics", sa.Column("transactions_count", sa.Integer(), nullable=False))
    op.add_column("coin_statistics", sa.Column("updated_at", sa.DateTime(), nullable=False))

    op.create_unique_constraint("uix_user_id_coin_id", "coin_statistics", ["user_id", "coin_id"])
    op.create_unique_constraint(None, "coin_statistics", ["id"])

    op.drop_column("coin_statistics", "total_realized_avg")
    op.drop_column("coin_statistics", "total_invested")
    op.drop_column("coin_statistics", "transaction_count")
    op.drop_column("coin_statistics", "total_sell")
    op.drop_column("coin_statistics", "total_invested_avg")
    op.drop_column("coin_statistics", "total_fee")
    op.drop_column("coin_statistics", "last_updated")
    op.drop_column("coin_statistics", "total_buy")
    op.drop_column("coin_statistics", "total_realized")

    op.create_unique_constraint(None, "coin_transactions", ["id"])
    op.create_unique_constraint(None, "coins", ["id"])
    op.create_unique_constraint(None, "users", ["id"])


def downgrade() -> None:
    op.drop_constraint(None, "users", type_="unique")
    op.drop_constraint(None, "coins", type_="unique")
    op.drop_constraint(None, "coin_transactions", type_="unique")
    op.add_column(
        "coin_statistics",
        sa.Column("total_realized", sa.NUMERIC(precision=25, scale=10), autoincrement=False, nullable=False),
    )
    op.add_column(
        "coin_statistics",
        sa.Column("total_buy", sa.NUMERIC(precision=25, scale=10), autoincrement=False, nullable=False),
    )
    op.add_column(
        "coin_statistics", sa.Column("last_updated", postgresql.TIMESTAMP(), autoincrement=False, nullable=False)
    )
    op.add_column(
        "coin_statistics",
        sa.Column("total_fee", sa.NUMERIC(precision=25, scale=10), autoincrement=False, nullable=False),
    )
    op.add_column(
        "coin_statistics",
        sa.Column("total_invested_avg", sa.NUMERIC(precision=25, scale=10), autoincrement=False, nullable=False),
    )
    op.add_column(
        "coin_statistics",
        sa.Column("total_sell", sa.NUMERIC(precision=25, scale=10), autoincrement=False, nullable=False),
    )
    op.add_column("coin_statistics", sa.Column("transaction_count", sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column(
        "coin_statistics",
        sa.Column("total_invested", sa.NUMERIC(precision=25, scale=10), autoincrement=False, nullable=False),
    )
    op.add_column(
        "coin_statistics",
        sa.Column("total_realized_avg", sa.NUMERIC(precision=25, scale=10), autoincrement=False, nullable=False),
    )
    op.drop_constraint(None, "coin_statistics", type_="unique")
    op.drop_constraint("uix_user_id_coin_id", "coin_statistics", type_="unique")
    op.drop_column("coin_statistics", "updated_at")
    op.drop_column("coin_statistics", "transactions_count")
    op.drop_column("coin_statistics", "fee_total")
    op.drop_column("coin_statistics", "realized_avg")
    op.drop_column("coin_statistics", "realized_total")
    op.drop_column("coin_statistics", "sell_total")
    op.drop_column("coin_statistics", "invested_avg")
    op.drop_column("coin_statistics", "invested_total")
    op.drop_column("coin_statistics", "buy_total")
