import jwt, json, base64, os
from time import time
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from time import time
from hashlib import md5
from flask_login import UserMixin
from flask import current_app, url_for
from app import db, login

class PaginatedAPIMixin(object):
	@staticmethod
	def to_collection_dict(query, page, per_page, endpoint, **kwargs):
		resources = query.paginate(page, per_page, False)
		data = {
			'items': [item.to_dict() for item in resources.items],
			'_meta': {
				'page': page,
				'per_page': per_page,
				'total_pages': resources.pages,
				'total_items': resources.total
			},
			'_links': {
				'self': url_for(endpoint, page=page, per_page=per_page, **kwargs),
				'next': url_for(endpoint, page=page + 1, per_page=per_page, **kwargs) \
					if resources.has_next else None,
				'prev': url_for(endpoint, page=page - 1, per_page=per_page, **kwargs) \
					if resources.has_prev else None
			}
		}
		return data

class User(PaginatedAPIMixin, UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	about_me = db.Column(db.String(140))
	last_seen = db.Column(db.DateTime, default=datetime.utcnow)
	
	def get_reset_password_token(self, expires_in=600):
		return jwt.encode(
			{'reset_password': self.id, 'exp': time() + expires_in},
			app.config['SECRET_KEY'], algorithm='HS256'.decode('utf-8'))

	@staticmethod
	def verify_reset_password_token(token):
		try:
			id = jwt.decode(token, app.config['SECRET_KEY'],
							algorithms=['HS256'])['reset_password']
		except:
			return
		return User.query.get(id)

	def avatar(self, size):
		digest = md5(self.email.lower().encode('utf-8')).hexdigest()
		return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest,size)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	def __repr__(self):
		return '<User {}>'.format(self.username)

@login.user_loader
def load_user(id):
	return User.query.get(int(id))	
		
class Education(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	url = db.Column(db.String(140))
	name = db.Column(db.String(120))
	title = db.Column(db.String(120))
	location = db.Column(db.String(120))

class WorkHistory(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	url = db.Column(db.String(140))
	name = db.Column(db.String(120))
	title = db.Column(db.String(120))
	location = db.Column(db.String(120))
	start_date = db.Column(db.DateTime)
	end_date = db.Column(db.DateTime, default=datetime.utcnow)

class Award(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	url=db.Column(db.String(140))
	name=db.Column(db.String(120))
	agency=db.Column(db.String(120))
	expiration_date=db.Column(db.DateTime)
	license_number=db.Column(db.String(30))
		