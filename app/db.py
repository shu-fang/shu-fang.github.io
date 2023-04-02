import sqlite3

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
            date DATE NOT NULL DEFAULT (DATE('now', 'localtime')),
            balances TEXT NOT NULL DEFAULT "0"
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

def update_account_balance(request):
    conn = db_connection('accounts')
    cursor = conn.cursor()
    # update account balance
    if request.method == 'POST':
        for account in request.form:
            if account.startswith('balance--'):
                name = account[9:]
                balance = request.form[account]
                if balance == "":
                    balance = '0'
                cursor.execute("UPDATE accounts SET balances=? WHERE name=?", (balance, name))
                conn.commit()

    cursor.execute("SELECT name, balances FROM accounts")
    conn.close()
make_entries_table()
make_accounts_table()