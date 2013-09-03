# -*- coding: utf-8 -*-
'''
Settings for {{cookiecutter.project_name}} project.

'''

import os

from unipath import Path

BASE_DIR = Path(__file__).ancestor(2)


DEBUG = False

TESTING = False


MONGODB_SETTINGS = {
    'DB': '',
    'USERNAME': '',
    'PASSWORD': '',
    'HOST': '',
    'PORT': '',
}
