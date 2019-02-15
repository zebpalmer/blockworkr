import logging
from datetime import datetime
from werkzeug.wsgi import DispatcherMiddleware
from prometheus_client import make_wsgi_app, Histogram, Summary, Counter, Gauge

from blockworkr.log import setup_logging


# noinspection PyUnresolvedReferences
from flask import Flask, request, Response, abort, redirect, send_from_directory, jsonify
from blockworkr import SVC, SVCObj


setup_logging(name="blockworkr", loglevel="DEBUG")
logging.info("Blockworkr Starting")


ws = Flask("Blockworkr")

svc = SVC()
SVCObj.svc = svc


# noinspection PyPep8,PyPackageRequirements
from werkzeug.contrib.fixers import ProxyFix

ws.wsgi_app = ProxyFix(ws.wsgi_app)

if svc.cfg.get("metricsz_enabled"):
    app = DispatcherMiddleware(ws, {"/metrics": make_wsgi_app()})
else:
    app = ws


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
    return "OK"


@ws.route("/<combo>.txt")
def unified(combo):
    res = gen_output(svc.blockr.unified(combo))
    return Response(res, mimetype="text/plain")


def gen_output(s):
    lines = sorted(s)
    return b"\n".join(lines)


@ws.route("/configz")
def configz():
    if not svc.cfg.get("configz_enabled"):
        abort(403)
    return jsonify(svc.cfg)
