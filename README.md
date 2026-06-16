# 📊 Sales Intelligence Hub
### Branch-Based Sales Management System — MySQL · Python · Streamlit

A multi-branch sales & financial tracking system. It stores branch-wise sales,
tracks split payments, **auto-calculates received and pending amounts using
database triggers + a generated column**, and exposes everything through a
role-based Streamlit dashboard (Super Admin / Admin).

---

## 1. Project Structure

```
sales_hub/
├── 01_schema.sql          # database, 4 tables, constraints, generated column
├── 02_triggers.sql        # AFTER INSERT/UPDATE/DELETE triggers on payment_splits
├── 03_sample_data.sql     # 5 branches, 6 users, 24 sales, 29 payment splits
├── 04_queries.sql         # all 20 analytical SQL queries
├── db_connection.py       # MySQL connection helper + password hashing
├── app.py                 # Streamlit dashboard (login, RBAC, reports)
├── requirements.txt       # Python dependencies
├── .streamlit/
│   └── secrets.toml.example
└── README.md
```

---

## 2. Database Design

Four normalised tables.

| Table | Key columns | Notes |
|-------|-------------|-------|
| `branches` | `branch_id` (PK) | branch master |
| `users` | `user_id` (PK), `email` UNIQUE, `branch_id` (FK) | login + role; Super Admin has `branch_id = NULL` |
| `customer_sales` | `sale_id` (PK), `branch_id` (FK), `mobile_number` UNIQUE | **main financial table** |
| `payment_splits` | `payment_id` (PK), `sale_id` (FK) | many payments per sale |

**Relationships**

```
branches (1) ─── (many) customer_sales (1) ─── (many) payment_splits
branches (1) ─── (many) users
```

**Key design points**
- `pending_amount` is a **STORED generated column**: `gross_sales - received_amount`. It is never written manually.
- `received_amount` is **only ever updated by triggers** — never by hand (a core project rule).
- `status ENUM('Open','Close')` auto-flips to `Close` once a sale is fully paid.
- `CHECK` constraints enforce valid products (`DS/DA/BA/FSD`) and methods (`Cash/UPI/Card`).
- Passwords stored as **SHA-256 hashes** (`SHA2(pw,256)` in SQL, `hashlib.sha256` in Python).

> Requires **MySQL 8.0.16+** (for `CHECK` constraint enforcement + stored generated columns).

---

## 3. Automation Logic (Triggers)

Triggers live on `payment_splits`. On every **INSERT / UPDATE / DELETE** they:

1. Re-sum `amount_paid` for the affected `sale_id`.
2. Write that total into `customer_sales.received_amount`.
3. Flip `status` to `Close` when `received_amount >= gross_sales`, else `Open`.

`pending_amount` recomputes automatically (generated column). The brief only
requires `AFTER INSERT`; `UPDATE`/`DELETE` are added so edits and reversals stay
consistent.

---

## 4. Setup & Run

```bash
# 1. Create DB + load everything (run in order)
mysql -u root -p < 01_schema.sql
mysql -u root -p < 02_triggers.sql
mysql -u root -p < 03_sample_data.sql

# 2. Configure DB access for the app
#    Either edit DEFAULTS in db_connection.py,
#    or copy .streamlit/secrets.toml.example -> .streamlit/secrets.toml and fill it in.

# 3. Install deps + run
pip install -r requirements.txt
streamlit run app.py
```

Quick connectivity test: `python db_connection.py`

---

## 5. Demo Login Credentials

| Username | Password | Role | Scope |
|----------|----------|------|-------|
| `superadmin` | `admin123` | Super Admin | all branches |
| `chennai_admin` | `chennai123` | Admin | Chennai |
| `delhi_admin` | `delhi123` | Admin | Delhi |
| `bangalore_admin` | `bangalore123` | Admin | Bangalore |
| `mumbai_admin` | `mumbai123` | Admin | Mumbai |
| `hyderabad_admin` | `hyderabad123` | Admin | Hyderabad |

---

## 6. Role-Based Access Control

