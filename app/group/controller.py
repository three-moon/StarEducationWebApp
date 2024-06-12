from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required

from app.constants import BASE_URL
from app.core.decorators import role_required
from app.core.validators import can_access
from app.group import bp
from app.group.service import *
from app.user.model import Teacher, Student


@bp.route("/create", methods=["GET", "POST"])
@role_required(Teacher)
def create():
    form = GroupForm("Создать")
    if form.validate_on_submit():
        group = create_group(form)
        if group:
            flash('Группа "%s" создана' % group.name, "success")
            return redirect(url_for("group.read", key=group.key))
    return render_template("group/create.html", title="Создать группу", form=form)


@bp.route("/<string:key>", methods=["GET"])
@login_required
def read(key: str):
    group = read_group(key)
    can_access(group)
    is_completed = bool(request.args.get("is_completed"))
    from app.task.service import read_all_tasks
    return render_template("group/read.html", title=group.name, group=group,
                           tasks=read_all_tasks(group, is_completed), is_completed=is_completed)


@bp.route("/all", methods=["GET"])
@login_required
def all():
    return render_template("group/all.html", title="Ваши группы", groups=read_all_groups())


@bp.route("/<string:key>/update", methods=["GET", "POST"])
@role_required(Teacher)
def update(key: str):
    group = read_group(key)
    can_access(group)
    form = GroupForm("Сохранить")
    if form.validate_on_submit():
        group = update_group(group, form)
        if group:
            flash('Группа "%s" изменена' % group.name, "success")
            return redirect(url_for("group.read", key=group.key))
    else:
        populate_group_form(group, form)
    return render_template("group/update.html", title="Редактировать группу", form=form, group=group)


@bp.route("/<string:key>/delete", methods=["GET"])
@role_required(Teacher)
def delete(key: str):
    group = read_group(key)
    can_access(group)
    name = group.name
    if delete_group(group):
        flash('Группа "%s" удалена' % name, "dark")
    return redirect(url_for(BASE_URL))


@bp.route("/join", methods=["GET", "POST"])
@role_required(Student)
def join():
    form = JoinGroupForm()
    if form.validate_on_submit():
        group = join_group(form)
        if group:
            flash("Вы успешно присоединились к группе '%s'" % group.name, "success")
            return redirect(url_for(BASE_URL))
    return render_template("group/join.html", title="Присоединиться к группе", form=form)


@bp.route("/<string:key>/leave", methods=["GET"])
@role_required(Student)
def leave(key: str):
    group = read_group(key)
    can_access(group)
    if leave_group(group):
        flash("Вы покинули группу '%s'" % group.name, "dark")
    return redirect(url_for(BASE_URL))


@bp.route("/<string:key>/exclude/<int:student_id>", methods=["GET"])
@role_required(Teacher)
def exclude(key: str, student_id: int):
    group = read_group(key)
    can_access(group)
    from app.user.service import read_student
    student = read_student(student_id)
    if exclude_from_group(group, student):
        flash("Студент %s удален из группы" % student.user.initials, "dark")
    return redirect(url_for("group.students", key=key))


@bp.route("/<string:key>/students", methods=["GET"])
@role_required(Teacher)
def students(key: str):
    group = read_group(key)
    can_access(group)
    return render_template("group/students.html", title="Список группы", group=group)
