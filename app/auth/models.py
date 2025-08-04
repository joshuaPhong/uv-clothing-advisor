from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from .. import db


class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	password_hash = db.Column(db.String(128), nullable=False)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	def get_id(self):
		return str(self.id)

	def __repr__(self):
		return f"<User {self.username}>"


# --- Helper functions ---

def get_user_by_id(user_id):
	return User.query.get(int(user_id))


def get_user_by_username(username):
	return User.query.filter_by(username=username).first()


def create_user(username, email, password):
	if get_user_by_username(username):
		return None  # Username already exists

	new_user = User(username=username, email=email)
	new_user.set_password(password)

	db.session.add(new_user)
	db.session.commit()
	return new_user
