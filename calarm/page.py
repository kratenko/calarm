import flask

bp = flask.Blueprint('page', __name__, url_prefix='/page')

PAGES = {
    'about': """
Cyber alarm!
""",
    'register': """
<h1>Register new Cyber Alarm Device</h1>
You can create your own LoRaWAN Cyber Alarm Device! To register it with the Deep Cyber 
TTN-Application you will need our help. Write us a mail to alarm [at] deepcyber.de.
Or better yet, come visit us during the 35C3 at our assembly (and hopefully someone 
will be there who can help you).
""",
    "datenschutz": """
<h1>Datenschutz</h1>
This web page does not allow you, to enter any data. Somewhere in the server, your IP 
will be logged, but I don't think we'll ever take a look in those logs...<br>
If you register a device on our ttn-app we will store the data your device transmits.
That data will be displayed on our web page and might be transmitted to twitter or some 
other social network services. 
<br>
We preserve the right to delete any data as we see fit.
""",
    'imprint': """
<h1>Imprint</h1>
'Tis but a little toy! 🙇For more look at
<a href="https://www.deepcyber.de/imprint/">https://www.deepcyber.de/imprint</a>.
<h1>Impressum</h1>
Dies ist nicht mehr als ne kleine Anwendung, die LoRaWAN demonstrieren soll. 
Ein Spielzeug. Wenn jemand ernsthaft n Problem damit hat, schaut unter 
<a href="https://www.deepcyber.de/imprint/">https://www.deepcyber.de/imprint</a>.
<h1>Disclaimer</h1>
There might be content displayed here sent to us from 3rd parties. We will remove them, 
if we know of problems with those contents.
"""
}


@bp.route("/<slug>")
def page(slug):
    try:
        return flask.render_template("page.html", slug=slug, content=PAGES[slug])
    except KeyError:
        flask.abort(404)
