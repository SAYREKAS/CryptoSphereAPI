"""
Module for handling coin transactions: creating and managing user coin operations.
"""

from loguru import logger
from sqlalchemy import select
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.models import UsersORM, CoinsORM, CoinTransactionsORM, CoinStatisticsORM
from api.schemas.coins_crud_schemas import OperationActionSchema


async def get_coin_or_raise_error(session: AsyncSession, username: str, coin_name: str, coin_symbol: str):
    """Fetch coin information for a user. Raise HTTPException if the coin does not exist."""

    try:
        query_result = await session.execute(
            select(CoinsORM)
            .join(UsersORM, UsersORM.id == CoinsORM.user_id)
            .where(
                UsersORM.username == username,
                CoinsORM.name == coin_name,
                CoinsORM.symbol == coin_symbol,
            )
        )
        coin_record = query_result.scalar_one_or_none()

        if coin_record is None:
            logger.error(f"Coin '{coin_name}' ({coin_symbol}) not found for user '{username}'.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Coin '{coin_name}' ({coin_symbol}) not found for user '{username}'.",
            )

        return coin_record

    except Exception as e:
        logger.critical(f"Error while fetching coin for user '{username}': {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error while fetching coin data.",
        )


async def new_transaction_record(session: AsyncSession, transaction_data: OperationActionSchema) -> CoinTransactionsORM:
    """Create a new transaction record for the specified user and coin."""

    coin_info = await get_coin_or_raise_error(
        session,
        transaction_data.username,
        transaction_data.coin_name,
        transaction_data.coin_symbol,
    )

    transaction_record = CoinTransactionsORM(
        coin_id=coin_info.id,
        user_id=coin_info.user_id,
        buy=transaction_data.buy,
        sell=transaction_data.sell,
        paid=transaction_data.paid,
        average_price=transaction_data.average_price,
        fee=transaction_data.fee,
    )

    logger.info(f"Transaction record created for user '{transaction_data.username}'.")
    return transaction_record


async def update_coin_statistics(session: AsyncSession, transaction: CoinTransactionsORM) -> CoinStatisticsORM:
    """Update or create coin statistics for a user based on the provided transaction."""

    query_result = await session.execute(
        select(CoinStatisticsORM)
        .where(
            CoinStatisticsORM.user_id == transaction.user_id,
            CoinStatisticsORM.coin_id == transaction.coin_id,
        )
        .with_for_update()
    )
    statistics_record = query_result.scalar_one_or_none()

    if statistics_record is not None:
        # Update existing statistics record
        statistics_record.buy_total += transaction.buy
        statistics_record.sell_total += transaction.sell
        statistics_record.invested_total += transaction.paid if transaction.buy > 0 else 0
        statistics_record.realized_total += transaction.paid if transaction.sell > 0 else 0
        statistics_record.holdings += transaction.buy - transaction.sell
        statistics_record.fee_total += transaction.fee
        statistics_record.transactions_count += 1

        # Update average values
        statistics_record.invested_avg = (
            statistics_record.invested_total / statistics_record.buy_total if statistics_record.buy_total > 0 else 0
        )
        statistics_record.realized_avg = (
            statistics_record.realized_total / statistics_record.sell_total if statistics_record.sell_total > 0 else 0
        )
        return statistics_record

    # Create a new statistics record
    new_statistics_record = CoinStatisticsORM(
        user_id=transaction.user_id,
        coin_id=transaction.coin_id,
        buy_total=transaction.buy,
        sell_total=transaction.sell,
        invested_total=transaction.paid if transaction.buy > 0 else 0,
        realized_total=transaction.paid if transaction.sell > 0 else 0,
        invested_avg=transaction.average_price if transaction.buy > 0 else 0,
        realized_avg=transaction.average_price if transaction.sell > 0 else 0,
        holdings=transaction.buy - transaction.sell,
        fee_total=transaction.fee,
        transactions_count=1,
    )
    return new_statistics_record


async def process_coin_transaction(session: AsyncSession, transaction_data: OperationActionSchema) -> None:
    """Process a coin transaction: create the transaction record and update statistics."""

    try:
        async with session.begin():
            transaction_record = await new_transaction_record(session=session, transaction_data=transaction_data)
            statistics_record = await update_coin_statistics(session=session, transaction=transaction_record)

            session.add(transaction_record)
            session.add(statistics_record)

        logger.info(
            f"Transaction processed successfully for user '{transaction_data.username}', coin '{transaction_data.coin_name}' ({transaction_data.coin_symbol})."
        )

    except HTTPException as e:
        logger.error(f"HTTPException during transaction processing: {e.detail}")
        raise

    except Exception as e:
        logger.critical(f"Critical error during transaction processing: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error while processing the transaction.",
        )
