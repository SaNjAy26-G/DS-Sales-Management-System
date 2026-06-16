-- ============================================================
--  SALES INTELLIGENCE HUB
--  File 04 : ANALYTICAL SQL QUERIES (all 20 answered)
--  Minimum required = 15. All 20 are provided below.
-- ============================================================

USE sales_management_system;

-- ============================================================
--  BASIC QUERIES
-- ============================================================

-- Q1. Retrieve all records from the customer_sales table.
SELECT * FROM customer_sales;

-- Q2. Retrieve all records from the branches table.
SELECT * FROM branches;

-- Q3. Retrieve all records from the payment_splits table.
SELECT * FROM payment_splits;

-- Q4. Display all sales with status = 'Open'.
SELECT * FROM customer_sales WHERE status = 'Open';

-- Q5. Retrieve all sales belonging to the Chennai branch.
SELECT cs.*
FROM customer_sales cs
JOIN branches b ON cs.branch_id = b.branch_id
WHERE b.branch_name = 'Chennai';

-- ============================================================
--  AGGREGATION QUERIES
-- ============================================================

-- Q6. Calculate the total gross sales across all branches.
SELECT SUM(gross_sales) AS total_gross_sales FROM customer_sales;

-- Q7. Calculate the total received amount across all sales.
SELECT SUM(received_amount) AS total_received_amount FROM customer_sales;

-- Q8. Calculate the total pending amount across all sales.
SELECT SUM(pending_amount) AS total_pending_amount FROM customer_sales;

-- Q9. Count the total number of sales per branch.
SELECT b.branch_name, COUNT(cs.sale_id) AS total_sales
FROM branches b
LEFT JOIN customer_sales cs ON b.branch_id = cs.branch_id
GROUP BY b.branch_id, b.branch_name
ORDER BY total_sales DESC;

-- Q10. Find the average gross sales amount.
SELECT ROUND(AVG(gross_sales), 2) AS avg_gross_sales FROM customer_sales;

-- ============================================================
--  JOIN-BASED QUERIES
-- ============================================================

-- Q11. Retrieve sales details along with the branch name.
SELECT cs.sale_id, b.branch_name, cs.name AS customer_name,
       cs.product_name, cs.gross_sales, cs.received_amount,
       cs.pending_amount, cs.status
FROM customer_sales cs
JOIN branches b ON cs.branch_id = b.branch_id
ORDER BY cs.sale_id;

-- Q12. Retrieve sales details along with total payment received (via payment_splits).
SELECT cs.sale_id, cs.name AS customer_name, cs.gross_sales,
       COALESCE(SUM(ps.amount_paid), 0) AS total_paid_via_splits,
       cs.pending_amount
FROM customer_sales cs
LEFT JOIN payment_splits ps ON cs.sale_id = ps.sale_id
GROUP BY cs.sale_id, cs.name, cs.gross_sales, cs.pending_amount
ORDER BY cs.sale_id;

-- Q13. Show branch-wise total gross sales (JOIN + GROUP BY).
SELECT b.branch_name, SUM(cs.gross_sales) AS branch_gross_sales
FROM branches b
JOIN customer_sales cs ON b.branch_id = cs.branch_id
GROUP BY b.branch_id, b.branch_name
ORDER BY branch_gross_sales DESC;

-- Q14. Display sales along with payment method used.
SELECT cs.sale_id, cs.name AS customer_name, ps.payment_date,
       ps.amount_paid, ps.payment_method
FROM customer_sales cs
JOIN payment_splits ps ON cs.sale_id = ps.sale_id
ORDER BY cs.sale_id, ps.payment_date;

-- Q15. Retrieve sales along with branch admin name.
SELECT cs.sale_id, cs.name AS customer_name, b.branch_name,
       b.branch_admin_name, cs.gross_sales, cs.status
FROM customer_sales cs
JOIN branches b ON cs.branch_id = b.branch_id
ORDER BY cs.sale_id;

-- ============================================================
--  FINANCIAL TRACKING QUERIES
-- ============================================================

-- Q16. Find sales where the pending amount is greater than 5000.
SELECT sale_id, name AS customer_name, gross_sales,
       received_amount, pending_amount, status
FROM customer_sales
WHERE pending_amount > 5000
ORDER BY pending_amount DESC;

-- Q17. Retrieve top 3 highest gross sales.
SELECT sale_id, name AS customer_name, product_name, gross_sales
FROM customer_sales
ORDER BY gross_sales DESC
LIMIT 3;

-- Q18. Find the branch with the highest total gross sales.
SELECT b.branch_name, SUM(cs.gross_sales) AS total_gross_sales
FROM branches b
JOIN customer_sales cs ON b.branch_id = cs.branch_id
GROUP BY b.branch_id, b.branch_name
ORDER BY total_gross_sales DESC
LIMIT 1;

-- Q19. Retrieve monthly sales summary (group by month & year).
SELECT YEAR(date) AS sales_year,
       MONTH(date) AS sales_month,
       DATE_FORMAT(date, '%Y-%m') AS year_month,
       COUNT(sale_id) AS num_sales,
       SUM(gross_sales) AS monthly_gross_sales
FROM customer_sales
GROUP BY YEAR(date), MONTH(date), DATE_FORMAT(date, '%Y-%m')
ORDER BY sales_year, sales_month;

-- Q20. Calculate payment method-wise total collection (Cash / UPI / Card).
SELECT payment_method,
       COUNT(*) AS num_transactions,
       SUM(amount_paid) AS total_collected
FROM payment_splits
GROUP BY payment_method
ORDER BY total_collected DESC;
