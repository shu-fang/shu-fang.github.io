import sqlite3

conn = sqlite3.connect("accounts.sqlite")

cursor = conn.cursor()
sql_query = """ CREATE TABLE IF NOT EXISTS accounts (
    name text NOT NULL,
    type text NOT NULL DEFAULT "unknown",
    tax_status text NOT NULL DEFAULT "unknown"
)"""
cursor.execute(sql_query)
