# -*- coding: utf-8 -*-

import os.path

from .utils import get_dtb_config, getenv


class BaseConfig(object):
    '''
    Base settings for {{cookiecutter.project_name}} project.
    '''

    DEBUG = False

    TESTING = False

    BASE_DIR = os.path.dirname(os.path.dirname(__file__))

    SECRET_KEY = getenv('SECRET_KEY')

    # Databases uri string (e.g. mongodb://localhost/wsys)
    MONGODB_SETTINGS = get_dtb_config(getenv('DATABASE_URL'))


class Production(BaseConfig):
    pass


class Development(BaseConfig):
    '''
    Development settings.
    '''
    DEBUG = True


class Testing(BaseConfig):
    '''
    Testing settings.
    '''

    TESTING = True

    MONGODB_SETTINGS = get_dtb_config("mongodb://localhost/{{cookiecutter.repo_name}}_test")
