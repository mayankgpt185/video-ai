import json
from flask import Flask
from flask_bcrypt import Bcrypt

from .config import config_by_name
from flask.app import Flask
from flask_mongoengine import MongoEngine
from flask.json.provider import JSONProvider
from flask.json.provider import JSONProvider
import json
from mongoengine import *


flask_bcrypt = Bcrypt()
mongoDb = MongoEngine()

def create_app(config_name: str) -> Flask:
    app = Flask(__name__)
    setAppConfig(config_name, app)
    mongoDb.init_app(app)
    flask_bcrypt.init_app(app)
    return app

def setAppConfig(config_name, app):
    env_file = f"env-{config_name}.json"
    app.config.from_file(env_file, load=json.load)


def setup_mongoDB(app) -> any:
    return app
