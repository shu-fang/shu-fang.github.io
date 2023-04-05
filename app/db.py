import sqlite3
import psycopg2, os
from psycopg2 import extras
from datetime import date, datetime
from enum import Enum


class Tables(Enum):
    ACCOUNTS = "accounts"
    POSTTAX_ENTRIES = "PosttaxEntries"
    PRETAX_ENTRIES = "PretaxEntries"
    ANALYSIS = "AnalysisTable"
    
class Database:
    def __init__(self, name): 
       self.name = name
       return
    
    def make_table(self, fields):
        print("making table ", self.name)
        try:
            conn = self.db_connection()
            cursor = conn.cursor()

            sql_query = f"""CREATE TABLE IF NOT EXISTS {self.name} (
                id SERIAL PRIMARY KEY,
                {', '.join(fields)}
            )"""
            print("query for", self.name, " : ", sql_query)
            cursor.execute(sql_query)
            conn.commit()
            conn.close()

        except sqlite3.Error as e:
            print(f"Error creating {self.name} table: {e}")

    def db_connection(self):
        conn = None
        if 'USERNAME' in os.environ and os.environ['USERNAME'] == 'lfang':
            try:
                conn = psycopg2.connect(
                    host="localhost",
                    database="mydb",
                    user="postgres",
                    password="1011"
                )
            except psycopg2.Error as e:
                print(e)
            return conn

        try:
            DATABASE_URL = os.environ['DATABASE_URL']
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            return conn
        except psycopg2.Error as e:
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
        cursor.execute(f"SELECT * FROM {self.name} LIMIT 0")
        columns = [column[0] for column in cursor.description if column[0] != 'id']        
        conn.close()
        return columns
    
    def get_all_entries(self):
        conn = self.db_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {self.name}")
        rows = [row[1:] for row in cursor.fetchall()]
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
            "balances text NOT NULL DEFAULT '0'",
        ])
    
    def add_account(self, request):
        conn = self.db_connection()
        cursor = conn.cursor()
        print("add request:", request.form)
        new_name = request.form['addAccountName']
        new_type = "placeholder"
        new_tax_status = request.form['tax_status']
        sql = """INSERT INTO accounts (name, type, tax_status)
                    VALUES (%s, %s, %s)"""
        cursor = cursor.execute(sql, (new_name, new_type, new_tax_status))
        conn.commit()
        conn.close()
    
    def delete_account(self, request):
        conn = self.db_connection()
        cursor = conn.cursor()
        
        name = request.form['deleteAccountName']
        tax_status = request.form['tax_status']
        print("delete request:", request.form, type(name))
        sql = f"""DELETE FROM accounts WHERE name = %s and tax_status = %s"""
        cursor = cursor.execute(sql, (name, tax_status))
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
        cursor.execute(f"SELECT MAX(date) FROM {table}")
        latest_date = cursor.fetchone()[0]
        
        entry_date = datetime.strptime(request.form['entry_date'], '%Y-%m-%d').date()
        if request.method == 'POST' and (not latest_date or entry_date >= latest_date):
            for account in request.form:
                name = account
                balance = self.format_balance(request.form[account])
                
                cursor.execute("UPDATE accounts SET balances=%s WHERE name=%s", (balance, name))
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
            "date DATE NOT NULL DEFAULT CURRENT_DATE",
            *self.columns + [f"CONSTRAINT unique_date_{self.name} UNIQUE (date)"]
        ])
    
    def add_column(self, request):
        conn = self.db_connection()
        cursor = conn.cursor()
        sql_query = f'ALTER TABLE {self.name} ADD COLUMN "{request.form["addAccountName"]}" INTEGER DEFAULT 0'
        cursor.execute(sql_query)
        conn.commit()
        conn.close()

    def delete_column(self, request):
        column = request.form["deleteAccountName"]
        print("deleting ", column, " from ", self.name)
        if column not in self.get_column_names():
            print("WARNING: account ", column, " does not exist")
            return 
        conn = self.db_connection()
        cursor = conn.cursor()
        sql_query = f"""DELETE FROM accounts WHERE name = %s"""
        cursor.execute(sql_query, (column,))
        conn.commit()
        conn.close()

    def add_entry(self, request):
        conn = self.db_connection()
        cursor = conn.cursor()
        accounts = {key: value for key, value in request.form.items() if key not in ['entry_date', 'posttax_submit', 
                                                                                     'pretax_submit']}
        entry_date = request.form['entry_date']
        # Construct the SQL query to insert a new row into the 'entries' table
        columns = [f'"{col}"' for col in accounts.keys()]
        
        values = ', '.join(['%s'] * len(accounts))
        print("Adding entry to ", self.name)
        sql_query = f"INSERT INTO {self.name} ({', '.join(columns)}, date) VALUES ({values}, DATE %s) "\
            f"ON CONFLICT (date) DO UPDATE SET "\
            f"{', '.join([f'{col} = EXCLUDED.{col}' for col in columns if col != 'date'])};"
        print("adding entry with query:", sql_query)
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
        self.name = str(Tables.PRETAX_ENTRIES.value)
        print("xx:", Tables.PRETAX_ENTRIES.value)
        super().__init__(self.name)

class PosttaxEntriesTable(EntriesDatabase):
    def __init__(self):
        self.name = str(Tables.POSTTAX_ENTRIES.value)
        super().__init__(self.name, 
                         ["income INTEGER NOT NULL DEFAULT 0",
                            "new_investment INTEGER NOT NULL DEFAULT 0"])

class AnalysisTable(Database):
    def __init__(self):
        self.name = "AnalysisTable"
        super().__init__(self.name)
        self.make_table()

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
        self.wipe_table()
        conn = self.db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

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
            cursor.execute(f"INSERT INTO {self.name} (date, balance, cashflow, spending, notes) VALUES (DATE %s, %s,%s, %s, %s)",
                       (date, balance, cashflow, spending, ""))
            last_balance = balance
        conn.commit()
        conn.close()

def addAccount(request, all_tables):
    # add account to account table, as column to entries table
    all_tables[Tables.ACCOUNTS].add_account(request)
    tax_status = request.form['tax_status']
    if tax_status == 'pre-tax':
        all_tables[Tables.PRETAX_ENTRIES].add_column(request)
    else:
        all_tables[Tables.POSTTAX_ENTRIES].add_column(request)

def deleteAccount(request, all_tables):
    print("form:", request.form)
    tax_status = request.form['tax_status']
    all_tables[Tables.ACCOUNTS].delete_account(request)
    if tax_status == 'pre-tax':
        all_tables[Tables.PRETAX_ENTRIES].delete_column(request)
    elif tax_status == 'post-tax':
        all_tables[Tables.POSTTAX_ENTRIES].delete_column(request)

    all_tables[Tables.ANALYSIS].recalculate(all_tables[Tables.POSTTAX_ENTRIES])
    
def wipeAllTables(tables):
    for table in tables.values():
        table.wipe_table()

def addNewEntry(request, all_tables):
    if request.method != 'POST':
        print("WARNING: failed to add new entry, request method is not POST")
        return 
    
    all_tables[Tables.ACCOUNTS].update_account_balance(request)
    if 'posttax_submit' in request.form:
        all_tables[Tables.POSTTAX_ENTRIES].add_entry(request)
        all_tables[Tables.ANALYSIS].recalculate(all_tables[Tables.POSTTAX_ENTRIES])
    elif 'pretax_submit' in request.form:
        all_tables[Tables.PRETAX_ENTRIES].add_entry(request)
    else:
        print("WARNING: request from input page not recognized")