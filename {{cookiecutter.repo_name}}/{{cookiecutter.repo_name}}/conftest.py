# -*- coding: utf-8 -*-

import six

import os
import os.path
import socket
import shutil
import sys
import time

import pytest

from six.moves import socketserver
from six.moves import SimpleHTTPServer
from six.moves.urllib.request import urlopen
from six.moves.urllib.parse import urljoin

from multiprocessing import Process
from mongoengine import signals

from {{cookiecutter.repo_name}} import create_app, db as database


# XXX: when object is created, call ensure_indexes,
# then indexes is set on recreated database.
def ensure_indexes(sender, document, **kwargs):
    document.ensure_indexes()

signals.pre_init.connect(ensure_indexes)


class Db(object):
    def __init__(self, application):
        self.application = application

    def clean(self):
        # XXX: sice smaze vsechny data, ale pri tvorbe nove dtb uz nevytvori spravne indexy
        # smazeme vsechny vytvorene kolekce
        dtb = database.connection[self.application.config['MONGODB_SETTINGS']['DB']]
        if (self.application.config['MONGODB_SETTINGS']['USERNAME'] and
                self.application.config['MONGODB_SETTINGS']['PASSWORD']):
            dtb.authenticate(
                self.application.config['MONGODB_SETTINGS']['USERNAME'],
                self.application.config['MONGODB_SETTINGS']['PASSWORD']
            )

        for name in dtb.collection_names():
            if not name.startswith('system'):
                dtb.drop_collection(name)


class SimpleBrowser(object):
    def __init__(self, client):
        self.client = client
        self.response = None

    def get(self, *args, **kwargs):
        self.response = self.client.get(*args, **kwargs)

    def post(self, *args, **kwargs):
        self.response = self.client.post(*args, **kwargs)

    def put(self, *args, **kwargs):
        self.response = self.client.put(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.response = self.client.delete(*args, **kwargs)

    def head(self, *args, **kwargs):
        self.response = self.client.head(*args, **kwargs)

    def options(self, *args, **kwargs):
        self.response = self.client.options(*args, **kwargs)

    def trace(self, *args, **kwargs):
        self.response = self.client.trace(*args, **kwargs)

    def patch(self, *args, **kwargs):
        self.response = self.client.patch(*args, **kwargs)


@pytest.fixture
def app(request):
    app = create_app('Testing')

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)

    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def simple_browser(client):
    simple_browser = SimpleBrowser(client)
    return simple_browser


@pytest.fixture
def db(request, app):
    db = Db(application=app)

    request.addfinalizer(db.clean)

    return db


class Server(object):

    def __init__(self, application):
        self.application = application
        self.schema = 'http'
        self.host = 'localhost'
        self.port = self._get_free_port()

        self.start()

    def _run(self, host, port):
        # close all outputs
        sys.stdout.close()
        sys.stdout = open(os.devnull)
        sys.stderr.close()
        sys.stderr = sys.stdout

        self.application.run(host=host, port=port)

    def _get_free_port(self, base_port=5555):
        for i in range(50000):
            port = base_port + i
            try:
                test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                test_socket.bind((self.host, port))
                test_socket.close()
                break
            except IOError:
                pass

        return port

    def is_alive(self, max_retries=5):
        '''
        Return True if server in child process respond.
        max_retries -- number of tries
        '''
        for i in range(max_retries):
            try:
                urlopen(self.url)
                return True
            except IOError:
                time.sleep(2 ** i)

        return False

    def start(self):
        self.p = Process(target=self._run,
                         kwargs={'host': self.host, 'port': self.port})

        self.p.start()

        if not self.is_alive():
            # TODO: raise exception or log some message
            self.stop()

    def stop(self):
        self.p.terminate()
        self.p.join()

    def restart(self):
        self.stop()
        self.start()

    @property
    def url(self):
        return '%s://%s:%d' % (self.schema, self.host, self.port)

    if sys.version_info < (3, 0):
        def __unicode__(self):
            return self.url

        def __add__(self, other):
            return urljoin(unicode(self), other)
    else:
        def __str__(self):
            return self.url

        def __add__(self, other):
            return urljoin(str(self), other)

    def __repr__(self):
        return '<LiveServer listening at %s>' % self.url


@pytest.fixture(scope='session')
def live_server(request, app, db):
    server = Server(application=app)

    request.addfinalizer(server.stop)

    return server
