from flask import render_template, current_app
from flask_babel import _ 
from app.email import send_email

def send_password_reset_email(user):
	token = user.get_reset_password_token()
	send_email(_('Brian Parker Reset Your Password'),
				sender=app.config['ADMINS'][0],
				recipients=[user.email],
				text_body=render_template('email/reset_password.txt',
											user=user, token=token),
				html_body=render_template('email/reset_password.html',
											user=user, token=token))

def send_new_login_email(user):
	send_email(_('New Resume Login'),
				sender=app.config['ADMINS'][0],
				recipients='bcparker21@gmail.com',
				text_body=render_template('email/new_login.txt',user=user),
				html_body=render_template('email/new_login.html',user=user))