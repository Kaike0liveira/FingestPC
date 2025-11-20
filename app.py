import os
import sqlite3
from datetime import datetime, date
from io import BytesIO

from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import pandas as pd
from sklearn.linear_model import LinearRegression
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.environ.get('SECRET_KEY') or 'dev_secret_change_me'


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        email TEXT,
        role TEXT,
        photo TEXT
    )
    ''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL,
        category TEXT,
        date TEXT,
        user_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS settings (
        user_id INTEGER PRIMARY KEY,
        monthly_limit REAL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')
    conn.commit()
    conn.close()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def current_user():
    if 'user_id' in session:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
        user = cur.fetchone()
        conn.close()
        return user
    return None


def predict_next_month(user_id):
    conn = get_db()
    df = pd.read_sql_query('SELECT amount, date FROM expenses WHERE user_id = ?', conn, params=(user_id,))
    conn.close()
    if df.empty:
        return 0.0, {}

    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M')
    monthly = df.groupby('month')['amount'].sum().reset_index()
    monthly['month_idx'] = range(len(monthly))

    if len(monthly) < 2:
        next_pred = float(monthly['amount'].iloc[-1])
    else:
        X = monthly[['month_idx']].values
        y = monthly['amount'].values
        model = LinearRegression()
        model.fit(X, y)
        next_pred = float(model.predict([[len(monthly)]])[0])

    # média por categoria
    conn = get_db()
    cat_df = pd.read_sql_query('SELECT category, amount FROM expenses WHERE user_id = ?', conn, params=(user_id,))
    conn.close()
    if cat_df.empty:
        cat_avg = {}
    else:
        cat_avg = cat_df.groupby('category')['amount'].mean().round(2).to_dict()

    return round(float(next_pred), 2), cat_avg


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form.get('email')

        conn = get_db()
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) as c FROM users')
        count = cur.fetchone()['c']
        role = 'admin' if count == 0 else 'user'

        hashed = generate_password_hash(password)
        try:
            cur.execute('INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)',
                        (username, hashed, email, role))
            conn.commit()
            user_id = cur.lastrowid
            # default settings
            cur.execute('INSERT OR IGNORE INTO settings (user_id, monthly_limit) VALUES (?, ?)', (user_id, 0.0))
            conn.commit()
            conn.close()
            flash('Registrado com sucesso. Faça login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()
            flash('Nome de usuário já existe.', 'danger')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cur.fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash('Bem-vindo, {}'.format(user['username']), 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciais inválidas.', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Você saiu.', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    user = current_user()
    if not user:
        return redirect(url_for('login'))

    conn = get_db()
    df = pd.read_sql_query('SELECT amount, category, date FROM expenses WHERE user_id = ?', conn, params=(user['id'],))
    cur = conn.cursor()
    cur.execute('SELECT monthly_limit FROM settings WHERE user_id = ?', (user['id'],))
    s = cur.fetchone()
    limit = s['monthly_limit'] if s else 0.0
    conn.close()

    chart_labels = []
    chart_values = []

    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.to_period('M')
        monthly = df.groupby('month')['amount'].sum().reset_index()
        chart_labels = monthly['month'].astype(str).tolist()
        chart_values = monthly['amount'].round(2).tolist()

    prediction, cat_avg = predict_next_month(user['id'])

    return render_template('dashboard.html', user=user, labels=chart_labels, values=chart_values, prediction=prediction, category_avg=cat_avg, limit=limit)


@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    user = current_user()
    if not user:
        return redirect(url_for('login'))
    if request.method == 'POST':
        amount = float(request.form['amount'])
        category = request.form['category']
        date_str = request.form.get('date') or date.today().isoformat()
        conn = get_db()
        cur = conn.cursor()
        cur.execute('INSERT INTO expenses (amount, category, date, user_id) VALUES (?, ?, ?, ?)',
                    (amount, category, date_str, user['id']))
        conn.commit()
        conn.close()
        flash('Gasto adicionado.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_expense.html')


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    user = current_user()
    if not user:
        return redirect(url_for('login'))
    conn = get_db()
    cur = conn.cursor()
    if request.method == 'POST':
        limit = float(request.form.get('monthly_limit') or 0.0)
        cur.execute('INSERT OR REPLACE INTO settings (user_id, monthly_limit) VALUES (?, ?)', (user['id'], limit))
        conn.commit()
        flash('Configurações salvas.', 'success')

    cur.execute('SELECT monthly_limit FROM settings WHERE user_id = ?', (user['id'],))
    s = cur.fetchone()
    limit = s['monthly_limit'] if s else 0.0
    conn.close()
    return render_template('settings.html', limit=limit)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user = current_user()
    if not user:
        return redirect(url_for('login'))
    conn = get_db()
    cur = conn.cursor()
    if request.method == 'POST':
        if 'email' in request.form:
            email = request.form.get('email')
            cur.execute('UPDATE users SET email = ? WHERE id = ?', (email, user['id']))
            conn.commit()
            flash('Email atualizado.', 'success')

        if 'password' in request.form and request.form.get('password'):
            newpw = generate_password_hash(request.form.get('password'))
            cur.execute('UPDATE users SET password = ? WHERE id = ?', (newpw, user['id']))
            conn.commit()
            flash('Senha alterada.', 'success')

        if 'photo' in request.files:
            file = request.files['photo']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                ext = filename.rsplit('.', 1)[1].lower()
                saved_name = f'user_{user["id"]}.{ext}'
                path = os.path.join(app.config['UPLOAD_FOLDER'], saved_name)
                file.save(path)
                cur.execute('UPDATE users SET photo = ? WHERE id = ?', (saved_name, user['id']))
                conn.commit()
                flash('Foto atualizada.', 'success')

    cur.execute('SELECT * FROM users WHERE id = ?', (user['id'],))
    refreshed = cur.fetchone()
    conn.close()
    return render_template('profile.html', user=refreshed)


@app.route('/admin', methods=['GET'])
def admin():
    user = current_user()
    if not user or user['role'] != 'admin':
        flash('Acesso negado.', 'danger')
        return redirect(url_for('dashboard'))

    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT id, username, email, role, photo FROM users')
    users = cur.fetchall()

    # estatísticas básicas
    cur.execute('SELECT COUNT(*) as total_users FROM users')
    total_users = cur.fetchone()['total_users']
    cur.execute('SELECT SUM(amount) as total_spent FROM expenses')
    total_spent = cur.fetchone()['total_spent'] or 0.0
    conn.close()

    return render_template('admin_dashboard.html', users=users, total_users=total_users, total_spent=round(total_spent, 2))


@app.route('/admin/set_role', methods=['POST'])
def set_role():
    user = current_user()
    if not user or user['role'] != 'admin':
        return jsonify({'error': 'Acesso negado.'}), 403
    target_id = int(request.form['user_id'])
    new_role = request.form['role']

    if target_id == user['id'] and new_role != 'admin':
        flash('Você não pode rebaixar seu próprio papel.', 'warning')
        return redirect(url_for('admin'))

    conn = get_db()
    cur = conn.cursor()
    cur.execute('UPDATE users SET role = ? WHERE id = ?', (new_role, target_id))
    conn.commit()
    conn.close()
    flash('Papel atualizado.', 'success')
    return redirect(url_for('admin'))


@app.route('/export')
def export_excel():
    user = current_user()
    if not user:
        return redirect(url_for('login'))
    conn = get_db()
    df = pd.read_sql_query('SELECT amount, category, date FROM expenses WHERE user_id = ?', conn, params=(user['id'],))
    conn.close()
    if df.empty:
        flash('Sem dados para exportar.', 'info')
        return redirect(url_for('dashboard'))

    output = BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)
    filename = f'expenses_user_{user["id"]}.xlsx'
    return send_file(output, as_attachment=True, download_name=filename, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@app.route('/api/summary')
def api_summary():
    user = current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT SUM(amount) as total FROM expenses WHERE user_id = ?', (user['id'],))
    total = cur.fetchone()['total'] or 0.0
    cur.execute('SELECT monthly_limit FROM settings WHERE user_id = ?', (user['id'],))
    s = cur.fetchone()
    limit = s['monthly_limit'] if s else 0.0
    conn.close()
    return jsonify({'total': round(float(total), 2), 'limit': round(float(limit), 2)})


if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    init_db()
    app.run(debug=True)
