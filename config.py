from typing import Any
import os

from PySide6.QtCore import Qt

# import app
import app_secrets
from sysver import (sysver, _appname)
from menuformname_viewMap import FormNameToURL_Map
from externalWebPageURL_Map import ExternalWebPageURL_Map

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or app_secrets.SECRET_KEY     # not needed for standalone, right?
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session
    PERMANENT_SESSION_LIFETIME = 3600 * 24  # 24 hours      # currently not implemented in standalone, but might be nice to add in the future

    # app specific
    DEV_MODE = app_secrets.sysver_key == 'DEV'
    APP_NAME = _appname
    APP_VERSION = sysver[app_secrets.sysver_key]
    APP_LOGO_URL = getattr(app_secrets, 'app_logo', "F:/calvincTools/calvincTools/assets/cTools.png")
    APP_LOGO:Any = None    # will be set after class creation
    APP_NEWS_FILE = 'F:/calvinc-app-template/assets/files/' + 'appNews.md'
    FORMNAME_TO_URL_MAP = FormNameToURL_Map
    EXTERNAL_WEBPAGE_URL_MAP = ExternalWebPageURL_Map
    STARTUP_URL = getattr(app_secrets, 'startup_URL', '/WICS')  # needed????
    STARTUP_DELEGATE = getattr(app_secrets, 'startup_delegate', 'auth.login')   # needed???
    
    MISC_FILELOC = getattr(app_secrets, 'MISC_FILELOC', os.getcwd())

    COUNTLIST_RECLIMIT = 500

    DEFAULT_DATEFORMAT = '%Y-%m-%d'  # default date format for displaying dates in the app

    # this is a default value for new user password,
    # should be changed in production and moved to app_secrets.py or environment variable for better security
    NEWUSER_DEFAULT_PW = getattr(app_secrets, 'newuser_default_PW', 'TempPassword123!')

    USER_AUTHENTICATION_ENABLED = getattr(app_secrets, 'usr_authentication_enabled', True)  # default to True if not specified in app_secrets
    # debugging - how to load calvincTools templates in subdirectories
    # EXPLAIN_TEMPLATE_LOADING = True
    
    @classmethod
    def init_app_logo(cls):
        from PySide6.QtGui import QPixmap

        pixsize=100
        if os.path.exists(cls.APP_LOGO_URL):
            applogo = QPixmap(cls.APP_LOGO_URL).scaled(pixsize, pixsize, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        else:
            applogo = QPixmap()

        return applogo

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        app_secrets.database_uri
        # f'sqlite:///{app_secrets.cMenu_dbPath}'
        # 'sqlite:///dev_database.db'
    SQLALCHEMY_ENGINE_OPTIONS = getattr(app_secrets, 'SQLALCHEMY_ENGINE_OPTIONS', {})
    # SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        app_secrets.database_uri
        # f'sqlite:///{app_secrets.cMenu_dbPath}'
        # 'sqlite:///prod_database.db'
    SQLALCHEMY_ENGINE_OPTIONS = getattr(app_secrets, 'SQLALCHEMY_ENGINE_OPTIONS', {})

    # Enhanced security for production
    SESSION_COOKIE_SECURE = True  # HTTPS only


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
}

appConfig:Any = None