- **Super Admin** — sees & adds data for **all** branches, plus the SQL Console.
- **Admin** — sees & adds data **only for their own branch**; every query is
  scoped with `WHERE branch_id = <their branch>`.
- Session-based login (`st.session_state`), logout button, and no page renders
  until authentication succeeds.

---

## 7. Business Use Cases — Coverage Checklist

Every business case from the brief is implemented. ✅

| # | Business Use Case | Where it lives |
|---|-------------------|----------------|
| 1 | Track branch-wise sales performance | Sales Report (branch filter) + Insights → branch comparison · `Q13` |
| 2 | Monitor received vs pending payments | Dashboard KPIs + donut, Sales Report → Pending Payments · `Q7/Q8/Q16` |
| 3 | Auto-calculate net revenue after deductions | Generated column `pending_amount` + triggers; "Received (Net Revenue)" KPI |
| 4 | Manage split payments for customers | `payment_splits` table + **Add Payment Split** page |
| 5 | Identify high-performing branches | Insights → top-branch banner · `Q18` |
| 6 | Analyze sales trends by date | Insights → monthly trend line · `Q19` |
| 7 | Monitor revenue-sharing payouts | **Revenue Sharing** page (configurable % on collected revenue) |
| 8 | Generate financial summaries for decisions | Dashboard KPIs + Insights (method analysis, comparisons) · `Q6/Q10/Q20` |

> **Note on "net revenue / net sales":** the supplied schema has no discount/deduction
> column, so *net revenue* is interpreted as the **received (actually collected)
> amount** driven by the triggers, with `pending_amount` as the outstanding balance.
> *Revenue sharing* is modelled as a configurable percentage of each branch's
> collected revenue, since the brief lists it as a use case without a dedicated table.

---

## 8. Dashboard Features

- 🔐 Secure login + logout, session management
- ➕ Add sales entry (Super Admin: any branch · Admin: own branch)
- 💵 Add payment split (triggers auto-update received/pending/status)
- 📄 Sales report with branch / status / product filters + pending view
- 📊 Financial KPI summary (total sales, gross, received, pending, collection %)
- 📈 Insights: branch comparison, received vs pending, monthly trend, payment-method mix
- 🤝 Revenue-sharing payout modeller
- 🗃️ SQL Console running predefined queries (Super Admin)

---

## 9. SQL Queries

`04_queries.sql` contains all **20** queries (minimum required is 15):
5 basic · 5 aggregation · 5 join-based · 5 financial-tracking. A subset is also
runnable live from the dashboard's **SQL Console**.

---

## 10. Demo Data Snapshot

5 branches · 24 sales · 29 payment splits.

| Metric | Value |
|--------|-------|
| Total gross sales | ₹9,34,000 |
| Total received | ₹5,89,000 |
| Total pending | ₹3,45,000 |
| Collection % | 63.1% |
| Closed sales | 10 |
| Open sales | 14 (4 with no payment yet) |
| Cash / UPI / Card collected | ₹1,43,000 / ₹2,70,000 / ₹1,76,000 |

All `received_amount`/`pending_amount`/`status` values above are produced by the
**triggers** firing on the payment inserts — none are typed manually.

---

## 11. Evaluation-Metric Mapping

| Metric | Addressed by |
|--------|--------------|
| Database normalization | 4 normalised tables, FKs, no redundancy |
| Trigger implementation | INSERT/UPDATE/DELETE triggers on `payment_splits` |
| Accurate financial calculations | generated column + trigger re-summing |
| SQL query optimization | indexes on `branch_id`, `date`, `sale_id`; grouped aggregates |
| Joins & aggregations | `04_queries.sql` Q11–Q20 |
| Streamlit functionality & UI | `app.py` (RBAC, forms, filters, charts) |
| Clean Python structure | separated `db_connection.py`, helper functions |
| Business insight interpretation | Insights & Revenue-Sharing pages |

---

## 12. Tech Stack

`Python` · `MySQL 8` · `SQL Triggers` · `Generated Columns` · `Streamlit` ·
`Plotly` · `pandas`
