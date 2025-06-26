from flask import Flask, render_template, redirect, url_for, request, session, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import io
import csv
import plotly.graph_objs as go
import plotly
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-fallback-secret')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

def current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

from functools import wraps
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user():
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        hashed = generate_password_hash(password)
        user = User(username=username, password=hashed)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    user = current_user()
    transactions = Transaction.query.filter_by(user_id=user.id).all()
    if not transactions:
        flash('No transactions yet. Add some to see graphs.')
        return redirect(url_for('transactions'))
    dates = [t.date.strftime('%Y-%m-%d') for t in transactions]
    amounts = [t.amount for t in transactions]

    line = go.Scatter(x=dates, y=amounts, mode='lines+markers', name='Expenses')

    categories = [t.category_id for t in transactions]
    cat_names = [Category.query.get(cid).name if Category.query.get(cid) else 'Unknown' for cid in categories]
    pie = go.Pie(labels=cat_names, values=amounts, hole=0.3)

    fig = go.Figure([line])
    fig_pie = go.Figure([pie])

    plot_div = plotly.io.to_html(fig, full_html=False)
    pie_div = plotly.io.to_html(fig_pie, full_html=False)

    return render_template('dashboard.html', user=user, plot_div=plot_div, pie_div=pie_div)

@app.route('/categories', methods=['GET', 'POST'])
@login_required
def categories():
    user = current_user()
    if request.method == 'POST':
        name = request.form['name']
        if name:
            c = Category(name=name, user_id=user.id)
            db.session.add(c)
            db.session.commit()
            flash('Category added')
    cats = Category.query.filter_by(user_id=user.id).all()
    return render_template('categories.html', categories=cats)

@app.route('/transactions', methods=['GET', 'POST'])
@login_required
def transactions():
    user = current_user()
    categories = Category.query.filter_by(user_id=user.id).all()
    if request.method == 'POST':
        title = request.form['title']
        amount = float(request.form['amount'])
        date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        category_id = int(request.form['category_id'])
        t = Transaction(title=title, amount=amount, date=date, category_id=category_id, user_id=user.id)
        db.session.add(t)
        db.session.commit()
        flash('Transaction added')
    txs = Transaction.query.filter_by(user_id=user.id).order_by(Transaction.date.desc()).all()
    return render_template('transactions.html', transactions=txs, categories=categories)

@app.route('/profile')
@login_required
def profile():
    user = current_user()
    return render_template('profile.html', user=user)

@app.route('/set_budget', methods=['GET', 'POST'])
@login_required
def set_budget():
    user = current_user()
    budget = Budget.query.filter_by(user_id=user.id).first()
    if request.method == 'POST':
        amount = float(request.form['amount'])
        if budget:
            budget.amount = amount
        else:
            budget = Budget(amount=amount, user_id=user.id)
            db.session.add(budget)
        db.session.commit()
        flash('Budget updated')
        return redirect(url_for('dashboard'))
    return render_template('set_budget.html', budget=budget)

@app.route('/export')
@login_required
def export():
    user = current_user()
    transactions = Transaction.query.filter_by(user_id=user.id).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Title', 'Amount', 'Date', 'Category'])
    for t in transactions:
        cat = Category.query.get(t.category_id)
        writer.writerow([t.title, t.amount, t.date, cat.name if cat else 'Unknown'])
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name='transactions.csv')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
