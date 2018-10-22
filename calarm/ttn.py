import functools
from typing import Iterator
import flask
# import ttn as tn
import os
import json
import hmac

from calarm.db import get_db, dirty_db

bp = flask.Blueprint('ttn', __name__, url_prefix='/ttn')


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    config = flask.current_app.config
    try:
        isuser = hmac.compare_digest(config['TTN_USER'], username)
        ispass = hmac.compare_digest(config['TTN_PASSWORD'], password)
    except KeyError:
        flask.current_app.logger.warn("No credentials for ttn specified.")
        return False
    return isuser and ispass


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return flask.Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )


def requires_auth(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        auth = flask.request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


def ping_pipe():
    pipe_path = "/tmp/calarm"
    try:
        os.mkfifo(pipe_path)
    except FileExistsError:
        # that's okay, actually
        pass
    try:
        with os.fdopen(os.open(pipe_path, os.O_WRONLY | os.O_NONBLOCK), "w") as pipe:
            pipe.write(".")
    except OSError:
        # no one listening? well, we tried...
        pass


@bp.route("/callback", methods=('POST',))
@requires_auth
def callback():
    print("AUTH", flask.request.headers)
    db = get_db()
    db.execute(
        'INSERT INTO dump (url, dumped) VALUES(?,?)',
        ("/ttn/callback", flask.request.get_data())
    )
    data = flask.request.get_json() or {}
    payload = data.get('payload_fields', {})
    db.execute(
        'INSERT INTO alarm (devid, deveui, action, level, message)'
        ' VALUES(?,?,?,?,?)',
        (
            data.get('dev_id', '[unknown]'),
            data.get('hardware_serial', '[unknown]'),
            payload.get('action', '[unknown]'),
            payload.get('level', None),
            payload.get('message', None),
        )
    )
    db.commit()
    ping_pipe()
    return "Ok"


@bp.route("/list",)
def list_devs():
    return "Ok"
    #handler = tn.HandlerClient(APP_ID, ACCESS_KEY)
    #ac = handler.application()
    #s = ""
    #for dev in ac.devices():
    #    s += dev.dev_id
    #return s


def get_events(since):
    with dirty_db() as db:
        events = db.execute(
            'SELECT id, devid, deveui, created, level, message'
            ' FROM alarm'
            ' WHERE id>?'
            ' ORDER BY devid ASC',
            (since,)
        ).fetchall()
    for ev in events:
        yield ev


@bp.route("/sub", methods=['POST', ])
@requires_auth
def subs():
    def gen(since) -> Iterator[str]:
        last = since
        while True:
            with os.fdopen(os.open("/tmp/calarm", os.O_RDONLY)) as _:
                for ev in get_events(last):
                    data = {
                        "event": "alarm",
                        "device": ev['devid'],
                        "level": ev['level'],
                        "number": ev['id'],
                        "timestamp": str(ev['created']),
                    }
                    last = max(last, ev['id'])
                    yield 'data: {}\n\n'.format(json.dumps(data))

    since = -1
    db = get_db()
    d = db.execute(
        'SELECT MAX(id) AS last_id'
        ' FROM alarm'
    ).fetchone()
    if d:
        since = d['last_id']
    return flask.Response(
        gen(since),
        mimetype="text/event-stream",
    )


#@bp.route("/push")
#def push():
#    ping_pipe()
#    return "Ok"
