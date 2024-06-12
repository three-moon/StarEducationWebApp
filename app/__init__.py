import logging
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

from flask import Flask, render_template, has_request_context, request
from flask.logging import default_handler
from flask_login import current_user

from app import user, general, group, task, answer
from app.extensions import db, migrate, login, bootstrap
from config import config


def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config.get(config_name))

    register_extensions(app)
    register_blueprints(app)
    register_errorhandler(app)

    if not app.debug and not app.testing:
        configure_logger(app)

    return app


def register_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    bootstrap.init_app(app)


def register_blueprints(app):
    app.register_blueprint(user.bp, url_prefix="/user")
    app.register_blueprint(general.bp)
    app.register_blueprint(group.bp, url_prefix="/group")
    app.register_blueprint(task.bp, url_prefix="/task")
    app.register_blueprint(answer.bp, url_prefix="/answer")


def register_errorhandler(app):
    def render_error(error):
        error_code = getattr(error, "code", 500)
        return render_template("errors/%s.html" % error_code), error_code

    for errcode in [400, 403, 404, 405, 500]:
        app.errorhandler(errcode)(render_error)


class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.header = 'Пользователь "%s" c %s на %s' % (
                current_user,
                request.remote_addr,
                request.url,
            )
            record.request_args = request.args.to_dict()
            record.request_form = request.form.to_dict()
            record.request_form.pop('password', None)
        else:
            record.header = ""
            record.request_args = None
            record.request_form = None

        return super().format(record)


def configure_logger(app):
    formatter = RequestFormatter(
        "[%(asctime)s] %(header)s\n" "%(levelname)s: %(message)s\n"
    )
    error_formatter = RequestFormatter(
        "[%(asctime)s] %(header)s\n"
        "with %(request_args)s; %(request_form)s\n"
        "%(levelname)s in %(module)s: %(message)s"
    )
    default_handler.setFormatter(formatter)
    if not os.path.exists("logs"):
        os.mkdir("logs")
    file_handler = TimedRotatingFileHandler(
        "logs/edu.log", when="midnight", interval=1
    )
    file_handler.suffix = "%Y%m%d"
    file_handler.setFormatter(formatter)
    error_handler = RotatingFileHandler(
        "logs/error_edu.log", maxBytes=10240, backupCount=100
    )
    error_handler.setFormatter(error_formatter)
    file_handler.setLevel(logging.INFO)
    error_handler.setLevel(logging.WARNING)
    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info("EduPlatform startup")
