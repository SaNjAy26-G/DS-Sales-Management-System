-- ============================================================
--  SALES INTELLIGENCE HUB
--  File 02 : AUTOMATION LOGIC (TRIGGERS)
--
--  Rule of the project: received_amount is NEVER updated by hand.
--  Every time a payment row is inserted / updated / deleted in
--  payment_splits, the trigger re-sums the payments for that sale,
--  writes it to customer_sales.received_amount, and flips the
--  status to 'Close' once the sale is fully paid.
--
--  pending_amount needs no trigger -- it is a GENERATED column and
--  recomputes automatically whenever received_amount changes.
-- ============================================================

USE sales_management_system;

DROP TRIGGER IF EXISTS trg_payment_after_insert;
DROP TRIGGER IF EXISTS trg_payment_after_update;
DROP TRIGGER IF EXISTS trg_payment_after_delete;

DELIMITER $$

-- ---- AFTER INSERT (mandatory) -------------------------------
CREATE TRIGGER trg_payment_after_insert
AFTER INSERT ON payment_splits
FOR EACH ROW
BEGIN
    UPDATE customer_sales cs
    SET cs.received_amount = (
            SELECT COALESCE(SUM(ps.amount_paid), 0)
            FROM payment_splits ps
            WHERE ps.sale_id = NEW.sale_id
        ),
        cs.status = CASE
            WHEN (SELECT COALESCE(SUM(ps.amount_paid), 0)
                  FROM payment_splits ps
                  WHERE ps.sale_id = NEW.sale_id) >= cs.gross_sales
            THEN 'Close' ELSE 'Open'
        END
    WHERE cs.sale_id = NEW.sale_id;
END$$

-- ---- AFTER UPDATE (keeps totals correct on edits) -----------
CREATE TRIGGER trg_payment_after_update
AFTER UPDATE ON payment_splits
FOR EACH ROW
BEGIN
    UPDATE customer_sales cs
    SET cs.received_amount = (
            SELECT COALESCE(SUM(ps.amount_paid), 0)
            FROM payment_splits ps
            WHERE ps.sale_id = NEW.sale_id
        ),
        cs.status = CASE
            WHEN (SELECT COALESCE(SUM(ps.amount_paid), 0)
                  FROM payment_splits ps
                  WHERE ps.sale_id = NEW.sale_id) >= cs.gross_sales
            THEN 'Close' ELSE 'Open'
        END
    WHERE cs.sale_id = NEW.sale_id;
END$$

-- ---- AFTER DELETE (keeps totals correct on removals) --------
CREATE TRIGGER trg_payment_after_delete
AFTER DELETE ON payment_splits
FOR EACH ROW
BEGIN
    UPDATE customer_sales cs
    SET cs.received_amount = (
            SELECT COALESCE(SUM(ps.amount_paid), 0)
            FROM payment_splits ps
            WHERE ps.sale_id = OLD.sale_id
        ),
        cs.status = CASE
            WHEN (SELECT COALESCE(SUM(ps.amount_paid), 0)
                  FROM payment_splits ps
                  WHERE ps.sale_id = OLD.sale_id) >= cs.gross_sales
            THEN 'Close' ELSE 'Open'
        END
    WHERE cs.sale_id = OLD.sale_id;
END$$

DELIMITER ;
