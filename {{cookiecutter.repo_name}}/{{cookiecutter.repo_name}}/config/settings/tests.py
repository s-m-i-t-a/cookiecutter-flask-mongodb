# -*- coding: utf-8 -*-

from config.settings.base import *


TESTING = True

MONGODB_SETTINGS = get_dtb_config("mongodb://localhost/{{cookiecutter.repo_name}}_tests")
