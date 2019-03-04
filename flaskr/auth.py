import functools

from flask import (
	Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

# Create blueprint named auth, all requests that begin with /auth
bp = Blueprint('auth', __name__, url_prefix='/auth')

# Associates /auth/register with register()
@bp.route('/register', methods=('GET', 'POST'))
def register():
	if request.method == 'POST':
		# Special dict from view
		username = request.form['username']
		password = request.form['password']
		db = get_db()
		error = None

		if not username:
			error = 'Username is required.'
		elif not password:
			error = 'Password is required.'
		elif db.execute(
			'SELECT id FROM user WHERE username = ?', (username,)
		).fetchone() is not None:
		# fetchone returns one row (should be zero for new user)
			error = 'User {} is already registered.'.format(username)

		if error is None:
			# This library prevents injection attacks
			db.execute(
				'INSERT INTO user (username, password) VALUES (?,?)',
				(username, generate_password_hash(password))
			)
			# Need to commit after modification
			db.commit()
			# Redirect user to login page
			return redirect(url_for('auth.login'))

		# flash stores errors and messages to be rendered
		flash(error)
	return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		db = get_db()
		error = None
		user = db.execute(
			'SELECT * FROM user WHERE username = ?', (username, )
		).fetchone()

		if user is None:
			error = 'Incorrect username.'
		elif not check_password_hash(user['password'], password):
			error = "Incorrect password."

		if error is None:
			# Session is dict with data stored across sessions
			session.clear()
			session['user_id'] = user['id']
			return redirect(url_for('index'))

		flash(error)

	return render_template('auth/login.html')

# Decorator registers function to run before the view, no matter what the URL is
@bp.before_app_request
def load_logged_in_user():
	user_id = session.get('user_id')

	if user_id is None:
		g.user = None
	else:
		g.user = get_db().execute(
			'SELECT * FROM user WHERE id = ?', (user_id,)
		).fetchone()

@bp.route('/logout')
def logout():
	session.clear()
	return redirect(url_for('index'))


# Create decorator to be called before loading the view
def login_required(view):
	@functools.wraps(view)
	def wrapped_view(**kwargs):
		if g.user is None:
			# This is how to call things from blueprint.
			return redirect(url_for('auth.login'))

		return view(**kwargs)
	return wrapped_view