from flask import Flask, render_template, request, send_from_directory
import sqlite3
from .db import PretaxEntriesTable, PosttaxEntriesTable, AccountsDatabase
from datetime import datetime
from flask import jsonify

app = Flask(__name__)

@app.route('/static/css/<path:path>')
def serve_css(path):
    return send_from_directory('static/css', path)

accounts_db = AccountsDatabase()
pretax_entries_table = PretaxEntriesTable()
posttax_entries_table = PosttaxEntriesTable()

@app.route('/')
def index():
    pretax_balance, posttax_balance = accounts_db.get_latest_balances()
    return render_template('index.html', pretax_balance=pretax_balance, posttax_balance=posttax_balance)

@app.route('/accounts')
def accounts():
    return render_template('accounts.html', 
                           pretax_accounts=accounts_db.get_accounts('pre-tax'), 
                           posttax_accounts = accounts_db.get_accounts('post-tax'))

@app.route('/input', methods=['GET','POST'])
def input():
    if request.method == 'POST':
        accounts_db.update_account_balance(request)
        if 'posttax_submit' in request.form:
            posttax_entries_table.add_entry(request)
        elif 'pretax_submit' in request.form:
            pretax_entries_table.add_entry(request)
        else:
            print("WARNING: request from input page not recognized")

    # get all entries 
    conn = posttax_entries_table.db_connection()
    post_cursor = conn.cursor()
    post_cursor.execute(f'SELECT * FROM {posttax_entries_table.get_table_name()}')
    
    posttax_entries = post_cursor.fetchall()
    conn.close()

    conn = pretax_entries_table.db_connection()
    pre_cursor = conn.cursor()
    pre_cursor.execute(f'SELECT * FROM {pretax_entries_table.get_table_name()}')
    pretax_entries = pre_cursor.fetchall()
    conn.close()
    return render_template('input.html', 
                           current_date=datetime.today().strftime('%Y-%m-%d'), 
                           pretax_accounts=accounts_db.get_accounts("pre-tax"), 
                           posttax_accounts=accounts_db.get_accounts("post-tax"), 
                           posttax_entries=posttax_entries,
                           pretax_entries=pretax_entries,
                           pre_cursor=pre_cursor,
                           post_cursor=post_cursor)

@app.route('/submit', methods=['POST'])
def submit():
    # insert new account into accounts database
    accounts_db.add_account(request)
    tax_status = request.form['tax_status']
    if tax_status == 'pre-tax':
        pretax_entries_table.add_column(request)
    else:
        posttax_entries_table.add_column(request)
    new_type = "placeholder"
    return jsonify({'name': request.form['accountName'], 'type': new_type, 'tax_status': tax_status}), 200

@app.route('/clear', methods=['POST'])
def clear():
    accounts_db.wipe_table()
    pretax_entries_table.wipe_table()
    posttax_entries_table.wipe_table()
    return "Database cleared", 200

@app.route('/data')
def data():
    pretax_accounts = ["\"" + str(account[0]) + "\"" for account in accounts_db.get_accounts("pre-tax")]
    posttax_accounts = ["\"" + str(account[0]) + "\"" for account in accounts_db.get_accounts("post-tax")]
    
    conn = accounts_db.db_connection()
    cursor = conn.cursor()
    
    query = "SELECT date, " + ", ".join(pretax_accounts) + " as pretax_data FROM PretaxEntries"
    print("query:", query)
    pretax_rows = []
    if pretax_accounts:
        pretax_rows = cursor.execute(query).fetchall()
    
    query = "SELECT date, " + ", ".join(posttax_accounts) + " as posttax_data FROM PosttaxEntries"
    posttax_rows = []
    if posttax_accounts:
        posttax_rows = cursor.execute(query).fetchall()
    conn.close()

    # TODO: pass date, pretax balance, posttax balance to chart --> need to change to separate date values 
    print("rows:", posttax_rows)
    data = []
    for i in range(max(len(pretax_rows), len(posttax_rows))):
        date = datetime.today()
        pretaxBalance, posttaxBalance = 0, 0
        if i < len(pretax_rows):
            pretax_row = pretax_rows[i]
            pretaxBalance = sum([int(x) for x in pretax_row[1:]])
            date = pretax_row[0]
        if i < len(posttax_rows):
            posttax_row = posttax_rows[i]
            posttaxBalance = sum([int(x) for x in posttax_row[1:]])
            date = posttax_row[0]
        
        data.append((date,pretaxBalance, posttaxBalance))
    conn.close()
    print("Data:", data)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
