import unittest
from app import create_app, db
from app.models import User, WorkHistory, Duty, Education, Award
from config import Config
from datetime import datetime, timedelta

class TestConfig(Config):
	TESTING = True
	SQLALCHEMY_DATABASE_URI = 'sqlite://'

class UserModelCase(unittest.TestCase):
	def setUp(self):
		self.app = create_app(TestConfig)
		self.app_context = self.app.app_context()
		self.app_context.push()
		db.create_all()

	def tearDown(self):
		db.session.remove()
		db.drop_all()
		self.app_context.pop()

	def test_password_hashing(self):
		u = User(username='susan')
		u.set_password('cat')
		self.assertFalse(u.check_password('dog'))
		self.assertTrue(u.check_password('cat'))

class WorkHistoryModelCase(unittest.TestCase):
	def setUp(self):
		self.app = create_app(TestConfig)
		self.app_context = self.app.app_context()
		self.app_context.push()
		db.create_all()

	def tearDown(self):
		db.session.remove()
		db.drop_all()
		self.app_context.pop()

	def test_add_duty(self):
		now=datetime.utcnow()
		w1=WorkHistory(url = 'test.com',
			name = 'Testing Company',
			title = 'Product Tester',
			location = 'Fakesville',
			start_date = now + timedelta(days=-365),
			end_date = now,
			lat = 0,
			lon = 0,
			supervisor= 'Supervisor',
			supervisor_title= 'Manager',
			supervisor_email='supervisor@testingcompany.com',
			supervisor_phone='123-456-789')
		w2=WorkHistory(url = 'test2.com',
			name = 'Testing Company2',
			title = 'Product Tester2',
			location = 'Fakesville',
			start_date = now + timedelta(days=-365),
			end_date = now,
			lat = 0,
			lon = 0,
			supervisor= 'Supervisor',
			supervisor_title= 'Manager',
			supervisor_email='supervisor@testingcompany.com',
			supervisor_phone='123-456-789')
		db.session.add_all([w1,w2])
		d1=Duty(body='Did some stuff',job_id=w1.id)
		d2=Duty(body='Did some other stuff', job_id=w2.id)
		db.session.add_all([d1,d2])
		db.session.commit()
		self.assertEqual(w1.duties, d1)
		self.assertEqual(w2.duties, d2)
if __name__=='__main__':
	unittest.main(verbosity=2)