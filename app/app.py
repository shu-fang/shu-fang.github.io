from flask import Flask, render_template, request, send_from_directory, redirect
import psycopg2
from .db import PretaxEntriesTable, PosttaxEntriesTable, AccountsDatabase, AnalysisTable, addAccount, wipeAllTables, Tables, addNewEntry, deleteAccount
from datetime import datetime
from flask import jsonify

app = Flask(__name__)

@app.route('/static/css/<path:path>')
def serve_css(path):
    return send_from_directory('static/css', path)

all_tables = {Tables.ACCOUNTS:AccountsDatabase(), 
              Tables.PRETAX_ENTRIES:PretaxEntriesTable(), 
              Tables.POSTTAX_ENTRIES:PosttaxEntriesTable(),
              Tables.ANALYSIS:AnalysisTable()}

@app.route('/')
def index():
    pretax_balance, posttax_balance = all_tables[Tables.ACCOUNTS].get_latest_balance()
    columns = all_tables[Tables.ANALYSIS].get_column_names()
    rows = all_tables[Tables.ANALYSIS].get_all_entries()
    return render_template('index.html', pretax_balance=pretax_balance,
                           posttax_balance=posttax_balance,
                           columns = columns, rows = rows)

@app.route('/accounts')
def accounts():
    return render_template('accounts.html', 
                           pretax_accounts=all_tables[Tables.ACCOUNTS].get_accounts('pre-tax'), 
                           posttax_accounts=all_tables[Tables.ACCOUNTS].get_accounts('post-tax'))

@app.route('/input', methods=['GET','POST'])
def input():
    if request.method == 'POST':
        addNewEntry(request, all_tables)
        
    return render_template('input.html', 
                           current_date=datetime.today().strftime('%Y-%m-%d'), 
                           pretax_accounts=all_tables[Tables.ACCOUNTS].get_accounts("pre-tax"), 
                           posttax_accounts=all_tables[Tables.ACCOUNTS].get_accounts("post-tax"), 
                           posttax_entries=all_tables[Tables.POSTTAX_ENTRIES].get_all_entries(),
                           pretax_entries=all_tables[Tables.PRETAX_ENTRIES].get_all_entries(),
                           pretax_columns = all_tables[Tables.PRETAX_ENTRIES].get_column_names(),
                           posttax_columns = all_tables[Tables.POSTTAX_ENTRIES].get_column_names())

@app.route('/add_account', methods=['POST', 'GET']) 
def add_account():
    # adds new account
    status = addAccount(request, all_tables)
    if not status:
        return jsonify({'error':"Error adding account"}), 400
    return jsonify({'name': request.form['addAccountName'], 'type': request.form['type'],
                    'tax_status': request.form['tax_status']}), 200

@app.route('/delete_account', methods=['DELETE', 'GET'])
def delete_account():
    deleteAccount(request, all_tables)
    new_type = "placeholder"
    return jsonify({'name': request.form['deleteAccountName'], 'type': new_type, 'tax_status': request.form['tax_status']}), 200

@app.route('/clear', methods=['POST'])
def clear():
    wipeAllTables(all_tables)
    return "Database cleared", 200

@app.route('/data')
def data():
    posttax_data = sorted(all_tables[Tables.ANALYSIS].get_date_balance())
    data = []
    for date, balance in posttax_data:
        data.append((date.strftime('%Y-%m-%d'), balance))
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
