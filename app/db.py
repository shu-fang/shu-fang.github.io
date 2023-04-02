import sqlite3
from datetime import date 

def make_accounts_table():
    try:
        conn = sqlite3.connect("accounts.sqlite")
        cursor = conn.cursor()

        sql_query = """CREATE TABLE IF NOT EXISTS accounts (
            name text NOT NULL DEFAULT "unknown",
            type text NOT NULL DEFAULT "unknown",
            tax_status text NOT NULL DEFAULT "unknown",
            balances text NOT NULL DEFAULT "0"
        )"""

        cursor.execute(sql_query)
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Error creating accounts table: {e}")

def make_entries_table():
    try:
        conn = sqlite3.connect("entries.sqlite")
        cursor = conn.cursor()

        sql_query = """CREATE TABLE IF NOT EXISTS entries (
            date DATE NOT NULL DEFAULT (DATE('now', 'localtime'))
        )"""

        cursor.execute(sql_query)
        conn.commit()
        conn.close()

    except sqlite3.Error as e:
        print(f"Error creating table: {e}")

def delete_table(table):
    conn = sqlite3.connect(table + '.sqlite')
    cursor = conn.cursor()

    # retrieve the current column names
    cursor.execute("DROP TABLE IF EXISTS " + table)
    conn.commit()
    conn.close()

def db_connection(table):
    conn = None
    try:
        conn = sqlite3.connect(table + '.sqlite')
    except sqlite3.error as e:
        print(e)
    return conn

def add_entry(request):
    conn = sqlite3.connect("entries.sqlite")
    cursor = conn.cursor()

    accounts = request.form
    
    # Construct the SQL query to insert a new row into the 'entries' table
    columns = ', '.join(accounts.keys())
    values = ', '.join(['?'] * len(accounts))
    sql_query = f"INSERT INTO entries ({columns}, date) VALUES ({values}, ?)"
    params = list(accounts.values()) + [date.today()]
    print(list(accounts.values()))
    # Execute the SQL query and commit the changes to the database
    cursor.execute(sql_query, params)
    conn.commit()
    conn.close()

def update_account_balance(request):
    # update accounts table
    conn = db_connection('accounts')
    cursor = conn.cursor()
    add_entry(request)
    # update account balance
    if request.method == 'POST':
        for account in request.form:
            name = account
            balance = request.form[account]
            if balance == "":
                balance = '0'
            cursor.execute("UPDATE accounts SET balances=? WHERE name=?", (balance, name))
            conn.commit()

    cursor.execute("SELECT name, balances FROM accounts")
    conn.close()

make_entries_table()
make_accounts_table()