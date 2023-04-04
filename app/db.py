import sqlite3
from datetime import date 

class Database:
    def __init__(self, name):
       self.name = name
       return
    
    def make_table(self, fields):
        try:
            conn = self.db_connection()
            cursor = conn.cursor()

            sql_query = f"""CREATE TABLE IF NOT EXISTS {self.name} (
                {', '.join(fields)}
            )"""
            print("added fields:", fields)
            cursor.execute(sql_query)
            conn.commit()
            conn.close()

        except sqlite3.Error as e:
            print(f"Error creating {self.name} table: {e}")

    def db_connection(self):
        conn = None
        try:
            conn = sqlite3.connect('database.sqlite')
        except sqlite3.error as e:
            print(e)
        return conn
    
    def delete_table(self):
        conn = self.db_connection()
        cursor = conn.cursor()

        # retrieve the current column names
        cursor.execute("DROP TABLE IF EXISTS " + self.name)
        conn.commit()
        conn.close()

    def wipe_table(self):
        return

    def format_balance(self, balance):
        if not balance.isdigit():
            balance = '0'
        else:
            balance = str(int(balance))
        return balance 

    def get_table_name(self):
        return self.name

    def get_column_names(self):
        conn = self.db_connection()
        cursor = conn.cursor()

        # Execute a query to get the column names of the table
        cursor.execute(f"PRAGMA table_info({self.name})")
        columns = [column[1] for column in cursor.fetchall()]

        conn.close()
        return columns
    
    def get_all_entries(self):
        conn = self.db_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {self.name}")
        rows = cursor.fetchall()
        conn.close()
        return rows
    
class AccountsDatabase(Database):
    def __init__(self):
        name = "accounts"
        super().__init__(name)
        self.make_table()

    def make_table(self):
        super().make_table([
            "name text NOT NULL DEFAULT 'unknown'",
            "type text NOT NULL DEFAULT 'unknown'",
            "tax_status text NOT NULL DEFAULT 'unknown'",
            "balances text NOT NULL DEFAULT '0'"
        ])
    
    def add_account(self, request):
        conn = self.db_connection()
        cursor = conn.cursor()
        new_name = request.form['accountName']
        new_type = "placeholder"
        new_tax_status = request.form['tax_status']
        sql = """INSERT INTO accounts (name, type, tax_status)
                    VALUES (?, ?, ?)"""
        cursor = cursor.execute(sql, (new_name, new_type, new_tax_status))
        conn.commit()
        conn.close()

    def update_account_balance(self, request):
        # update accounts table
        conn = self.db_connection()
        cursor = conn.cursor()

        # update account balance
        
        table = ""
        if 'pretax_submit' in request.form:
            table = "PretaxEntries"
        elif 'posttax_submit' in request.form:
            table = "PosttaxEntries"
        else:
            print("WARNING: request form not recognized")
        latest_date = cursor.execute(f"SELECT MAX(date) FROM {table}").fetchone()[0]
        
        entry_date = request.form['entry_date']
        if request.method == 'POST' and (not latest_date or entry_date >= latest_date):
            for account in request.form:
                name = account
                balance = self.format_balance(request.form[account])
                
                cursor.execute("UPDATE accounts SET balances=? WHERE name=?", (balance, name))
                conn.commit()

        cursor.execute("SELECT name, balances FROM accounts")
        conn.close()
    
    def get_latest_balances(self):
        conn = self.db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, balances, tax_status FROM accounts")
        
        accounts_data = cursor.fetchall()
        pretax_balance = sum([int(balance) for _, balance, tax_status in accounts_data if balance.isdigit() and tax_status == 'pre-tax'])
        posttax_balance = sum([int(balance) for _, balance, tax_status in accounts_data if balance.isdigit() and tax_status == 'post-tax'])
        return (pretax_balance, posttax_balance)
    
    def get_accounts(self, tax_status):
        conn = self.db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM accounts WHERE tax_status = '" + tax_status + "'")
        accounts = cursor.fetchall()
        conn.close()
        return accounts

    def wipe_table(self):
        self.delete_table()
        self.make_table()

