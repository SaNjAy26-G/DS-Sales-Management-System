"""
app.py  --  Sales Intelligence Hub
Branch-Based Sales Management System (MySQL + Python + Streamlit)

Run with:  streamlit run app.py
"""

import datetime
import pandas as pd
import plotly.express as px
import streamlit as st

from db_connection import get_connection, run_query, hash_password

# ----------------------------------------------------------------------
# Page config
# ----------------------------------------------------------------------
st.set_page_config(page_title="Sales Intelligence Hub", page_icon="📊", layout="wide")

PRODUCTS = ["DS", "DA", "BA", "FSD"]
METHODS = ["Cash", "UPI", "Card"]

# Predefined queries exposed in the SQL console (mandatory feature)
PREDEFINED_QUERIES = {
    "Q1  All customer_sales": "SELECT * FROM customer_sales;",
    "Q2  All branches": "SELECT * FROM branches;",
    "Q3  All payment_splits": "SELECT * FROM payment_splits;",
    "Q4  Sales with status = Open": "SELECT * FROM customer_sales WHERE status='Open';",
    "Q6  Total gross sales": "SELECT SUM(gross_sales) AS total_gross_sales FROM customer_sales;",
    "Q7  Total received amount": "SELECT SUM(received_amount) AS total_received FROM customer_sales;",
    "Q8  Total pending amount": "SELECT SUM(pending_amount) AS total_pending FROM customer_sales;",
    "Q9  Sales count per branch":
        "SELECT b.branch_name, COUNT(cs.sale_id) AS total_sales "
        "FROM branches b LEFT JOIN customer_sales cs ON b.branch_id=cs.branch_id "
        "GROUP BY b.branch_id, b.branch_name ORDER BY total_sales DESC;",
    "Q10 Average gross sales": "SELECT ROUND(AVG(gross_sales),2) AS avg_gross_sales FROM customer_sales;",
    "Q13 Branch-wise total gross sales":
        "SELECT b.branch_name, SUM(cs.gross_sales) AS branch_gross_sales "
        "FROM branches b JOIN customer_sales cs ON b.branch_id=cs.branch_id "
        "GROUP BY b.branch_id, b.branch_name ORDER BY branch_gross_sales DESC;",
    "Q16 Pending amount > 5000":
        "SELECT sale_id, name AS customer_name, gross_sales, received_amount, pending_amount "
        "FROM customer_sales WHERE pending_amount > 5000 ORDER BY pending_amount DESC;",
    "Q17 Top 3 highest gross sales":
        "SELECT sale_id, name AS customer_name, product_name, gross_sales "
        "FROM customer_sales ORDER BY gross_sales DESC LIMIT 3;",
    "Q18 Branch with highest gross sales":
        "SELECT b.branch_name, SUM(cs.gross_sales) AS total_gross_sales "
        "FROM branches b JOIN customer_sales cs ON b.branch_id=cs.branch_id "
        "GROUP BY b.branch_id, b.branch_name ORDER BY total_gross_sales DESC LIMIT 1;",
    "Q19 Monthly sales summary":
        "SELECT DATE_FORMAT(date,'%Y-%m') AS ym, COUNT(sale_id) AS num_sales, "
        "SUM(gross_sales) AS monthly_gross FROM customer_sales "
        "GROUP BY DATE_FORMAT(date,'%Y-%m') ORDER BY ym;",
    "Q20 Payment method-wise collection":
        "SELECT payment_method, COUNT(*) AS txns, SUM(amount_paid) AS total_collected "
        "FROM payment_splits GROUP BY payment_method ORDER BY total_collected DESC;",
}


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def fetch_df(sql, params=None):
    cols, rows = run_query(sql, params)
    df = pd.DataFrame(rows, columns=cols)
    for c in df.columns:
        if df[c].dtype == object:
            df[c] = pd.to_numeric(df[c], errors="ignore")
    return df


def branch_clause(prefix="cs"):
    """Return (where_clause, params) scoped to the logged-in user's role."""
    user = st.session_state.user
    if user["role"] == "Super Admin":
        return "", []
    return f" WHERE {prefix}.branch_id = %s ", [user["branch_id"]]


def authenticate(username, password):
    sql = (
        "SELECT u.user_id, u.username, u.role, u.branch_id, b.branch_name "
        "FROM users u LEFT JOIN branches b ON u.branch_id=b.branch_id "
        "WHERE u.username=%s AND u.password=%s"
    )
    cols, rows = run_query(sql, (username, hash_password(password)))
    if rows:
        return dict(zip(cols, rows[0]))
    return None


def get_branches_for_user():
    user = st.session_state.user
    if user["role"] == "Super Admin":
        df = fetch_df("SELECT branch_id, branch_name FROM branches ORDER BY branch_name;")
    else:
        df = fetch_df(
            "SELECT branch_id, branch_name FROM branches WHERE branch_id=%s",
            (user["branch_id"],),
        )
    return df


