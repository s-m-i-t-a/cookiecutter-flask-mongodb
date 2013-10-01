# -*- coding: utf-8 -*-

from config.settings.base import *


DEBUG = True

MONGODB_SETTINGS = get_dtb_config("mongodb://localhost/{{cookiecutter.repo_name}}")
