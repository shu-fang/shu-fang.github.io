from flask import Flask, render_template, request, send_from_directory, redirect
import psycopg2
from .db import PretaxEntriesTable, PosttaxEntriesTable, AccountsDatabase, AnalysisTable, addAccount, wipeAllTables, Tables, addNewEntry, deleteAccount
from datetime import datetime
from flask import jsonify

app = Flask(__name__)

@app.route('/static/css/<path:path>')
def serve_css(path):
    return send_from_directory('static/css', path)
print("dropping posttax entries")
post = PretaxEntriesTable()
conn = post.db_connection()
cursor = conn.cursor()

# retrieve the current column names
cursor.execute("DROP TABLE IF EXISTS PosttaxEntries")
conn.commit()
conn.close()
print("DROPPED")
all_tables = {Tables.ACCOUNTS:AccountsDatabase(), 
              Tables.PRETAX_ENTRIES:PretaxEntriesTable(), 
              Tables.POSTTAX_ENTRIES:PosttaxEntriesTable(),
              Tables.ANALYSIS:AnalysisTable()}

@app.route('/')
def index():
    pretax_balance, posttax_balance = all_tables[Tables.ACCOUNTS].get_latest_balances()
    columns = all_tables[Tables.ANALYSIS].get_column_names()
    rows = all_tables[Tables.ANALYSIS].get_all_entries()
    return render_template('index.html', pretax_balance=pretax_balance,
                           posttax_balance=posttax_balance,
                           columns = columns, rows = rows)

@app.route('/accounts')
def accounts():
    return render_template('accounts.html', 
                           pretax_accounts=all_tables[Tables.ACCOUNTS].get_accounts('pre-tax'), 
                           posttax_accounts = all_tables[Tables.ACCOUNTS].get_accounts('post-tax'))

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

# @app.route('/submit', methods = ['POST', 'DELETE'])
# def submit():
#     print("submit triggered", request.form)
#     form_data = request.form
#     if 'addAccountName' in form_data:
#         return add_account(request)
#     elif 'deleteAccountName' in form_data:
#         return delete_account(request)
#     else:
#         return "Invalid form data", 400
    
@app.route('/add_account', methods=['POST', 'GET']) 
def add_account():
    print("add account triggered")
    # adds new account
    addAccount(request, all_tables)
    print("request 1", request.form)
    new_type = "placeholder"
    return jsonify({'name': request.form['addAccountName'], 'type': new_type, 'tax_status': request.form['tax_status']}), 200

@app.route('/delete_account', methods=['DELETE', 'GET'])
def delete_account():
    print("delete account triggered")
    print("request:  :", request.form)
    deleteAccount(request, all_tables)
    new_type = "placeholder"
    return jsonify({'name': request.form['deleteAccountName'], 'type': new_type, 'tax_status': request.form['tax_status']}), 200

@app.route('/clear', methods=['POST'])
def clear():
    wipeAllTables(all_tables)
    return "Database cleared", 200

@app.route('/data')
def data():
    pretax_accounts = ["\"" + str(account[0]) + "\"" for account in all_tables[Tables.ACCOUNTS].get_accounts("pre-tax")]
    posttax_accounts = ["\"" + str(account[0]) + "\"" for account in all_tables[Tables.ACCOUNTS].get_accounts("post-tax")]
    
    conn = all_tables[Tables.ACCOUNTS].db_connection()
    cursor = conn.cursor()
    
    query = "SELECT date, " + ", ".join(pretax_accounts) + " as pretax_data FROM " + all_tables[Tables.PRETAX_ENTRIES].get_table_name()
    pretax_rows = []
    if pretax_accounts:
        cursor.execute(query)
        pretax_rows = cursor.fetchall()
    
    query = "SELECT date, " + ", ".join(posttax_accounts) + " as posttax_data FROM " + all_tables[Tables.POSTTAX_ENTRIES].get_table_name()
    posttax_rows = []
    if posttax_accounts:
        cursor.execute(query)
        posttax_rows = cursor.fetchall()
    conn.close()

    # TODO: pass date, pretax balance, posttax balance to chart --> need to change to separate date values 
    data = []
    for i in range(max(len(pretax_rows), len(posttax_rows))):
        date = datetime.today().strftime("%Y-%m-%d")
        pretaxBalance, posttaxBalance = 0, 0
        if i < len(pretax_rows):
            pretax_row = pretax_rows[i]
            pretaxBalance = sum([int(x) for x in pretax_row[1:]])
        if i < len(posttax_rows):
            posttax_row = posttax_rows[i]
            posttaxBalance = sum([int(x) for x in posttax_row[1:]])
        data.append((date,pretaxBalance, posttaxBalance))
    conn.close()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