# ----------------------------------------------------------------------
# Login screen
# ----------------------------------------------------------------------
def login_screen():
    st.title("📊 Sales Intelligence Hub")
    st.caption("Branch-Based Sales Management System")
    st.subheader("🔐 Login")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

    if submitted:
        if not username or not password:
            st.warning("Enter both username and password.")
            return
        try:
            user = authenticate(username.strip(), password)
        except Exception as e:
            st.error(f"Database error: {e}")
            return
        if user:
            st.session_state.logged_in = True
            st.session_state.user = user
            st.rerun()
        else:
            st.error("Invalid credentials.")

    with st.expander("Demo credentials"):
        st.markdown(
            "- **Super Admin** -> `superadmin` / `admin123`\n"
            "- **Chennai Admin** -> `chennai_admin` / `chennai123`\n"
            "- **Delhi Admin** -> `delhi_admin` / `delhi123`\n"
            "- **Bangalore Admin** -> `bangalore_admin` / `bangalore123`\n"
            "- **Mumbai Admin** -> `mumbai_admin` / `mumbai123`\n"
            "- **Hyderabad Admin** -> `hyderabad_admin` / `hyderabad123`"
        )


# ----------------------------------------------------------------------
# Page: KPI dashboard  (BC2, BC3, BC8)
# ----------------------------------------------------------------------
def page_dashboard():
    st.header("Financial KPI Summary")
    where, params = branch_clause("cs")
    df = fetch_df(
        f"SELECT SUM(gross_sales) gross, SUM(received_amount) received, "
        f"SUM(pending_amount) pending, COUNT(*) sales FROM customer_sales cs {where}",
        params,
    )
    gross = float(df["gross"].iloc[0] or 0)
    received = float(df["received"].iloc[0] or 0)
    pending = float(df["pending"].iloc[0] or 0)
    sales = int(df["sales"].iloc[0] or 0)
    collection_pct = (received / gross * 100) if gross else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Sales", f"{sales}")
    c2.metric("Gross Sales", f"₹{gross:,.0f}")
    c3.metric("Received (Net Revenue)", f"₹{received:,.0f}")
    c4.metric("Pending", f"₹{pending:,.0f}")
    c5.metric("Collection %", f"{collection_pct:.1f}%")

    st.divider()
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Received vs Pending")
        donut = pd.DataFrame(
            {"Type": ["Received", "Pending"], "Amount": [received, pending]}
        )
        st.plotly_chart(
            px.pie(donut, names="Type", values="Amount", hole=0.5),
            use_container_width=True,
        )
    with col_b:
        st.subheader("Sales Status (Open vs Close)")
        sdf = fetch_df(
            f"SELECT status, COUNT(*) cnt FROM customer_sales cs {where} GROUP BY status",
            params,
        )
        if not sdf.empty:
            st.plotly_chart(
                px.bar(sdf, x="status", y="cnt", color="status", text="cnt"),
                use_container_width=True,
            )


# ----------------------------------------------------------------------
# Page: Add Sale
# ----------------------------------------------------------------------
def page_add_sale():
    st.header("➕ Add New Sales Entry")
    branches = get_branches_for_user()
    user = st.session_state.user

    with st.form("add_sale"):
        if user["role"] == "Super Admin":
            branch_name = st.selectbox("Branch", branches["branch_name"])
            branch_id = int(
                branches.loc[branches["branch_name"] == branch_name, "branch_id"].iloc[0]
            )
        else:
            branch_id = int(user["branch_id"])
            st.info(f"Branch: **{user['branch_name']}** (your assigned branch)")

        date = st.date_input("Sale Date", value=datetime.date.today())
        name = st.text_input("Customer Name")
        mobile = st.text_input("Mobile Number (unique)")
        product = st.selectbox("Product", PRODUCTS)
        gross = st.number_input("Gross Sales (₹)", min_value=0.0, step=1000.0)
        submitted = st.form_submit_button("Save Sale")

    if submitted:
        if not name or not mobile or gross <= 0:
            st.warning("Customer name, mobile and a positive gross amount are required.")
            return
        try:
            run_query(
                "INSERT INTO customer_sales (branch_id, date, name, mobile_number, "
                "product_name, gross_sales) VALUES (%s,%s,%s,%s,%s,%s)",
                (branch_id, date, name.strip(), mobile.strip(), product, gross),
                fetch=False,
            )
            st.success(f"Sale recorded for {name}. Pending = ₹{gross:,.0f} (no payment yet).")
        except Exception as e:
            st.error(f"Could not save (duplicate mobile?): {e}")


