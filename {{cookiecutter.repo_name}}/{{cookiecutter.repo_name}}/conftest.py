# -*- coding: utf-8 -*-

import os
import socket
import sys
import time
import urlparse
import urllib

import pytest

from multiprocessing import Process
from mongoengine import signals

from app import app as application, db as database


# XXX: when object is created, call ensure_indexes,
# then indexes is set on recreated database.
def ensure_indexes(sender, document, **kwargs):
    document.ensure_indexes()

signals.pre_init.connect(ensure_indexes)


class Db(object):
    def clean(self):
        # XXX: sice smaze vsechny data, ale pri tvorbe nove dtb uz nevytvori spravne indexy
        # smazeme vsechny vytvorene kolekce
        dtb = database.connection[application.config['MONGODB_SETTINGS']['DB']]
        if (application.config['MONGODB_SETTINGS']['USER'] and
                application.config['MONGODB_SETTINGS']['PASSWORD']):
            dtb.authenticate(application.config['MONGODB_SETTINGS']['USER'],
                             application.config['MONGODB_SETTINGS']['PASSWORD'])

        for name in dtb.collection_names():
            if not name.startswith('system'):
                dtb.drop_collection(name)


@pytest.fixture
def db(request):
    db = Db()

    request.addfinalizer(db.clean)

    return db


@pytest.fixture
def app():
    return application


@pytest.fixture
def client():
    return application.test_client()


class Server(object):

    def __init__(self):
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

        application.run(host=host, port=port)

    def _get_free_port(self, base_port=5555):
        for i in xrange(50000):
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
                urllib.urlopen(self.url)
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
            return urlparse.urljoin(unicode(self), other)
    else:
        def __str__(self):
            return self.url

        def __add__(self, other):
            return urlparse.urljoin(str(self), other)

    def __repr__(self):
        return '<LiveServer listening at %s>' % self.url


@pytest.fixture(scope='session')
def live_server(request, db):
    server = Server()

    request.addfinalizer(server.stop)

    return server
