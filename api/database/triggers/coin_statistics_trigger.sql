CREATE OR REPLACE FUNCTION coin_statistics_trigger()
    RETURNS TRIGGER AS
$$
BEGIN
    UPDATE "coin_statistics"
    SET total_buy          = total_buy + NEW.buy,
        total_sell         = total_sell + NEW.sell,
        total_invested     = total_invested + NEW.buy * NEW.average_price,
        total_realized     = total_realized + NEW.sell * NEW.average_price,
        total_invested_avg = CASE
                                 WHEN total_buy + NEW.buy > 0
                                     THEN (total_invested + NEW.buy * NEW.average_price) / (total_buy + NEW.buy)
                                 ELSE 0
            END,
        total_realized_avg = CASE
                                 WHEN total_sell + NEW.sell > 0
                                     THEN (total_realized + NEW.sell * NEW.average_price) / (total_sell + NEW.sell)
                                 ELSE 0
            END,
        holdings           = holdings + NEW.buy - NEW.sell,
        total_fee          = total_fee + NEW.fee,
        transaction_count  = transaction_count + 1,
        last_updated       = NOW()
    WHERE coin_id = NEW.coin_id
      AND user_id = NEW.user_id;

    IF NOT FOUND THEN
        INSERT INTO "coin_statistics" (user_id,
                                       coin_id,
                                       total_buy,
                                       total_sell,
                                       total_invested,
                                       total_realized,
                                       total_invested_avg,
                                       total_realized_avg,
                                       holdings,
                                       total_fee,
                                       transaction_count,
                                       last_updated)
        VALUES (NEW.user_id,
                NEW.coin_id,
                NEW.buy,
                NEW.sell,
                NEW.buy * NEW.average_price,
                NEW.sell * NEW.average_price,
                CASE
                    WHEN NEW.buy > 0 THEN NEW.average_price
                    ELSE 0
                    END,
                CASE
                    WHEN NEW.sell > 0 THEN NEW.average_price
                    ELSE 0
                    END,
                NEW.buy - NEW.sell,
                COALESCE(NEW.fee, 0),
                1,
                NOW());
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER after_coin_transaction
    AFTER INSERT OR UPDATE
    ON "coin_transactions"
    FOR EACH ROW
EXECUTE FUNCTION coin_statistics_trigger();