from flask import Flask, render_template, redirect, url_for, request, session, flash, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import io
import csv
import plotly.graph_objs as go
import plotly
import plotly.express as px
import pandas as pd
import os
from collections import defaultdict

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'budget-buddy-secret-key-2024')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///budget_buddy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(7), default='#3498db')  # Hex color code
    icon = db.Column(db.String(50), default='💰')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(10), default='expense')  # 'income' or 'expense'
    date = db.Column(db.Date, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    notes = db.Column(db.Text)

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    amount = db.Column(db.Float, nullable=False)
    month = db.Column(db.Integer, nullable=False)  # 1-12
    year = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    target_date = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
    if current_user():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return redirect(url_for('register'))
        
        hashed = generate_password_hash(password)
        user = User(username=username, email=email, password=hashed)
        db.session.add(user)
        db.session.commit()
        
        # Create default categories
        default_categories = [
            ('Food & Dining', '#e74c3c', '🍽️'),
            ('Transportation', '#3498db', '🚗'),
            ('Shopping', '#9b59b6', '🛍️'),
            ('Entertainment', '#f39c12', '🎬'),
            ('Bills & Utilities', '#34495e', '💡'),
            ('Healthcare', '#1abc9c', '🏥'),
            ('Income', '#27ae60', '💰'),
            ('Savings', '#2ecc71', '💎')
        ]
        
        for name, color, icon in default_categories:
            category = Category(name=name, color=color, icon=icon, user_id=user.id)
            db.session.add(category)
        
        db.session.commit()
        flash('Registration successful! Welcome to Budget Buddy!', 'success')
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
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('dashboard'))
        
        flash('Invalid credentials', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    user = current_user()
    
    # Get current month's data
    current_date = datetime.now()
    start_of_month = current_date.replace(day=1)
    
    # Get transactions for current month
    transactions = Transaction.query.filter(
        Transaction.user_id == user.id,
        Transaction.date >= start_of_month.date()
    ).all()
    
    # Calculate totals
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
    total_expenses = sum(t.amount for t in transactions if t.transaction_type == 'expense')
    balance = total_income - total_expenses
    
    # Get recent transactions
    recent_transactions = Transaction.query.filter_by(user_id=user.id).order_by(Transaction.date.desc()).limit(5).all()
    
    # Get categories for expense breakdown
    categories = Category.query.filter_by(user_id=user.id).all()
    
    # Get goals
    goals = Goal.query.filter_by(user_id=user.id).limit(3).all()
    
    return render_template('dashboard.html', 
                         user=user, 
                         total_income=total_income,
                         total_expenses=total_expenses,
                         balance=balance,
                         recent_transactions=recent_transactions,
                         categories=categories,
                         goals=goals)

@app.route('/api/expense-chart')
@login_required
def expense_chart():
    user = current_user()
    current_date = datetime.now()
    start_of_month = current_date.replace(day=1)
    
    transactions = Transaction.query.filter(
        Transaction.user_id == user.id,
        Transaction.transaction_type == 'expense',
        Transaction.date >= start_of_month.date()
    ).all()
    
    # Group by category
    category_totals = defaultdict(float)
    for transaction in transactions:
        category = Category.query.get(transaction.category_id)
        if category:
            category_totals[category.name] += transaction.amount
    
    return jsonify({
        'labels': list(category_totals.keys()),
        'data': list(category_totals.values()),
        'colors': [Category.query.filter_by(name=name, user_id=user.id).first().color 
                  for name in category_totals.keys()]
    })

@app.route('/api/income-expense-trend')
@login_required
def income_expense_trend():
    user = current_user()
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    transactions = Transaction.query.filter(
        Transaction.user_id == user.id,
        Transaction.date >= start_date
    ).order_by(Transaction.date).all()
    
    daily_data = defaultdict(lambda: {'income': 0, 'expense': 0})
    
    for transaction in transactions:
        date_str = transaction.date.strftime('%Y-%m-%d')
        if transaction.transaction_type == 'income':
            daily_data[date_str]['income'] += transaction.amount
        else:
            daily_data[date_str]['expense'] += transaction.amount
    
    dates = sorted(daily_data.keys())
    income_data = [daily_data[date]['income'] for date in dates]
    expense_data = [daily_data[date]['expense'] for date in dates]
    
    return jsonify({
        'dates': dates,
        'income': income_data,
        'expenses': expense_data
    })

@app.route('/categories', methods=['GET', 'POST'])
@login_required
def categories():
    user = current_user()
    
    if request.method == 'POST':
        name = request.form['name']
        color = request.form['color']
        icon = request.form['icon']
        
        if name:
            category = Category(name=name, color=color, icon=icon, user_id=user.id)
            db.session.add(category)
            db.session.commit()
            flash('Category added successfully!', 'success')
    
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
        transaction_type = request.form['transaction_type']
        date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        category_id = int(request.form['category_id'])
        notes = request.form.get('notes', '')
        
        transaction = Transaction(
            title=title, 
            amount=amount, 
            transaction_type=transaction_type,
            date=date, 
            category_id=category_id, 
            user_id=user.id,
            notes=notes
        )
        db.session.add(transaction)
        db.session.commit()
        flash('Transaction added successfully!', 'success')
        return redirect(url_for('transactions'))
    
    # Get transactions with pagination
    page = request.args.get('page', 1, type=int)
    txs = Transaction.query.filter_by(user_id=user.id).order_by(Transaction.date.desc()).all()
    
    return render_template('transactions.html', transactions=txs, categories=categories)

@app.route('/goals', methods=['GET', 'POST'])
@login_required
def goals():
    user = current_user()
    
    if request.method == 'POST':
        title = request.form['title']
        target_amount = float(request.form['target_amount'])
        target_date = datetime.strptime(request.form['target_date'], '%Y-%m-%d').date()
        
        goal = Goal(title=title, target_amount=target_amount, target_date=target_date, user_id=user.id)
        db.session.add(goal)
        db.session.commit()
        flash('Goal created successfully!', 'success')
        return redirect(url_for('goals'))
    
    user_goals = Goal.query.filter_by(user_id=user.id).all()
    return render_template('goals.html', goals=user_goals)

@app.route('/budget', methods=['GET', 'POST'])
@login_required
def budget():
    user = current_user()
    categories = Category.query.filter_by(user_id=user.id).all()
    current_date = datetime.now()
    
    if request.method == 'POST':
        category_id = int(request.form['category_id'])
        amount = float(request.form['amount'])
        month = int(request.form.get('month', current_date.month))
        year = int(request.form.get('year', current_date.year))
        
        existing_budget = Budget.query.filter_by(
            user_id=user.id, 
            category_id=category_id, 
            month=month, 
            year=year
        ).first()
        
        if existing_budget:
            existing_budget.amount = amount
        else:
            budget_item = Budget(
                category_id=category_id, 
                amount=amount, 
                month=month, 
                year=year, 
                user_id=user.id
            )
            db.session.add(budget_item)
        
        db.session.commit()
        flash('Budget updated successfully!', 'success')
        return redirect(url_for('budget'))
    
    # Get current month's budgets
    budgets = Budget.query.filter_by(
        user_id=user.id, 
        month=current_date.month, 
        year=current_date.year
    ).all()
    
    return render_template('budget.html', budgets=budgets, categories=categories)

@app.route('/profile')
@login_required
def profile():
    user = current_user()
    
    # Calculate user statistics
    total_transactions = Transaction.query.filter_by(user_id=user.id).count()
    total_categories = Category.query.filter_by(user_id=user.id).count()
    total_goals = Goal.query.filter_by(user_id=user.id).count()
    
    return render_template('profile.html', 
                         user=user, 
                         total_transactions=total_transactions,
                         total_categories=total_categories,
                         total_goals=total_goals)

@app.route('/export')
@login_required
def export():
    user = current_user()
    transactions = Transaction.query.filter_by(user_id=user.id).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Title', 'Amount', 'Type', 'Date', 'Category', 'Notes'])
    
    for t in transactions:
        category = Category.query.get(t.category_id)
        writer.writerow([
            t.title, 
            t.amount, 
            t.transaction_type,
            t.date, 
            category.name if category else 'Unknown',
            t.notes or ''
        ])
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()), 
        mimetype='text/csv', 
        as_attachment=True, 
        download_name=f'budget_buddy_export_{datetime.now().strftime("%Y%m%d")}.csv'
    )

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
