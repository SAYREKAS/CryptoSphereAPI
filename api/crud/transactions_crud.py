"""
Module for handling coin transactions: creating and managing user coin operations.
"""

from loguru import logger
from sqlalchemy import select
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.models import UsersORM, CoinsORM, CoinTransactionsORM
from api.schemas.coins_crud_schemas import OperationActionSchema


async def create_coin_transaction(operation: OperationActionSchema, session: AsyncSession) -> OperationActionSchema:
    """Create new coin transaction for user"""

    try:
        result = await session.execute(
            select(CoinsORM)
            .join(UsersORM, UsersORM.id == CoinsORM.user_id)
            .where(
                UsersORM.username == operation.username,
                CoinsORM.name == operation.coin_name,
                CoinsORM.symbol == operation.coin_symbol,
            )
        )

        coin_info = result.scalar_one_or_none()
        if coin_info is None:
            logger.error(
                f"Coin with name '{operation.coin_name}' "
                f"and symbol '{operation.coin_symbol}' "
                f"not found for user '{operation.username}'."
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Coin '{operation.coin_name}' ({operation.coin_symbol}) "
                f"not found for user '{operation.username}'.",
            )

        new_transaction = CoinTransactionsORM(
            coin_id=coin_info.id,
            user_id=coin_info.user_id,
            buy=operation.buy,
            sell=operation.sell,
            paid=operation.paid,
            average_price=operation.average_price,
            fee=operation.fee,
        )
        session.add(new_transaction)
        await session.commit()

        logger.info(f"Successfully created coin transaction for user '{operation.username}'")
        return operation

    except SQLAlchemyError as e:
        logger.error(f"Database error while creating coin transaction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while processing the transaction.",
        )

    except Exception as e:
        logger.error(f"Unexpected error while creating coin transaction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the transaction.",
        )
