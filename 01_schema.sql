-- ============================================================
--  SALES INTELLIGENCE HUB  |  Branch-Based Sales Management System
--  File 01 : DATABASE + TABLE STRUCTURE
--  Engine  : MySQL 8.0.16+  (CHECK constraints + STORED generated columns)
-- ============================================================

DROP DATABASE IF EXISTS sales_management_system;
CREATE DATABASE sales_management_system;
USE sales_management_system;

-- ------------------------------------------------------------
-- 1. branches  -- master table for business branches
-- ------------------------------------------------------------
CREATE TABLE branches (
    branch_id          INT AUTO_INCREMENT PRIMARY KEY,
    branch_name        VARCHAR(100) NOT NULL,
    branch_admin_name  VARCHAR(100) NOT NULL
);

-- ------------------------------------------------------------
-- 2. users  -- login + role-based access (Super Admin / Admin)
--    Super Admin has branch_id = NULL (oversees every branch)
-- ------------------------------------------------------------
CREATE TABLE users (
    user_id    INT AUTO_INCREMENT PRIMARY KEY,
    username   VARCHAR(100) NOT NULL,
    password   VARCHAR(255) NOT NULL,                       -- stored as SHA-256 hex
    branch_id  INT NULL,
    role       ENUM('Super Admin','Admin') NOT NULL DEFAULT 'Admin',
    email      VARCHAR(255) NOT NULL UNIQUE,
    CONSTRAINT fk_users_branch
        FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
);

-- ------------------------------------------------------------
-- 3. customer_sales  -- main financial table
--    pending_amount  -> GENERATED column (auto = gross - received)
--    received_amount -> never edited by hand; updated only by triggers
-- ------------------------------------------------------------
CREATE TABLE customer_sales (
    sale_id          INT AUTO_INCREMENT PRIMARY KEY,
    branch_id        INT NOT NULL,
    date             DATE NOT NULL,
    name             VARCHAR(100) NOT NULL,
    mobile_number    VARCHAR(15) NOT NULL UNIQUE,
    product_name     VARCHAR(30) NOT NULL,
    gross_sales      DECIMAL(12,2) NOT NULL,
    received_amount  DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    pending_amount   DECIMAL(12,2)
                     GENERATED ALWAYS AS (gross_sales - received_amount) STORED,
    status           ENUM('Open','Close') NOT NULL DEFAULT 'Open',
    CONSTRAINT fk_sales_branch
        FOREIGN KEY (branch_id) REFERENCES branches(branch_id),
    CONSTRAINT chk_product
        CHECK (product_name IN ('DS','DA','BA','FSD')),
    CONSTRAINT chk_amounts
        CHECK (gross_sales >= 0 AND received_amount >= 0)
);

-- ------------------------------------------------------------
-- 4. payment_splits  -- one sale can have many partial payments
-- ------------------------------------------------------------
CREATE TABLE payment_splits (
    payment_id      INT AUTO_INCREMENT PRIMARY KEY,
    sale_id         INT NOT NULL,
    payment_date    DATE NOT NULL,
    amount_paid     DECIMAL(12,2) NOT NULL,
    payment_method  VARCHAR(50) NOT NULL,
    CONSTRAINT fk_payment_sale
        FOREIGN KEY (sale_id) REFERENCES customer_sales(sale_id)
        ON DELETE CASCADE,
    CONSTRAINT chk_method
        CHECK (payment_method IN ('Cash','UPI','Card')),
    CONSTRAINT chk_amount_paid
        CHECK (amount_paid > 0)
);

-- Helpful indexes for reporting
CREATE INDEX idx_sales_branch ON customer_sales(branch_id);
CREATE INDEX idx_sales_date   ON customer_sales(date);
CREATE INDEX idx_pay_sale     ON payment_splits(sale_id);
