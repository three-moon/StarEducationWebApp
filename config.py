import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config:
    BASE_URL = "group.all"
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProdConfig(Config):
    FLASK_ENV = "production"
    DEBUG = False
    TESTING = False


class DevConfig(Config):
    FLASK_ENV = "development"
    DEBUG = True
    TESTING = True


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    WTF_CSRF_ENABLED = False



config = {
    "test": TestConfig,
    "dev": DevConfig,
    "prod": ProdConfig,
    "default": ProdConfig,
}
