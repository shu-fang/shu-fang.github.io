from flask import Flask, render_template, request, send_from_directory
import sqlite3
from .db import db_connection, delete_table, make_entries_table, update_account_balance
from datetime import datetime
from flask import jsonify

app = Flask(__name__)

@app.route('/static/css/<path:path>')
def serve_css(path):
    return send_from_directory('static/css', path)

@app.route('/')
def index():
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, balances, tax_status FROM accounts")
    
    accounts_data = cursor.fetchall()
    pretax_balance = sum([int(balance) for _, balance, tax_status in accounts_data if balance.isdigit() and tax_status == 'pre-tax'])
    posttax_balance = sum([int(balance) for _, balance, tax_status in accounts_data if balance.isdigit() and tax_status == 'post-tax'])
    return render_template('index.html', account_balances=accounts_data, pretax_balance=pretax_balance, posttax_balance=posttax_balance)

@app.route('/get_pretax_accounts')
def get_pretax_accounts(tax_status):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM accounts WHERE tax_status = '" + tax_status + "'")
    accounts = cursor.fetchall()
    conn.close()
    return accounts

@app.route('/accounts')
def accounts():
    pretax_accounts = get_pretax_accounts('pre-tax')
    posttax_accounts = get_pretax_accounts('post-tax')
    return render_template('accounts.html', pretax_accounts=pretax_accounts, posttax_accounts = posttax_accounts)

@app.route('/input', methods=['GET','POST'])
def input():
    if request.method == 'POST':
        update_account_balance(request)

    # get all entries 
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM entries')
    entries = cursor.fetchall()
    conn.close()

    # get pretax accounts
    pretax_accounts = get_pretax_accounts("pre-tax")
    posttax_accounts = get_pretax_accounts("post-tax")

    current_date = datetime.today().strftime('%Y-%m-%d')
    return render_template('input.html', current_date=current_date, pretax_accounts=pretax_accounts, posttax_accounts=posttax_accounts, entries=entries, cursor=cursor)

@app.route('/submit', methods=['POST'])
def submit():
    # insert new account into accounts database
    conn = db_connection()
    cursor = conn.cursor()
    new_name = request.form['accountName']
    new_type = "placeholder"
    new_tax_status = request.form['tax_status']
    sql = """INSERT INTO accounts (name, type, tax_status)
                VALUES (?, ?, ?)"""
    cursor = cursor.execute(sql, (new_name, new_type, new_tax_status))
    conn.commit()
    conn.close()

    # insert new account as column into entries database
    conn = db_connection()
    cursor = conn.cursor()
    # Construct a new SQL query to add a new column to the 'entries' table
    sql_query = f"ALTER TABLE entries ADD COLUMN '{new_name}' TEXT DEFAULT '0'"
    # Execute the SQL query and commit the changes to the database
    cursor.execute(sql_query)
    conn.commit()
    conn.close()
    return jsonify({'name': new_name, 'type': new_type, 'tax_status': new_tax_status}), 200

@app.route('/clear', methods=['POST'])
def clear():
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM accounts")
    conn.commit()
    conn.close()

    conn = sqlite3.connect('entries.sqlite')
    cursor = conn.cursor()

    # retrieve the current column names
    delete_table('entries')
    make_entries_table()

    return "Database cleared", 200

@app.route('/data')
def data():
    pretax_accounts = ["\"" + str(account[0]) + "\"" for account in get_pretax_accounts("pre-tax")]
    posttax_accounts = ["\"" + str(account[0]) + "\"" for account in get_pretax_accounts("post-tax")]
    
    conn = db_connection()
    cursor = conn.cursor()
    query = "SELECT date, " + ", ".join(pretax_accounts) + " as pretax_data FROM entries"
    print("query:", query)
    pretax_rows = []
    if pretax_accounts:
        pretax_rows = cursor.execute(query).fetchall()
    query = "SELECT date, " + ", ".join(posttax_accounts) + " as posttax_data FROM entries"
    posttax_rows = []
    if posttax_accounts:
        posttax_rows = cursor.execute(query).fetchall()
    conn.close()
    print("rows:", posttax_rows)
    data = []
    for i in range(len(pretax_rows)):
        pretax_row = pretax_rows[i]
        posttax_row = posttax_rows[i]
        date = pretax_row[0]
        pretaxBalance = sum([int(x) for x in pretax_row[1:]])
        posttaxBalance = sum([int(x) for x in posttax_row[1:]])
        data.append((date,pretaxBalance, posttaxBalance))
    conn.close()
    print("Data:", data)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
