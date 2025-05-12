import os
import secrets
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, oauth
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            flash('Logged in successfully!', category='success')
            login_user(user, remember=True)
            return redirect(url_for('views.home'))
        if user:
            flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/login/google')
def login_google():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    redirect_uri = url_for('auth.auth_google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth.route('/authorize/google')
def auth_google_callback():
    # Exchange code for tokens
    token = oauth.google.authorize_access_token()

    # Parse & verify the ID token (with nonce)
    nonce     = token.get('nonce')
    user_info = oauth.google.parse_id_token(token, nonce)

    # Lookup or create our local user
    email = user_info['email']
    user  = User.query.filter_by(email=email).first()
    if not user:
        # Generate a URL-safe random string, then hash it
        random_password = secrets.token_urlsafe(16)
        random_pw       = generate_password_hash(random_password)

        user = User(
            email=email,
            first_name=user_info.get('name', '').split(' ')[0],
            password=random_pw
        )
        db.session.add(user)
        db.session.commit()

    # Log them in
    login_user(user, remember=True)
    flash('Logged in with Google!', category='success')
    return redirect(url_for('views.home'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email      = request.form.get('email')
        first_name = request.form.get('firstName')
        password1  = request.form.get('password1')
        password2  = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash("Passwords don't match.", category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(
                email=email,
                first_name=first_name,
                password=generate_password_hash(password1, method='pbkdf2:sha256')
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)
