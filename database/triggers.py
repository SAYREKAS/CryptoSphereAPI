from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text


async def update_coin_statistics(session: AsyncSession):
    await session.execute(
        text(
            """
CREATE OR REPLACE FUNCTION update_coin_statistics()
    RETURNS TRIGGER AS
$$
BEGIN
    UPDATE "coin_statistics"
    SET total_buy         = COALESCE(total_buy, 0) + COALESCE(NEW.buy, 0),
        total_sell        = COALESCE(total_sell, 0) + COALESCE(NEW.sell, 0),
        total_invested    = COALESCE(total_invested, 0) + COALESCE(NEW.buy, 0) * NEW.usd,
        total_realized    = COALESCE(total_realized, 0) + COALESCE(NEW.sell, 0) * NEW.usd,
        holdings          = COALESCE(holdings, 0) + (COALESCE(NEW.buy, 0) - COALESCE(NEW.sell, 0)),
        transaction_count = transaction_count + 1,
        last_updated      = NOW()
    WHERE coin_id = NEW.coin_id
      AND user_id = NEW.user_id;

    IF NOT FOUND THEN
        INSERT INTO "coin_statistics" (user_id, coin_id, total_buy, total_sell, total_invested, 
                                        total_realized, holdings, transaction_count, last_updated)
        VALUES (NEW.user_id,
                NEW.coin_id,
                COALESCE(NEW.buy, 0),
                COALESCE(NEW.sell, 0),
                COALESCE(NEW.buy, 0) * NEW.usd,
                COALESCE(NEW.sell, 0) * NEW.usd,
                COALESCE(NEW.buy, 0) - COALESCE(NEW.sell, 0),
                1,
                NOW());
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
            """
        )
    )

    # Створення тригера
    await session.execute(
        text(
            """
CREATE TRIGGER after_coin_transaction
    AFTER INSERT OR UPDATE
    ON "coin_transactions"
    FOR EACH ROW
EXECUTE FUNCTION update_coin_statistics();
            """
        )
    )

    await session.commit()