class EntriesDatabase(Database):
    def __init__(self, name, columns = []):
        super().__init__(name)
        self.columns = columns
        self.make_table()

    def make_table(self):
        super().make_table([
            "date DATE NOT NULL DEFAULT (DATE('now', 'localtime'))",
            *self.columns
        ])
    
    def add_column(self, request):
        conn = self.db_connection()
        cursor = conn.cursor()
        # Construct a new SQL query to add a new column to the 'entries' table
        sql_query = f"ALTER TABLE {self.name} ADD COLUMN '{request.form['accountName']}' INTEGER DEFAULT 0"
        # Execute the SQL query and commit the changes to the database
        cursor.execute(sql_query)
        conn.commit()
        conn.close()

    def add_entry(self, request):
        conn = self.db_connection()
        cursor = conn.cursor()
        accounts = {key: value for key, value in request.form.items() if key not in ['entry_date', 'posttax_submit', 
                                                                                     'pretax_submit']}
        entry_date = request.form['entry_date']
        # Construct the SQL query to insert a new row into the 'entries' table
        columns = [f"`{col}`" for col in accounts.keys()]
        
        values = ', '.join(['?'] * len(accounts))
        
        sql_query = f"INSERT INTO {self.name} ({', '.join(columns)}, date) VALUES ({values}, ?)"
        params = [self.format_balance(value) for value in accounts.values()] + [entry_date]
        # Execute the SQL query and commit the changes to the database
        cursor.execute(sql_query, params)
        conn.commit()
        conn.close()

    def wipe_table(self):
        self.delete_table()
        self.make_table()
    
class PretaxEntriesTable(EntriesDatabase):
    def __init__(self):
        super().__init__("PretaxEntries")

class PosttaxEntriesTable(EntriesDatabase):
    def __init__(self):
        super().__init__("PosttaxEntries", 
                         ["income INTEGER NOT NULL DEFAULT 0",
                            "new_investment INTEGER NOT NULL DEFAULT 0"])

class AnalysisTable(Database):
    def __init__(self):
        self.name = "AnalysisTable"
        super().__init__(self.name)
        self.make_table()
        print("making analysis table")

    def make_table(self):
        today = date.today().strftime('%Y-%m-%d')

        super().make_table([
            f"date DATE NOT NULL DEFAULT '{today}'",
            "balance INTEGER NOT NULL DEFAULT 0",
            "cashflow INTEGER NOT NULL DEFAULT 0",
            "spending INTEGER NOT NULL DEFAULT 0",
            "notes TEXT DEFAULT ''"
        ])
    
    def wipe_table(self):
        self.delete_table()
        self.make_table()
    
    def recalculate(self, posttax_table):
        # self.wipe_table()
        conn = self.db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get all the entries
        cursor.execute(f"SELECT * FROM {posttax_table.get_table_name()} ORDER BY date")
        entries = cursor.fetchall()
        
        # Calculate the total balance and cash flow based on the entries
        last_balance = 0
        income = 0 # need to get income
        for entry in entries:
            entry_dict = dict(entry)
            date = entry['date']
            income = entry['income']
            balance = sum(value for key, value in entry_dict.items() if key not in ['date', 'income'])
            cashflow = balance - last_balance 
            spending = income - cashflow
            cursor.execute(f"INSERT INTO {self.name} (date, balance, cashflow, spending, notes) VALUES (?, ?, ?, ?, ?)",
                       (date, balance, cashflow, spending, ""))
            last_balance = balance
        res = cursor.execute(f"SELECT * FROM AnalysisTable")
        rows = res.fetchall()
        print("rowsX:", [dict(x) for x in rows])
        conn.commit()
        conn.close()

    def get_all_entries(self):
        conn = self.db_connection()
        cursor = conn.cursor()
        res = cursor.execute(f"SELECT * FROM AnalysisTable")
        rows = res.fetchall()
        conn.close()
        return rows