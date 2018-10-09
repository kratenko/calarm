from flask import Flask
from flask import render_template, request

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/dev/new')
def device_new():
    error = None
    if request.method == 'POST':
        pass
    return render_template('device_new.html', error=error)


if __name__ == '__main__':
    app.run()