# ----------------------------------------------------------------------
# Page: Add Payment Split  (BC4)
# ----------------------------------------------------------------------
def page_add_payment():
    st.header("💵 Add Payment Split")
    where, params = branch_clause("cs")
    sales = fetch_df(
        f"SELECT cs.sale_id, cs.name, cs.gross_sales, cs.received_amount, "
        f"cs.pending_amount FROM customer_sales cs {where} "
        f"{'AND' if where else 'WHERE'} cs.status='Open' ORDER BY cs.sale_id",
        params,
    )
    if sales.empty:
        st.info("No open sales available for a payment in your scope.")
        return

    sales["label"] = sales.apply(
        lambda r: f"#{r.sale_id} · {r['name']} · pending ₹{float(r.pending_amount):,.0f}",
        axis=1,
    )
    with st.form("add_pay"):
        choice = st.selectbox("Select Sale", sales["label"])
        sale_id = int(sales.loc[sales["label"] == choice, "sale_id"].iloc[0])
        pending = float(sales.loc[sales["label"] == choice, "pending_amount"].iloc[0])
        pdate = st.date_input("Payment Date", value=datetime.date.today())
        amount = st.number_input("Amount Paid (₹)", min_value=0.0, step=1000.0)
        method = st.selectbox("Payment Method", METHODS)
        submitted = st.form_submit_button("Record Payment")

    if submitted:
        if amount <= 0:
            st.warning("Amount must be greater than zero.")
            return
        if amount > pending:
            st.warning(f"Amount exceeds pending (₹{pending:,.0f}). Recording anyway.")
        try:
            run_query(
                "INSERT INTO payment_splits (sale_id, payment_date, amount_paid, "
                "payment_method) VALUES (%s,%s,%s,%s)",
                (sale_id, pdate, amount, method),
                fetch=False,
            )
            st.success(
                "Payment recorded. Trigger has auto-updated received_amount, "
                "pending_amount and status."
            )
        except Exception as e:
            st.error(f"Could not record payment: {e}")


# ----------------------------------------------------------------------
# Page: Sales Report  (BC1, BC2)
# ----------------------------------------------------------------------
def page_sales_report():
    st.header("📄 Sales Report")
    user = st.session_state.user
    base = (
        "SELECT cs.sale_id, b.branch_name, cs.date, cs.name AS customer, "
        "cs.mobile_number, cs.product_name, cs.gross_sales, cs.received_amount, "
        "cs.pending_amount, cs.status FROM customer_sales cs "
        "JOIN branches b ON cs.branch_id=b.branch_id"
    )
    where, params = branch_clause("cs")
    df = fetch_df(base + where + " ORDER BY cs.sale_id", params)

    # Filters
    cols = st.columns(3)
    if user["role"] == "Super Admin":
        bsel = cols[0].selectbox("Branch filter", ["All"] + sorted(df["branch_name"].unique()))
        if bsel != "All":
            df = df[df["branch_name"] == bsel]
    ssel = cols[1].selectbox("Status filter", ["All", "Open", "Close"])
    if ssel != "All":
        df = df[df["status"] == ssel]
    psel = cols[2].selectbox("Product filter", ["All"] + PRODUCTS)
    if psel != "All":
        df = df[df["product_name"] == psel]

    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption(f"{len(df)} record(s)")

    st.subheader("Pending Payments")
    pend = df[df["pending_amount"].astype(float) > 0][
        ["sale_id", "branch_name", "customer", "gross_sales", "received_amount", "pending_amount"]
    ]
    st.dataframe(pend, use_container_width=True, hide_index=True)


