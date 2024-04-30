from flask import Flask, request, session, redirect, url_for, render_template, flash, g
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    budget = db.Column(db.Float, nullable=False, default=0.0)
    transactions = db.relationship('Transaction', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.budget}')"


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Transaction('{self.date}', '{self.amount}', '{self.description}')"


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            flash('Неверное имя пользователя или пароль', 'error')
    return render_template('login.html')


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/transactions')
def transactions():
    user_transactions = Transaction.query.filter_by(user_id=session['user_id']).all()
    return render_template('transactions.html', transactions=user_transactions)


@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    amount = float(request.form.get('amount'))
    description = request.form.get('description')
    user_id = session['user_id']
    transaction = Transaction(date=datetime.now(timezone.utc), amount=amount, description=description,
                              user_id=user_id)
    db.session.add(transaction)
    db.session.commit()
    return redirect(url_for('transactions'))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        b = float(request.form.get('start_budget'))
        user = User(username=username, password=password, budget=b)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('register.html')


@app.route('/budget')
def budget():
    user = User.query.filter_by(id=session['user_id']).first()
    start_budget = user.budget
    user_transactions = Transaction.query.filter_by(user_id=session['user_id']).all()
    total_spent = sum(transaction.amount for transaction in user_transactions)
    current_budget = start_budget - total_spent

    return render_template('budget.html', current_budget=current_budget, total_spent=total_spent,
                           start_budget=start_budget)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
