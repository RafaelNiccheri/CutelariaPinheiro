# website/auth.py

import os
from flask import (
    Blueprint, render_template, request,
    flash, redirect, url_for, current_app
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from authlib.integrations.flask_client import OAuthError

from . import db, oauth
from .models import User

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form.get('email')
        password = request.form.get('password')
        user     = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            # Create all tables in both the default and the per-user "management" bind
            with current_app.app_context():
                db.create_all()
            flash('Logged in successfully!', 'success')
            return redirect(url_for('views.home'))

        flash('Invalid email or password.', 'error')

    return render_template('login.html', user=current_user)


@auth.route('/login/google')
def login_google():
    redirect_uri = url_for('auth.authorize_google', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth.route('/login/google/authorize')
def authorize_google():
    try:
        token = oauth.google.authorize_access_token()
    except OAuthError:
        flash('Google login failed.', 'error')
        return redirect(url_for('auth.login'))

    userinfo = token.get('userinfo')
    if not userinfo:
        flash('Could not fetch user info from Google.', 'error')
        return redirect(url_for('auth.login'))

    email = userinfo.get('email')
    if not email:
        flash('No email returned by Google.', 'error')
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(email=email).first()
    if not user:
        # Generate a random hex string for the password
        random_pw = os.urandom(16).hex()
        user = User(
            email=email,
            first_name=userinfo.get('given_name', email.split('@')[0]),
            password=generate_password_hash(random_pw, method='pbkdf2:sha256')
        )
        db.session.add(user)
        db.session.commit()

    login_user(user, remember=True)
    # Initialize this user's management DB
    with current_app.app_context():
        db.create_all()

    flash('Logged in with Google!', 'success')
    return redirect(url_for('views.home'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email      = request.form.get('email')
        first_name = request.form.get('firstName')
        pw1        = request.form.get('password1')
        pw2        = request.form.get('password2')

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
        elif len(email) < 4:
            flash('Email must be at least 4 characters.', 'error')
        elif len(first_name) < 2:
            flash('First name must be at least 2 characters.', 'error')
        elif pw1 != pw2:
            flash("Passwords don't match.", 'error')
        elif len(pw1) < 7:
            flash('Password must be at least 7 characters.', 'error')
        else:
            new_user = User(
                email=email,
                first_name=first_name,
                password=generate_password_hash(pw1, method='pbkdf2:sha256')
            )
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user, remember=True)
            # Initialize this user's management DB
            with current_app.app_context():
                db.create_all()

            flash('Account created!', 'success')
            return redirect(url_for('views.home'))

    return render_template('sign_up.html', user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
