from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import MySQLdb.cursors
import requests

app = Flask(__name__)
app.secret_key = 'crypto_secret_key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Vaibhavi@123'
app.config['MYSQL_DB'] = 'crypto_tracker'

mysql = MySQL(app)
bcrypt = Bcrypt(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        cursor = mysql.connection.cursor()
        try:
            cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                         (username, email, hashed_pw))
            mysql.connection.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except:
            flash('Username or email already exists!', 'danger')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if user and bcrypt.check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password!', 'danger')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'])

@app.route('/add_coin', methods=['POST'])
def add_coin():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    coin_name = request.form['coin_name']
    coin_id = request.form['coin_id']
    quantity = float(request.form['quantity'])
    buy_price = float(request.form['buy_price'])
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO portfolio (user_id, coin_id, coin_name, quantity, buy_price) VALUES (%s, %s, %s, %s, %s)",
                   (session['user_id'], coin_id, coin_name, quantity, buy_price))
    mysql.connection.commit()
    flash('Coin added to portfolio!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/get_portfolio')
def get_portfolio():
    if 'user_id' not in session:
        return jsonify([])
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM portfolio WHERE user_id = %s", (session['user_id'],))
    coins = cursor.fetchall()
    if not coins:
        return jsonify([])
    ids = ','.join([c['coin_id'] for c in coins])
    url = f'https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd'
    prices = requests.get(url).json()
    result = []
    for coin in coins:
        current = prices.get(coin['coin_id'], {}).get('usd', 0)
        result.append({
            'id': coin['id'],
            'coin_name': coin['coin_name'],
            'quantity': coin['quantity'],
            'buy_price': coin['buy_price'],
            'current_price': current
        })
    return jsonify(result)

@app.route('/delete_coin/<int:coin_id>')
def delete_coin(coin_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM portfolio WHERE id = %s AND user_id = %s",
                   (coin_id, session['user_id']))
    mysql.connection.commit()
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)