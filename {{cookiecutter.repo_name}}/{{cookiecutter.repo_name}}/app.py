# -*- coding: utf-8 -*-

import os

from flask import Flask
from flask.ext.mongoengine import MongoEngine

from config.blueprints import register_blueprints


configuration = os.getenv('APP_CONFIGURATION', 'Production')
settings = 'config.settings.%s' % configuration


app = Flask(__name__)
app.config.from_object(settings)
db = MongoEngine(app)

register_blueprints(app)


if __name__ == '__main__':
    app.run()
