"""
db_connection.py
-----------------
Central MySQL connection helper for the Sales Intelligence Hub.

Credentials are read from Streamlit secrets (.streamlit/secrets.toml) when
available, otherwise from environment variables, otherwise from the DEFAULTS
below. Edit DEFAULTS or create secrets.toml to match your local MySQL.
"""

import os
import hashlib
import mysql.connector
from mysql.connector import Error

# ---- Default local credentials (override via secrets.toml or env vars) ----
DEFAULTS = {
    "host": "localhost",
    "user": "root",
    "password": "",          # <-- put your MySQL root password here
    "database": "sales_management_system",
    "port": 3306,
}


def _config():
    cfg = dict(DEFAULTS)
    # 1) Streamlit secrets (optional)
    try:
        import streamlit as st
        if "mysql" in st.secrets:
            cfg.update(dict(st.secrets["mysql"]))
    except Exception:
        pass
    # 2) Environment variables (optional)
    env_map = {
        "host": "DB_HOST", "user": "DB_USER", "password": "DB_PASSWORD",
        "database": "DB_NAME", "port": "DB_PORT",
    }
    for key, env in env_map.items():
        if os.getenv(env):
            cfg[key] = os.getenv(env)
    cfg["port"] = int(cfg["port"])
    return cfg


def get_connection():
    """Return a live MySQL connection (caller is responsible for closing)."""
    try:
        conn = mysql.connector.connect(**_config())
        return conn
    except Error as e:
        raise RuntimeError(f"Could not connect to MySQL: {e}")


def run_query(sql, params=None, fetch=True):
    """
    Run a query. For SELECTs returns (columns, rows).
    For INSERT/UPDATE/DELETE commits and returns lastrowid.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        if fetch:
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description] if cur.description else []
            return cols, rows
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def hash_password(plain: str) -> str:
    """SHA-256 hex digest -- matches MySQL SHA2(<pw>, 256) used in seed data."""
    return hashlib.sha256(plain.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    # Quick connectivity smoke test
    try:
        cols, rows = run_query("SELECT DATABASE(), VERSION();")
        print("Connected OK ->", rows)
    except Exception as exc:
        print("Connection failed:", exc)
