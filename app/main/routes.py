from werkzeug.urls import url_parse
from datetime import datetime
from guess_language import guess_language
from flask import render_template, flash, redirect, url_for, request, g, jsonify, Markup
from flask_login import current_user, login_user, logout_user, login_required
from flask_babel import _, get_locale
from app import db
from app.models import User, Education, WorkHistory, Award, Duty
from app.main.forms import LoginForm, RegistrationForm, EditProfileForm, ResetPasswordRequestForm, ResetPasswordForm, AddHistoryForm, EditHistoryForm, AddDutyForm, EmptyForm
from app.main import bp, maps
from config import Config
from folium.plugins import MarkerCluster
import folium, json, pdfkit
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
		current_user.agency = form.agency.data
		current_user.coverletter = form.coverletter.data
		db.session.commit()
		flash(_('Your changes have been saved.'))
		return redirect(url_for('main.edit_profile'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.agency.data = current_user.agency
		form.coverletter.data = current_user.coverletter
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

@bp.route('/education')
def education():
	schools = Education.query.all()
	return render_template('education.html', schools=schools)

@bp.route('/work_history')
def work_history():
	jobs = WorkHistory.query.order_by(WorkHistory.start_date.desc()).all()
	start_coords=[45.5584432,-114.5665322]
	m=folium.Map(location=start_coords,width=750, height=500,zoom_start=6,tiles=None,)
	folium.raster_layers.TileLayer(
		tiles='OpenStreetMap', name='Open Street Map').add_to(m)
	folium.raster_layers.TileLayer(
		tiles='stamenterrain', name='Terrain').add_to(m)
	folium.raster_layers.WmsTileLayer(
		url='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
		layers=None,
		name='Aerial',
		attr='ESRI World Imagery',
		show=False).add_to(m)
	marker_cluster=MarkerCluster(control=False).add_to(m)
	for job in jobs:
		popup=render_template('job_popup.html',name=job.name, title=job.title,url=job.url)
		folium.Marker([job.lat, job.lon],popup=popup).add_to(marker_cluster)
	fg=folium.FeatureGroup(name='Work History')
	folium.LayerControl().add_to(m)
	m=Markup(m.get_root().render())	
	return render_template('work_history.html', jobs=jobs, map=m)

@bp.route('/awards')
def awards():
	awards=Award.query.order_by(Award.start_date.desc()).all()
	return render_template('awards.html', awards=awards)

@bp.route('/job/<title>')
def job(title):
	j=WorkHistory.query.filter_by(title=title).first()
	duties=Duty.query.filter_by(job_id=j.id)
	return render_template('job.html',
		name=j.name,
		title=j.title,
		duties=duties,
		supervisor=j.supervisor,
		supervisor_title=j.supervisor_title,
		supervisor_email=j.supervisor_email,
		supervisor_phone=j.supervisor_phone)

@bp.route('/edit_history')
def edit_history():
	jobs = WorkHistory.query.order_by(WorkHistory.start_date.desc()).all()
	return render_template('edit_history.html', jobs=jobs)

@bp.route('/add_history', methods=['GET', 'POST'])
def add_history():
	form=AddHistoryForm()
	if form.validate_on_submit():
		job = WorkHistory(url = form.url.data,
						  name = form.name.data,
						  title = form.title.data,
						  location = form.location.data,
						  start_date = form.start_date.data,
						  end_date = form.end_date.data,
						  lat = form.lat.data,
						  lon = form.lon.data,
						  supervisor= form.supervisor.data,
						  supervisor_title= form.supervisor_title.data,
						  supervisor_email=form.supervisor_email.data,
						  supervisor_phone=form.supervisor_phone.data)
		db.session.add(job)
		db.session.commit()
		flash(_('Congratulations, job added!'))
		return redirect(url_for('main.work_history'))
	return render_template('add_history.html', form=form)

@bp.route('/edit_history2/<title>', methods=['GET', 'POST'])
def edit_history2(title):
	job=WorkHistory.query.filter_by(title=title).first()
	form=EditHistoryForm(title=title)
	if  form.validate_on_submit():
		job = WorkHistory(url = form.url.data,
						  name = form.name.data,
						  title = form.title.data,
						  location = form.location.data,
						  start_date = form.start_date.data,
						  end_date = form.end_date.data,
						  lat = form.lat.data,
						  lon = form.lon.data,
						  supervisor= form.supervisor.data,
						  supervisor_title= form.supervisor_title.data,
						  supervisor_email=form.supervisor_email.data,
						  supervisor_phone=form.supervisor_phone.data)
		db.session.commit()
		# return redirect(url_for('main.edit_history'))
	elif request.method == 'GET':
		form.url.data = job.url
		form.name.data = job.name
		form.title.data = job.title
		form.location.data = job.location
		form.start_date.data = job.start_date
		form.end_date.data = job.end_date
		form.lat = job.lat
		form.lon = job.lon
		form.supervisor = job.supervisor
		form.supervisor_title = job.supervisor_title
		form.supervisor_email = job.supervisor_email
		form.supervisor_phone = job.supervisor_phone
	return render_template('edit_history2.html',form=form, title=title)

@bp.route('/add_duty/<title>', methods=['GET', 'POST'])
def add_duty(title):
	job=WorkHistory.query.filter_by(title=title).first()
	form=AddDutyForm(title=title)
	if form.validate_on_submit:
		duty=Duty(job_id=job.id, body=form.duty.data)
		db.session.add(duty)
		db.session.commit()
		flash('Duty Added.')
		return redirect(url_for('main.edit_history'))

@bp.route('/contact')
def contact():
	return render_template('contact.html')

@bp.route('/about')
def about():
	return render_template('about.html')

@bp.route('/cover_letter/<username>')
def cover_letter(username):
	user = User.query.filter_by(username=username).first_or_404()
	return render_template('cover_letter.html',user=user)

@bp.route('/export_resume', methods=['GET','POST'])
def export_resume():
	jobs = WorkHistory.query.order_by(WorkHistory.start_date.desc()).all()
	education=Education.query.all()
	duties=Duty.query.all()
	return render_template('export_resume.html',
		education=education,
		jobs=jobs)

@bp.route('/export_resume_pdf.pdf')
def export_resume_pdf():
	jobs = WorkHistory.query.order_by(WorkHistory.start_date.desc()).all()
	education=Education.query.all()
	return pdfkit.from_string(render_template('export_resume.html',education=education,jobs=jobs),
		False,
		options={"enable-local-file-access":""})

@bp.route('/export_cover_letter/<username>')
def export_cover_letter(username):
	user=User.query.filter_by(username=username).first_or_404()
	return render_template('export_cover_letter.html', user=user)

@bp.route('/export_cover_letter_pdf.pdf')
def export_cover_letter_pdf():
	user=User.query.filter_by(username=current_user.username).first_or_404()
	return pdfkit.from_string(render_template('export_cover_letter.html',user=user),
		False,
		options={"enable-local-file-access":""})