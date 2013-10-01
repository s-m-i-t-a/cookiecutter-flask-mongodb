# -*- coding: utf-8 -*-

import os

from flask import Flask
from flask.ext.mongoengine import MongoEngine

from config.blueprints import register_blueprints


app = Flask(__name__)

app.config.from_object('config.settings.base')

if os.getenv('APP_SETTINGS', None) is not None:
    app.config.from_envvar("APP_SETTINGS")

db = MongoEngine(app)

register_blueprints(app)


if __name__ == '__main__':
    app.run()
