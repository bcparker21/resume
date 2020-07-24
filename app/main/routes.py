from werkzeug.urls import url_parse
from datetime import datetime
from guess_language import guess_language
from flask import render_template, flash, redirect, url_for, request, g, jsonify, Markup
from flask_login import current_user, login_user, logout_user, login_required
from flask_babel import _, get_locale
from app import db
from app.models import User
from app.main.forms import LoginForm, RegistrationForm, EditProfileForm, ResetPasswordRequestForm, ResetPasswordForm
from app.main import bp
from config import Config
import folium, json
import geopandas as gpd

@bp.before_request
def before_request():
	if current_user.is_authenticated:
		current_user.last_seen = datetime.utcnow()
		db.session.commit()
	g.locale = str(get_locale())

@bp.route('/', methods=['GET','POST'])
@bp.route('/index', methods=['GET','POST'])
def index():
	return render_template('index.html')

@bp.route('/login', methods=['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash(_('Invalid username or password'))
			return redirect(url_for('login'))
		login_user(user, remember=form.remember_me.data)
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('index')
		return redirect(url_for('index'))
	return render_template('login.html', title=_('Sign In'), form=form)

@bp.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))

@bp.route('/register', methods=['GET','POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form=RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data, email=form.email.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash(_('Congratulations, you are now a registered user!'))
		return redirect(url_for('login'))
	return render_template('register.html', title=_('Register'), form=form)

@bp.route('/user/<username>')
@login_required
def user(username):
	user = User.query.filter_by(username=username).first_or_404()
	return render_template('user.html',user=user)

@bp.route('/edit_profile', methods=['GET','POST'])
@login_required
def edit_profile():
	form = EditProfileForm(current_user.username)
	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.about_me = form.about_me.data
		db.session.commit()
		flash(_('Your changes have been saved.'))
		return redirect(url_for('edit_profile'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.about_me.data = current_user.about_me
	return render_template('edit_profile.html', title=_('Edit Profile'), form=form)

@bp.route('/reset_password_request', methods=['GET','POST'])
def reset_password_request():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = ResetPasswordRequestForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user:
			send_password_reset_email(user)
		flash(_('Check your email for the instructions to reset your password'))
		return redirect(url_for('login'))
	return render_template('reset_password_request.html',
							title=_('Reset Password'), form=form)

@bp.route('/reset_password/<token>', methods=['GET','POST'])
def reset_password(token):
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	user = User.verify_reset_password_token(token)
	if not user:
		return redirect(url_for('index'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
		user.set_password(form.password.data)
		db.session.commit()
		flash(_('Your password has been reset.'))
		return redirect(url_for('login'))
	return render_template('reset_password.html', form=form)