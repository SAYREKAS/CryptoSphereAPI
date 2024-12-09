CREATE OR REPLACE FUNCTION calculate_missing_transaction_data()
    RETURNS TRIGGER AS
$$
BEGIN
    IF COALESCE(NEW.paid, 0) = 0 THEN
        IF COALESCE(NEW.buy, 0) > 0 THEN
            NEW.paid := NEW.buy * COALESCE(NEW.average_price, 0);
        ELSIF COALESCE(NEW.sell, 0) > 0 THEN
            NEW.paid := NEW.sell * COALESCE(NEW.average_price, 0);
        END IF;
    END IF;

    IF COALESCE(NEW.average_price, 0) = 0 THEN
        IF COALESCE(NEW.buy, 0) > 0 THEN
            NEW.average_price := NEW.paid / NEW.buy;
        ELSIF COALESCE(NEW.sell, 0) > 0 THEN
            NEW.average_price := NEW.paid / NEW.sell;
        END IF;
    END IF;

    IF COALESCE(NEW.paid, 0) = 0 OR COALESCE(NEW.average_price, 0) = 0 THEN
        RAISE EXCEPTION 'Cannot calculate missing data: buy/sell, paid, or average_price values are invalid.';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER before_insert_or_update_coin_transactions
    BEFORE INSERT OR UPDATE
    ON "coin_transactions"
    FOR EACH ROW
EXECUTE FUNCTION calculate_missing_transaction_data();