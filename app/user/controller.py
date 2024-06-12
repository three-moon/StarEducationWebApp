from flask import render_template, redirect, url_for, abort, flash
from flask_login import current_user, login_required

from app.user import bp
from app.user.service import *
from app.constants import BASE_URL


@bp.route("/<string:role>/login", methods=["GET", "POST"])
def login(role: str):
    if current_user.is_authenticated:
        return redirect(url_for(BASE_URL))
    if role == "s":
        template = "user/login_s.html"
    elif role == "t":
        template = "user/login_t.html"
    else:
        return abort(404)
    form = LoginForm()
    if form.validate_on_submit():
        if login_user_role_username_password(role, form):
            return redirect(url_for(BASE_URL))
    return render_template(template, title="Войти", form=form)


@bp.route("/<string:role>/register", methods=["GET", "POST"])
def register(role: str):
    if role == "s":
        template = "user/register_s.html"
    elif role == "t":
        template = "user/register_t.html"
    else:
        return abort(404)
    form = RegistrationForm()
    if form.validate_on_submit():
        if create_user(role, form):
            flash("Пользователь успешно зарегистрирован", "success")
            return redirect(url_for(BASE_URL))
    return render_template(template, title="Регистрация", form=form)


@bp.route("/select_login", methods=["GET"])
def select_login():
    return render_template("user/select.html", next="user.login", title="Вход")


@bp.route("/select_register", methods=["GET"])
def select_register():
    return render_template("user/select.html", next="user.register", title="Регистрация")


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for(BASE_URL))


@bp.route("/settings", methods=["GET"])
@login_required
def settings():
    return render_template("user/settings.html")


@bp.route("/update", methods=["GET", "POST"])
@login_required
def update():
    form = UpdateForm()
    if form.validate_on_submit():
        if update_user(current_user, form):
            flash("Данные пользователя успешно обновлены", "success")
            return redirect(url_for("user.settings"))
    else:
        populate_update_form(current_user, form)
    return render_template("user/update.html", title="Редактировать пользователя", form=form)


@bp.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    form = PasswordForm()
    if form.validate_on_submit():
        if update_password(current_user, form):
            flash("Пароль успешно обновлен", "success")
            return redirect(url_for("user.settings"))
    return render_template("user/change_password.html", title="Изменить пароль", form=form)


@bp.route("/delete")
@login_required
def delete():
    if delete_user(current_user):
        flash("Пользователь успешно удален", "dark")
    return redirect(url_for(BASE_URL))
