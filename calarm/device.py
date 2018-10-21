import functools
import random
import re

import flask
from flask import render_template, request

from calarm.db import get_db

bp = flask.Blueprint('device', __name__, url_prefix='/device')


@bp.route("/callback", methods=('POST','GET'))
def callback():
    db = get_db()
    db.execute(
        'INSERT INTO dump (url, dumped) VALUES(?,?)',
        ("/ttn/callback", flask.request.get_data())
    )
    db.commit()
    return "Ok"

def generate_appkey():
    return ''.join(random.choices("0123456789ABCDEF", k=32))


def deveui_from_form():
    try:
        deveui = request.form['deveui']
    except KeyError:
        return "", "DevEUI is missing."
    error = None
    deveui = deveui.upper()
    deveui = re.sub(r"\s+", "", deveui)
    if deveui.startswith("0X"):
        deveui = deveui[2:]
    if not re.match("^[0-9A-F]{16}$", deveui):
        error = "DevEUI must be exactly 16 hex digits."
    return deveui, error


def name_from_form():
    try:
        name = request.form['name']
    except KeyError:
        return "", "Name is missing."
    error = None
    if not 2 <= len(name) <= 32:
        error = "Name must be 2 to 32 chars long."
    elif not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name):
        error = "Name must consist of only a-z, 0-9, and single '-' chars in the middle."
    elif re.match(r"^[a-z0-9]{16}$", name):
        error = "Name must not consist of exactly 16 digits and letters."
    return name, error


def description_from_form():
    try:
        description = request.form['description']
    except KeyError:
        description = ""
    error = None
    return description[:512], error


def register_device():
    error = {}
    deveui, err = deveui_from_form()
    if err:
        error['deveui'] = err
    name, err = name_from_form()
    if err:
        error['name'] = err
    description, err = description_from_form()
    if err:
        error['description'] = err
    if error:
        return error
    appeui = ""
    appkey = generate_appkey()
    return {"top":appkey}


@bp.route('/new', methods=['GET', 'POST'])
def device_new():
    error = {}
    if request.method == 'POST':
        error = register_device()
        if not error:
            return None
    return render_template('device_new.html', error=error)


