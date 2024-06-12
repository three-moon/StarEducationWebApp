from flask import Blueprint

bp = Blueprint("answer", __name__)

from app.answer import controller
