import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

DIRTY_DB_PATH = ""


class dirty_db:
    db = None

    def __enter__(self):
        self.db = sqlite3.connect(
            DIRTY_DB_PATH,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        self.db.row_factory = sqlite3.Row
        return self.db

    def __exit__(self, *args, **vargs):
        if self.db:
            self.db.close()


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    global DIRTY_DB_PATH
    DIRTY_DB_PATH = app.config['DATABASE']
