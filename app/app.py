from flask import Flask, render_template, request, send_from_directory
import sqlite3
from .db import db_connection, delete_table, make_entries_table, update_account_balance

from flask import jsonify

app = Flask(__name__)

@app.route('/static/css/<path:path>')
def serve_css(path):
    return send_from_directory('static/css', path)

@app.route('/')
def index():
    conn = db_connection('accounts')
    cursor = conn.cursor()
    cursor.execute("SELECT name, balances FROM accounts")
    accounts_data = cursor.fetchall()

    total_balance = sum([int(balance) for _, balance in accounts_data if balance.isdigit()])
    return render_template('index.html', account_balances=accounts_data, total_balance=total_balance)

@app.route('/get_pretax_accounts')
def get_pretax_accounts(tax_status):
    conn = db_connection('accounts')
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
    conn = sqlite3.connect('entries.sqlite')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM entries')
    entries = cursor.fetchall()
    conn.close()

    # get pretax accounts
    pretax_accounts = get_pretax_accounts("pre-tax")
    print("pretax:", pretax_accounts)
    print("enm:", entries)
    posttax_accounts = get_pretax_accounts("post-tax")
    return render_template('input.html', pretax_accounts=pretax_accounts, posttax_accounts=posttax_accounts, entries=entries, cursor=cursor)

@app.route('/submit', methods=['POST'])
def submit():
    # insert new account into accounts database
    conn = db_connection('accounts')
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
    conn = sqlite3.connect('entries.sqlite')
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
    conn = db_connection('accounts')
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
    conn = db_connection('entries')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM entries")
    rows = cursor.fetchall()
    conn.close()

    columns = [desc[0] for desc in cursor.description]
    data = []
    for row in rows:
        data.append(dict(zip(columns, row)))
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
