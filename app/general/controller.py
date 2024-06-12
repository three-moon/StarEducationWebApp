from flask import render_template, redirect, url_for
from flask_login import login_required, current_user

from app.constants import BASE_URL
from app.general import bp


@bp.route("/", methods=["GET"])
def index():
    if current_user.is_authenticated:
        return redirect(url_for(BASE_URL))
    return render_template("general/index.html")



