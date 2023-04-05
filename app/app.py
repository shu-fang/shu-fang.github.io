from flask import Flask, render_template, request, send_from_directory
import psycopg2
from .db import PretaxEntriesTable, PosttaxEntriesTable, AccountsDatabase, AnalysisTable
from datetime import datetime
from flask import jsonify

app = Flask(__name__)

@app.route('/static/css/<path:path>')
def serve_css(path):
    return send_from_directory('static/css', path)

accounts_db = AccountsDatabase()
pretax_entries_table = PretaxEntriesTable()
posttax_entries_table = PosttaxEntriesTable()
analysis_table = AnalysisTable()

@app.route('/')
def index():
    pretax_balance, posttax_balance = accounts_db.get_latest_balances()
    columns = analysis_table.get_column_names()
    rows = analysis_table.get_all_entries()
    return render_template('index.html', pretax_balance=pretax_balance,
                           posttax_balance=posttax_balance,
                           columns = columns, rows = rows)

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
            analysis_table.recalculate(posttax_entries_table)
        elif 'pretax_submit' in request.form:
            pretax_entries_table.add_entry(request)
        else:
            print("WARNING: request from input page not recognized")

    return render_template('input.html', 
                           current_date=datetime.today().strftime('%Y-%m-%d'), 
                           pretax_accounts=accounts_db.get_accounts("pre-tax"), 
                           posttax_accounts=accounts_db.get_accounts("post-tax"), 
                           posttax_entries=posttax_entries_table.get_all_entries(),
                           pretax_entries=pretax_entries_table.get_all_entries(),
                           pretax_columns = pretax_entries_table.get_column_names(),
                           posttax_columns = posttax_entries_table.get_column_names())

@app.route('/submit', methods=['POST']) # adds new account
def submit():
    # insert new account into accounts database
    accounts_db.add_account(request)
    tax_status = request.form['tax_status']
    if tax_status == 'pre-tax':
        pretax_entries_table.add_column(request)
    else:
        posttax_entries_table.add_column(request)
        analysis_table.recalculate(posttax_entries_table)
    new_type = "placeholder"
    return jsonify({'name': request.form['accountName'], 'type': new_type, 'tax_status': tax_status}), 200

@app.route('/clear', methods=['POST'])
def clear():
    accounts_db.wipe_table()
    pretax_entries_table.wipe_table()
    posttax_entries_table.wipe_table()
    analysis_table.wipe_table()
    return "Database cleared", 200

@app.route('/data')
def data():
    pretax_accounts = ["\"" + str(account[0]) + "\"" for account in accounts_db.get_accounts("pre-tax")]
    posttax_accounts = ["\"" + str(account[0]) + "\"" for account in accounts_db.get_accounts("post-tax")]
    
    conn = accounts_db.db_connection()
    cursor = conn.cursor()
    
    query = "SELECT date, " + ", ".join(pretax_accounts) + " as pretax_data FROM " + pretax_entries_table.get_table_name()
    pretax_rows = []
    if pretax_accounts:
        cursor.execute(query)
        pretax_rows = cursor.fetchall()
    
    query = "SELECT date, " + ", ".join(posttax_accounts) + " as posttax_data FROM " + posttax_entries_table.get_table_name()
    posttax_rows = []
    if posttax_accounts:
        cursor.execute(query)
        posttax_rows = cursor.fetchall()
    conn.close()

    # TODO: pass date, pretax balance, posttax balance to chart --> need to change to separate date values 
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
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
