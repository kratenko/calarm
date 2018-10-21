import re
import random
import os

from flask import Flask
from flask import render_template, request
from calarm.db import get_db


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'calarm.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    from . import page
    app.register_blueprint(page.bp)
    from . import ttn
    app.register_blueprint(ttn.bp)
    from . import device
    app.register_blueprint(device.bp)

    return app


app = create_app()


@app.route('/')
def hello_world():
    db = get_db()
    alarms = db.execute(
        'SELECT devid, deveui, created, level, message'
        ' FROM alarm'
        ' ORDER BY created DESC'
        ' LIMIT 10'
    ).fetchall()
    return render_template("alarms.html", alarms=alarms)


if __name__ == '__main__':
    app.run()


