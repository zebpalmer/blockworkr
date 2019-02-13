import logging
from datetime import datetime
from blockworkr.log import setup_logging
from flask import Flask, request, Response, abort, redirect, send_from_directory
from blockworkr import __version__, Block, SVC, SVCObj


setup_logging(name="blockworkr", loglevel="DEBUG")
logging.info("Blockworkr Starting")


ws = Flask("Blockworkr")

svc = SVC()
SVCObj.svc = svc

from werkzeug.contrib.fixers import ProxyFix

ws.wsgi_app = ProxyFix(ws.wsgi_app)


@ws.before_request
def check_update():
    if not svc.blockr.ready():
        abort(503, "Blocklist Unavailable (if blockworkr just started, lists may be updating)")


@ws.route("/")
def index():
    """
    Blockworkr Webservice Root
    """
    return f"Blockworkr Webservice {svc.__version__} at {datetime.utcnow()}"


@ws.route("/healthz")
def healthz():
    if not svc.blockr.ready():
        abort(500, "Blocklist Data Unavailable")
    return ""


@ws.route("/unified.txt")
def unified():
    res = gen_output(svc.blockr.unified)
    return Response(res, mimetype="text/plain")


def gen_output(s):
    l = sorted(s)
    return b"\n".join(l)
