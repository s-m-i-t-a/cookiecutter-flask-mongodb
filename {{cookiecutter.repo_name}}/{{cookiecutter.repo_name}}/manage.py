# -*- coding: utf-8 -*-

import os.path
import sys

from flask.ext.script import Manager, Server
from config.wsgi import app


manager = Manager(app)

# Turn on debugger by default and reloader
manager.add_command("runserver",
                    Server(use_debugger=True,
                           use_reloader=True,
                           host='0.0.0.0'))


if __name__ == "__main__":
    manager.run()
