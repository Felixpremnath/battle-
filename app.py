from flask import Flask, render_template, request, url_for, flash, session, redirect, jsonify
import sqlite3
from flask_session import Session
from datetime import datetime

app = Flask(__name__)

app.secret_key = '1111'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

ADMIN_CREDENTIALS ={
    'Admin': 'admin123',
    'felix' : '123'
}

def get_db_connection():
    conn = sqlite3.connect('database.db')
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS users(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT NOT NULL,
                   mail TEXT NOT NULL,
                   date TEXT NOT NULL)
                   ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template("all.html")

@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/submit', methods=['POST'])
def submit():
    name=request.form['name']
    mail=request.form['mail']
    date_str=request.form['date']

    appointment_date=datetime.strptime(date_str,'%Y-%m-%d')
    current_date=datetime.now()

    if appointment_date < current_date:
        flash("Error: The appointment date cannot be in the past.")
        return redirect(url_for('home'))

    # Insert data into database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, mail, date) VALUES (?, ?, ?)",
                   (name, mail, date_str))
    conn.commit()
    conn.close()

    flash("Successfully submitted!")
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[username] == password:
            session['logged_in'] = True
            session['username'] = username  # Store the username in the session
            flash('Successfully logged in!')
            return redirect(url_for('result'))
        else:
            flash('Invalid credentials, please try again.')
            return redirect(url_for('login'))
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('logged_in',None)
    session.pop('username', None)  # Remove the username from the session
    flash('you have been logged out.')
    return redirect(url_for('login'))

@app.route('/result')
def result():
    if not session.get('logged_in'):
        flash('You need to log in to access this page.')
        return redirect(url_for('login'))
    username = session.get('username')  # Get the username from the session
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    data = cursor.fetchall()
    conn.close()

    return render_template("result.html", username=username, data=data)

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/delete/<int:id>', methods=['DELETE'])
def delete(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)