# ----------------------------------------------------------------------
# Page: Insights & Reporting  (BC1, BC5, BC6, BC8)
# ----------------------------------------------------------------------
def page_insights():
    st.header("📈 Insights & Reporting")
    where, params = branch_clause("cs")

    # Branch-wise comparison (BC1, BC5)
    st.subheader("Branch-wise Gross Sales Comparison")
    bdf = fetch_df(
        f"SELECT b.branch_name, SUM(cs.gross_sales) gross, SUM(cs.received_amount) received, "
        f"SUM(cs.pending_amount) pending FROM customer_sales cs "
        f"JOIN branches b ON cs.branch_id=b.branch_id {where} "
        f"GROUP BY b.branch_name ORDER BY gross DESC",
        params,
    )
    if not bdf.empty:
        st.plotly_chart(
            px.bar(bdf, x="branch_name", y="gross", color="branch_name", text="gross"),
            use_container_width=True,
        )
        top = bdf.iloc[0]
        st.success(f"🏆 Highest performing branch: **{top['branch_name']}** "
                   f"(₹{float(top['gross']):,.0f} gross)")

    # Received vs Pending per branch (BC2)
    st.subheader("Received vs Pending by Branch")
    if not bdf.empty:
        melt = bdf.melt(
            id_vars="branch_name", value_vars=["received", "pending"],
            var_name="Type", value_name="Amount",
        )
        st.plotly_chart(
            px.bar(melt, x="branch_name", y="Amount", color="Type", barmode="group"),
            use_container_width=True,
        )

    # Sales trend by month (BC6)
    st.subheader("Sales Trend (Monthly)")
    tdf = fetch_df(
        f"SELECT DATE_FORMAT(cs.date,'%Y-%m') ym, SUM(cs.gross_sales) gross "
        f"FROM customer_sales cs {where} GROUP BY ym ORDER BY ym",
        params,
    )
    if not tdf.empty:
        st.plotly_chart(px.line(tdf, x="ym", y="gross", markers=True), use_container_width=True)

    # Payment method analysis (BC8)
    st.subheader("Payment Method Analysis")
    pwhere = ""
    pparams = []
    user = st.session_state.user
    if user["role"] != "Super Admin":
        pwhere = " WHERE cs.branch_id=%s "
        pparams = [user["branch_id"]]
    mdf = fetch_df(
        f"SELECT ps.payment_method, SUM(ps.amount_paid) total, COUNT(*) txns "
        f"FROM payment_splits ps JOIN customer_sales cs ON ps.sale_id=cs.sale_id "
        f"{pwhere} GROUP BY ps.payment_method ORDER BY total DESC",
        pparams,
    )
    if not mdf.empty:
        c1, c2 = st.columns(2)
        c1.plotly_chart(px.pie(mdf, names="payment_method", values="total"),
                        use_container_width=True)
        c2.dataframe(mdf, use_container_width=True, hide_index=True)


# ----------------------------------------------------------------------
# Page: Revenue Sharing Payouts  (BC7)
# ----------------------------------------------------------------------
def page_revenue_sharing():
    st.header("🤝 Revenue-Sharing Payouts")
    st.caption(
        "Revenue sharing is computed on the **received** (actually collected) amount "
        "per branch. Adjust the share percentage to model branch payouts."
    )
    share = st.slider("Branch revenue share (%)", 0, 100, 20)
    where, params = branch_clause("cs")
    df = fetch_df(
        f"SELECT b.branch_name, b.branch_admin_name, SUM(cs.received_amount) received "
        f"FROM customer_sales cs JOIN branches b ON cs.branch_id=b.branch_id {where} "
        f"GROUP BY b.branch_name, b.branch_admin_name ORDER BY received DESC",
        params,
    )
    if df.empty:
        st.info("No collected revenue to share yet.")
        return
    df["received"] = df["received"].astype(float)
    df["payout"] = (df["received"] * share / 100).round(2)
    df["company_retains"] = (df["received"] - df["payout"]).round(2)
    st.dataframe(
        df.rename(columns={
            "branch_name": "Branch", "branch_admin_name": "Admin",
            "received": "Collected (₹)", "payout": f"Payout @ {share}% (₹)",
            "company_retains": "Company Retains (₹)",
        }),
        use_container_width=True, hide_index=True,
    )
    st.plotly_chart(px.bar(df, x="branch_name", y="payout", text="payout",
                           title="Payout by Branch"), use_container_width=True)


# ----------------------------------------------------------------------
# Page: SQL Console  (mandatory predefined queries)
# ----------------------------------------------------------------------
def page_sql_console():
    st.header("🗃️ SQL Console (Predefined Queries)")
    if st.session_state.user["role"] != "Super Admin":
        st.warning("SQL console is restricted to Super Admin (global, unfiltered data).")
        return
    choice = st.selectbox("Choose a query", list(PREDEFINED_QUERIES.keys()))
    sql = PREDEFINED_QUERIES[choice]
    st.code(sql, language="sql")
    if st.button("Run Query"):
        try:
            df = fetch_df(sql)
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.caption(f"{len(df)} row(s) returned")
        except Exception as e:
            st.error(f"Query failed: {e}")


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def main():
    if not st.session_state.get("logged_in"):
        login_screen()
        return

    user = st.session_state.user
    with st.sidebar:
        st.markdown(f"### 👤 {user['username']}")
        st.markdown(f"**Role:** {user['role']}")
        st.markdown(f"**Branch:** {user['branch_name'] or 'All branches'}")
        st.divider()
        pages = {
            "Dashboard": page_dashboard,
            "Add Sale": page_add_sale,
            "Add Payment Split": page_add_payment,
            "Sales Report": page_sales_report,
            "Insights & Reporting": page_insights,
            "Revenue Sharing": page_revenue_sharing,
        }
        if user["role"] == "Super Admin":
            pages["SQL Console"] = page_sql_console
        choice = st.radio("Navigate", list(pages.keys()))
        st.divider()
        if st.button("🚪 Logout"):
            st.session_state.clear()
            st.rerun()

    pages[choice]()


if __name__ == "__main__":
    main()
