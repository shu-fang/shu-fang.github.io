from flask import Flask, render_template, request, flash

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/input')
def input():
    return render_template('input.html')

@app.route('/accounts')
def accounts():
    return render_template('accounts.html')

if __name__ == '__main__':
    app.run(debug=True)