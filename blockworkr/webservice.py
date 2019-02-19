import logging
from datetime import datetime
from werkzeug.wsgi import DispatcherMiddleware
from prometheus_client import make_wsgi_app, Histogram, Summary, Counter, Gauge

from flask_caching import Cache
from blockworkr.log import setup_logging
from blockworkr.block import Block

# noinspection PyUnresolvedReferences
from flask import Flask, request, Response, abort, redirect, send_from_directory, jsonify
from blockworkr import SVC, SVCObj


setup_logging(name="blockworkr", loglevel="DEBUG")
logging.info("Blockworkr Starting")


ws = Flask("Blockworkr")

svc = SVC()
SVCObj.svc = svc

if svc.cfg.get("memcached_server"):
    cachecfg = {
        "CACHE_TYPE": "memcached",
        "CACHE_DEFAULT_TIMEOUT": 900,
        "CACHE_KEY_PREFIX": "blockworkrws",
        "CACHE_MEMCACHED_SERVERS": svc.cfg["memcached_server"][0],  # need list
    }
else:
    cachecfg = {"CACHE_TYPE": "simple"}

cache = Cache(ws, config=cachecfg)

# noinspection PyPep8,PyPackageRequirements
from werkzeug.contrib.fixers import ProxyFix

ws.wsgi_app = ProxyFix(ws.wsgi_app)

if svc.cfg.get("metricsz_enabled"):
    app = DispatcherMiddleware(ws, {"/metrics": make_wsgi_app()})
else:
    app = ws

svc.blockr = Block(cfg=svc.cfg)

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
    return "OK"


@ws.route("/<combo>.txt")
def unified(combo):
    res = gen_output(svc.blockr.unified(combo))
    return Response(res, mimetype="text/plain")


def gen_output(s):
    lines = sorted(s)
    return b"\n".join(lines)

