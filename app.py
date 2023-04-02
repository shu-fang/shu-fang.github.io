from flask import Flask, render_template, request, flash, g
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import db
from flask import jsonify
from jinja2 import Environment, FileSystemLoader

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
    return render_template('index.html')

@app.route('/input')
def input():
    return render_template('input.html')

@app.route('/accounts')
def accounts():
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM accounts WHERE tax_status = 'pre-tax'")
    accounts = cursor.fetchall()
    conn.close()
    return render_template('accounts.html', pretax_accounts=accounts)

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
