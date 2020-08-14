from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, DateTimeField, FloatField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from flask_babel import _, lazy_gettext as _l
from app.models import User

class LoginForm(FlaskForm):
	username = StringField(_l('Username'), validators=[DataRequired()])
	password = PasswordField(_l('Password'), validators=[DataRequired()])
	remember_me = BooleanField(_l('Remember Me'))
	submit = SubmitField(_l('Sign In'))

class RegistrationForm(FlaskForm):
	username = StringField(_l('Username'), validators=[DataRequired()])
	email = StringField(_l('Email'), validators=[DataRequired(),Email()])
	password = PasswordField(_l('Password'), validators=[DataRequired()])
	password2 = PasswordField(_l('Repeat Password'), validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField(_l('Register'))

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user is not None:
			raise ValidationError(_('Please use a different username.'))

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is not None:
			raise ValidationError(_('Please use a different email address.'))

class EditProfileForm(FlaskForm):
	__tablename__='user'
	username = StringField(_l('Username'), validators=[DataRequired()])
	agency = StringField(_l('Agency'), validators=[Length(min=0, max=120)])
	coverletter=TextAreaField('Cover Letter')
	submit = SubmitField(_l('Submit'))

	def __init__(self, original_username, *args, **kwargs):
		super(EditProfileForm, self).__init__(*args, **kwargs)
		self.original_username = original_username

	def validate_username(self, username):
		if username.data != self.original_username:
			user = User.query.filter_by(username=self.username.data).first()
			if user is not None:
				raise ValidationError(_('Please use a different username.'))
		
class ResetPasswordRequestForm(FlaskForm):
	email = StringField(_l('Email'), validators=[DataRequired(), Email()])
	submit = SubmitField(_l('Request Password Reset'))

class ResetPasswordForm(FlaskForm):
	password = PasswordField(_l('Password'), validators=[DataRequired()])
	password2 = PasswordField(_l('Repeat Password'), validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField(_l('Reset Password'))
		
class AddHistoryForm(FlaskForm):
	url = StringField(_l('Website'))
	name = StringField(_l('Company'), validators=[DataRequired()])
	title = StringField(_l('Job Title'), validators=[DataRequired()])
	location = StringField(_l('Location'))
	start_date = DateTimeField(_l('Start Date'), validators=[DataRequired()])
	end_date = DateTimeField(_l('End Date'))
	lat = FloatField(_l('Latitude'))
	lon = FloatField(_l('longitude'))
	supervisor=StringField(_l('Supervisor'))
	supervisor_title=StringField(_l('Supervisor Title'))
	supervisor_email=StringField(_l('Supervisor Email'), validators=[Email()])
	supervisor_phone=StringField(_l('Supervisor Phone'))
	submit = SubmitField(_l('Add History'))

class EditHistoryForm(FlaskForm):
	url = StringField(_l('Website'))
	name = StringField(_l('Company'), validators=[DataRequired()])
	title = StringField(_l('Job Title'), validators=[DataRequired()])
	location = StringField(_l('Location'))
	start_date = DateTimeField(_l('Start Date'), validators=[DataRequired()])
	end_date = DateTimeField(_l('End Date'))
	lat = FloatField(_l('Latitude'))
	lon = FloatField(_l('longitude'))
	supervisor=StringField(_l('Supervisor'))
	supervisor_title=StringField(_l('Supervisor Title'))
	supervisor_email=StringField(_l('Supervisor Email'), validators=[Email()])
	supervisor_phone=StringField(_l('Supervisor Phone'))
	submit = SubmitField(_l('Edit History'))

class AddDutyForm(FlaskForm):
	duty=TextAreaField(_l('Add Duty'), validators=[DataRequired()])
	submit=SubmitField(_l('Add Duty'))

class EmptyForm(FlaskForm):
	submit=SubmitField('Submit')
		
class AddEducationForm(FlaskForm):
	url = StringField(_l('Website'))
	name = StringField(_l('Name'))
	title = StringField(_l('Title'))
	location = StringField(_l('Location'))
	submit=SubmitField(_l('Add Education'))

class AddAwardForm(FlaskForm):
	url=StringField(_l('Website'))
	name=StringField(_l('Name'))
	agency=StringField(_l('Agency'))
	expiration_date=StringField(_l('Expiration Date'))
	license_number=StringField(_l('License Number'))
	start_date=StringField(_l('Start Date'))
	end_date=StringField(_l('End Date'))
	submit=SubmitField(_l('Add Award'))

class EditEducationForm(FlaskForm):
	url = StringField(_l('Website'))
	name = StringField(_l('Name'))
	title = StringField(_l('Degree'))
	location = StringField(_l('Location'))
	submit=SubmitField(_l('Edit Education'))
		