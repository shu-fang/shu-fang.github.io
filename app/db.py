import sqlite3

try:
    conn = sqlite3.connect("accounts.sqlite")
    cursor = conn.cursor()

    sql_query = """CREATE TABLE IF NOT EXISTS accounts (
        name text NOT NULL,
        type text NOT NULL DEFAULT "unknown",
        tax_status text NOT NULL DEFAULT "unknown",
        balances text NOT NULL DEFAULT "0"
    )"""

    cursor.execute(sql_query)
    conn.commit()
    conn.close()

except sqlite3.Error as e:
    print(f"Error creating table: {e}")


try:
    conn = sqlite3.connect("entries.sqlite")
    cursor = conn.cursor()

    sql_query = """CREATE TABLE IF NOT EXISTS entries (
        date DATE NOT NULL DEFAULT (DATE('now', 'localtime')),
        balances TEXT NOT NULL DEFAULT "0"
    )"""

    cursor.execute(sql_query)
    conn.commit()
    conn.close()

except sqlite3.Error as e:
    print(f"Error creating table: {e}")