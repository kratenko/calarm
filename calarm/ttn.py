import functools
import time
from typing import Iterator
import flask
import ttn as tn
import os
import json
import datetime

from calarm.db import get_db

bp = flask.Blueprint('ttn', __name__, url_prefix='/ttn')

APP_ID = "cyber-alarm"
APP_EUI = "70B3D57ED0013117"
ACCESS_KEY = "ttn-account-v2.ZYD0bRcPQlJouTA-5wyIVJJzwxMfw2auJcBacGBYRQ4"


@bp.route("/callback", methods=('POST', 'GET'))
def callback():
    db = get_db()
    db.execute(
        'INSERT INTO dump (url, dumped) VALUES(?,?)',
        ("/ttn/callback", flask.request.get_data())
    )
    db.commit()
    return "Ok"


@bp.route("/list",)
def list_devs():
    handler = tn.HandlerClient(APP_ID, ACCESS_KEY)
    ac = handler.application()
    s = ""
    for dev in ac.devices():
        s += dev.dev_id
    return s


@bp.route("/sub", methods=['POST', 'GET'])
def subs():
    L = flask.current_app.logger
    last = time.time()

    def gen() -> Iterator[str]:
        i = 0
        L.warn("Jo!")
        while True:
            L.warn("True")
            with os.fdopen(os.open("/tmp/calarm", os.O_RDONLY)) as pipe:
                L.warn("with")
                i += 1
                data = {
                    "event": "alarm",
                    "device": "unknown",
                    "level": 1,
                    "number": i,
                    "timestamp": str(datetime.datetime.now()),
                }
                yield 'data: {}\n\n'.format(json.dumps(data))
    return flask.Response(
        gen(),
        mimetype="text/event-stream",
    )


@bp.route("/push")
def push():
    with os.fdopen(os.open("/tmp/calarm", os.O_WRONLY | os.O_NONBLOCK), "w") as pipe:
        pipe.write("ping")
    return "Ok"
