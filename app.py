from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from forms import LoginForm, RegistrationForm, SetAlertForm, ProfileForm
import requests
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login failed. Check your credentials.', 'danger')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data, password=form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        db.session.commit()
        flash('Profile updated successfully!', 'success')
    return render_template('profile.html', form=form)

@app.route('/stock/<symbol>', methods=['GET'])
@login_required
def stock(symbol):
    response = requests.get(f'https://api.example.com/stock/{symbol}')  # Replace with actual API
    if response.status_code != 200:
        flash('Error fetching stock data. Please try again later.', 'danger')
        return redirect(url_for('index'))
    stock_data = response.json()
    return render_template('stock.html', symbol=symbol, stock_data=stock_data)

@app.route('/set_alert', methods=['GET', 'POST'])
@login_required
def set_alert():
    form = SetAlertForm()
    if form.validate_on_submit():
        # Set alert logic here
        flash('Stock alert set!', 'success')
        return redirect(url_for('index'))
    return render_template('set_alert.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
