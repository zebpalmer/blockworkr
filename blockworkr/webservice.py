from flask import Flask, request, Response, abort, redirect, send_from_directory
from blockworkr import __version__




app = Flask("Blockworkr")
from werkzeug.contrib.fixers import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app)



@app.route("/")
def index():
    """
    Blockworkr Webservice Root
    """
    return f"Blockworkr Webservice {__version__}"

