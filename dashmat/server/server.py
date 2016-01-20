from dashmat.scheduler import Scheduler

from tornado.httpserver import HTTPServer
from tornado.wsgi import WSGIContainer
from tornado.ioloop import IOLoop

from flask import render_template, abort
from flask.helpers import send_file
from flask import Flask

import threading
import logging
import flask
import time
import os

log = logging.getLogger("dashmat.server")

here = os.path.dirname(__file__)

class Server(object):
    def __init__(self, host, port, debug, datastore, dashboards, checks, installed_widgets):
        self.thread_stopper = {"finished": False}

        self.host = host
        self.port = port
        self.debug = debug
        self.datastore = datastore

        self.checks = checks
        self.dashboards = dashboards
        self.installed_widgets = self.prepare_widgets(installed_widgets)

    def serve(self):
        http_server = HTTPServer(WSGIContainer(self.app))
        http_server.listen(self.port, self.host)
        log.info("Starting server on http://%s:%s", self.host, self.port)

        scheduler = Scheduler(self.datastore)
        for name, check_spec in self.checks.iteritems():
            # call init with the options
            CheckerKls = check_spec['import_path']
            checker = CheckerKls(**check_spec['options'])

            scheduler.register(checker, name)

        scheduler.start()

        try:
            IOLoop.instance().start()
        finally:
            self.thread_stopper["finished"] = True

    def prepare_widgets(self, installed_widgets):
        """
        Transform the installed widgets into a lookup dict based on the class name.

        :param installed_widgets: Array of classes
        :return: Dict of {name: instance}
        """
        result = {}
        for WidgetKls in installed_widgets:
            result[WidgetKls.__name__] = WidgetKls()
        return result

    @property
    def app(self):
        if getattr(self, "_app", None) is None:
            self._app = Flask(__name__)

            # Register our own routes
            self.register_routes(self._app)

        return self._app

    def register_routes(self, app):

        @app.route("/diagnostic/status/heartbeat", methods=['GET'])
        def heartbeat():
            return ""

        @app.route("/diagnostic/status/nagios", methods=['GET'])
        def nagios():
            return "OK"

        @app.route("/static/widget/<name>", methods=["GET"])
        def widget_bundle(name):
            if name not in self.installed_widgets:
                raise abort(404)

            return send_file(self.installed_widgets[name].get_bundle())

        @app.route('/data.json', methods=['GET'])
        def get_data():
            return flask.jsonify(self.datastore.get_all())

        @app.route("/", methods=['GET'])
        def index():
            props = {
                'dashboards': [
                    {"description": dashboard.description, "slug": slug}
                    for slug, dashboard in self.dashboards.iteritems()
                ],
            }

            return render_template('index.html', props=props, title="Welcome")

        @app.route("/<name>", methods=["GET"])
        def dashboard(name):
            if name not in self.dashboards:
                raise abort(404)

            dashboard = self.dashboards[name]

            props = {
                'widgets': dashboard['widgets'],
                'data': self.datastore.get_all()
            }

            widgets = set([
                widget.type for widget in dashboard['widgets']
            ])

            return render_template('dashboard.html', props=props, title=dashboard['description'], widgets=widgets)
