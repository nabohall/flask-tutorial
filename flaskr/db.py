import sqlite3

# g is object made for each request
# current_app is object that points to Flask app handling request
import click
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
	if 'db' not in g:
		g.db = sqlite3.connect(
			current_app.config['DATABASE'],
			detect_types=sqlite3.PARSE_DECLTYPES
		)
		#return rows that behave like dicts
		g.db.row_factory = sqlite3.Row

	return g.db

def close_db(e=None):
	db=g.pop('db',None)

	if db is not None:
		db.close()

def init_db():
	db = get_db()

	# open_resource looks for file local to flaskr package
	with current_app.open_resource('schema.sql') as f:
		db.executescript(f.read().decode('utf-8'))

# click.command creates a CLI command called init-db
@click.command('init-db')
@with_appcontext
def init_db_command():
	"""Clear the existing data and create new tables."""
	init_db()
	click.echo('Initialized the database')

# Register necessary functions to the application
def init_app(app):
	# app.teardown_appcontext specifies function to call after returning response
	app.teardown_appcontext(close_db)
	# app.cli.add_command adds new command that can be called via flask CLI (>flast command)
	app.cli.add_command(init_db_command)