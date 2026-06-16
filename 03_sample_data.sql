-- ============================================================
--  SALES INTELLIGENCE HUB
--  File 03 : SAMPLE / DEMO DATA
--
--  IMPORTANT: customer_sales rows are inserted with received_amount
--  left at its DEFAULT of 0. The received_amount and pending_amount
--  values you see afterwards are produced ENTIRELY by the triggers
--  firing on the payment_splits inserts below -- nothing is typed by hand.
--
--  Passwords are stored as SHA-256 hashes (see README for plain text).
-- ============================================================

USE sales_management_system;

-- ---------------- branches ----------------
INSERT INTO branches (branch_name, branch_admin_name) VALUES
('Chennai',   'Suriya Naraiyanan'),
('Delhi',     'Rohit Sharma'),
('Bangalore', 'Anitha Reddy'),
('Mumbai',    'Imran Khan'),
('Hyderabad', 'Kavya Nair');

-- ---------------- users ----------------
-- Super Admin has branch_id NULL (all-branch access)
INSERT INTO users (username, password, branch_id, role, email) VALUES
('superadmin',      SHA2('admin123',     256), NULL, 'Super Admin', 'superadmin@saleshub.com'),
('chennai_admin',   SHA2('chennai123',   256), 1,    'Admin',       'chennai@saleshub.com'),
('delhi_admin',     SHA2('delhi123',     256), 2,    'Admin',       'delhi@saleshub.com'),
('bangalore_admin', SHA2('bangalore123', 256), 3,    'Admin',       'bangalore@saleshub.com'),
('mumbai_admin',    SHA2('mumbai123',    256), 4,    'Admin',       'mumbai@saleshub.com'),
('hyderabad_admin', SHA2('hyderabad123', 256), 5,    'Admin',       'hyderabad@saleshub.com');

-- ---------------- customer_sales ----------------
-- (received_amount/pending_amount intentionally omitted -> driven by triggers)
INSERT INTO customer_sales (branch_id, date, name, mobile_number, product_name, gross_sales) VALUES
(1, '2024-01-12', 'Arjun Menon',    '9000000001', 'DS',  45000.00),
(1, '2024-02-09', 'Divya Krishnan', '9000000002', 'DA',  35000.00),
(1, '2024-03-15', 'Saravanan R',    '9000000003', 'FSD', 40000.00),
(1, '2024-05-20', 'Meena Lakshmi',  '9000000004', 'BA',  30000.00),
(1, '2024-08-02', 'Karthik V',      '9000000005', 'DS',  45000.00),
(2, '2024-01-25', 'Rahul Verma',    '9000000006', 'FSD', 42000.00),
(2, '2024-03-11', 'Sneha Gupta',    '9000000007', 'DA',  36000.00),
(2, '2024-06-18', 'Aakash Jain',    '9000000008', 'DS',  46000.00),
(2, '2024-09-09', 'Pooja Singh',    '9000000009', 'BA',  31000.00),
(2, '2024-11-21', 'Vikram Nanda',   '9000000010', 'FSD', 40000.00),
(3, '2024-02-14', 'Nikhil Rao',     '9000000011', 'DS',  47000.00),
(3, '2024-04-05', 'Shreya Iyer',    '9000000012', 'FSD', 41000.00),
(3, '2024-07-30', 'Manoj Kumar',    '9000000013', 'DA',  34000.00),
(3, '2024-10-16', 'Deepa Shetty',   '9000000014', 'BA',  30000.00),
(3, '2024-12-08', 'Ganesh Hegde',   '9000000015', 'DS',  45000.00),
(4, '2024-01-19', 'Farhan Ali',     '9000000016', 'DA',  35000.00),
(4, '2024-04-22', 'Priya Nair',     '9000000017', 'FSD', 43000.00),
(4, '2024-07-07', 'Rohan Desai',    '9000000018', 'DS',  46000.00),
(4, '2024-10-29', 'Sana Shaikh',    '9000000019', 'BA',  32000.00),
(5, '2024-02-27', 'Teja Reddy',     '9000000020', 'FSD', 40000.00),
(5, '2024-05-13', 'Lavanya M',      '9000000021', 'DA',  35000.00),
(5, '2024-08-24', 'Akhil Varma',    '9000000022', 'DS',  45000.00),
(5, '2025-01-10', 'Bhavana K',      '9000000023', 'BA',  30000.00),
(5, '2025-02-18', 'Charan Tej',     '9000000024', 'FSD', 41000.00);

-- ---------------- payment_splits ----------------
-- Fully paid sales -> status auto-flips to 'Close'
-- Partially paid    -> remain 'Open' with a pending balance
-- Sales 5,10,15,24 have NO payments -> fully pending
INSERT INTO payment_splits (sale_id, payment_date, amount_paid, payment_method) VALUES
-- sale 1 : 45000 fully paid in two splits
(1,  '2024-01-12', 25000.00, 'UPI'),
(1,  '2024-01-20', 20000.00, 'Cash'),
-- sale 2 : partial
(2,  '2024-02-10', 15000.00, 'Card'),
-- sale 3 : fully paid single
(3,  '2024-03-16', 40000.00, 'UPI'),
-- sale 4 : partial in two splits
(4,  '2024-05-21', 10000.00, 'Cash'),
(4,  '2024-06-01',  5000.00, 'UPI'),
-- sale 6 : fully paid two splits
(6,  '2024-01-26', 20000.00, 'Card'),
(6,  '2024-02-05', 22000.00, 'UPI'),
-- sale 7 : partial
(7,  '2024-03-12', 18000.00, 'UPI'),
-- sale 8 : fully paid
(8,  '2024-06-19', 46000.00, 'Cash'),
-- sale 9 : partial two splits
(9,  '2024-09-10', 10000.00, 'Card'),
(9,  '2024-09-25',  6000.00, 'Cash'),
-- sale 11 : fully paid two splits
(11, '2024-02-15', 25000.00, 'UPI'),
(11, '2024-02-28', 22000.00, 'Card'),
-- sale 12 : partial
(12, '2024-04-06', 20000.00, 'Cash'),
-- sale 13 : fully paid
(13, '2024-07-31', 34000.00, 'UPI'),
-- sale 14 : partial two splits
(14, '2024-10-17', 12000.00, 'Card'),
(14, '2024-11-02',  8000.00, 'UPI'),
-- sale 16 : fully paid
(16, '2024-01-20', 35000.00, 'Card'),
-- sale 17 : partial
(17, '2024-04-23', 23000.00, 'UPI'),
-- sale 18 : fully paid two splits
(18, '2024-07-08', 26000.00, 'Cash'),
(18, '2024-07-20', 20000.00, 'UPI'),
-- sale 19 : partial
(19, '2024-10-30', 12000.00, 'Card'),
-- sale 20 : fully paid
(20, '2024-02-28', 40000.00, 'UPI'),
-- sale 21 : partial two splits
(21, '2024-05-14', 15000.00, 'Cash'),
(21, '2024-05-30',  5000.00, 'Card'),
-- sale 22 : fully paid
(22, '2024-08-25', 45000.00, 'Card'),
-- sale 23 : partial
(23, '2025-01-11', 10000.00, 'UPI');
