from flask import Blueprint, request, redirect, render_template, url_for, flash
from . import db
from .models import User
from flask_login import login_user, logout_user, login_required

auth = Blueprint('auth', __name__)


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.form
        username = data['username']
        email = data['email']
        password = data['password']

        if db.session.query(User).filter_by(username=username).first() is not None:
            flash('Username taken')
            return render_template('signup.html', email=email, password=password)

        if db.session.query(User).filter_by(email=email).first() is not None:
            flash('You already have an account')
            return redirect(url_for('auth.login'))
        new_user = User(username=username, email=email)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()
        flash('Successfully registered. Log in to continue')
        return redirect(url_for('auth.login'))
    else:
        return render_template('signup.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        username = data['username']
        password = data['password']

        user = db.session.query(User).filter_by(username=username).first()
        if user:
            if user.check_password(password):
                login_user(user)
                return redirect(url_for('main.home'))
        flash("Invalid username or password")
        return render_template('login.html')
    else:
        return render_template('login.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))