from app import create_app, db
from app.models import User, Education, WorkHistory, Award, Duty

app = create_app()

@app.shell_context_processor
def make_shell_context():
	return {'db':db,
			'User': User,
			'Education': Education,
			'WorkHistory': WorkHistory,
			'Award': Award,
			'Duty': Duty}