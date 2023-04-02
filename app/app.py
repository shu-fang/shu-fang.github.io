from flask import Flask, render_template, request, flash, g
import sqlite3
import db as db
from flask import jsonify
# from jinja2 import Environment, FileSystemLoader

app = Flask(__name__)

def db_connection():
    conn = None
    try:
        conn = sqlite3.connect("accounts.sqlite")
    except sqlite3.error as e:
        print(e)
    return conn

@app.route('/')
def index():
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, balances FROM accounts")
    accounts_data = cursor.fetchall()

    total_balance = sum([balance for _, balance in accounts_data])
    return render_template('index.html', account_balances=accounts_data, total_balance=total_balance)

@app.route('/get_pretax_accounts')
def get_pretax_accounts():
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM accounts WHERE tax_status = 'pre-tax'")
    accounts = cursor.fetchall()
    conn.close()
    return accounts

@app.route('/accounts')
def accounts():
    pretax_accounts = get_pretax_accounts()
    return render_template('accounts.html', pretax_accounts=pretax_accounts)

@app.route('/input', methods=['GET','POST'])
def input():
    conn = db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        for account in request.form:
            if account.startswith('balance--'):
                name = account[9:]
                balance = request.form[account]
                cursor.execute("UPDATE accounts SET balances=? WHERE name=?", (balance, name))
                conn.commit()

    cursor.execute("SELECT name, balances FROM accounts")
    pretax_accounts = get_pretax_accounts()
    return render_template('input.html', pretax_accounts=pretax_accounts)

@app.route('/submit', methods=['POST'])
def submit():
    conn = db_connection()
    cursor = conn.cursor()
    new_name = request.form['accountName']
    new_type = "placeholder"
    new_tax_status = "pre-tax"
    sql = """INSERT INTO accounts (name, type, tax_status)
                VALUES (?, ?, ?)"""
    cursor = cursor.execute(sql, (new_name, new_type, new_tax_status))
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
    return "Database cleared", 200

if __name__ == '__main__':
    app.run(debug=True)
