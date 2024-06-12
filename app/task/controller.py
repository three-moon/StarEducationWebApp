from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required

from app.core.decorators import role_required
from app.core.validators import can_access
from app.user.model import Teacher
from app.task import bp
from app.task.service import *


@bp.route("/create/<string:key>", methods=["GET", "POST"])
@role_required(Teacher)
def create(key: str):
    from app.group.service import read_group
    group = read_group(key)
    can_access(group)
    form = TaskForm("Создать")
    if form.validate_on_submit():
        task = create_task(form, group)
        if task:
            flash("Задание успешно создано", "success")
            return redirect(url_for("group.read", key=key))
    return render_template('task/create.html', title="Создать задание", form=form, group=group)


@bp.route('/<int:task_id>', methods=['GET'])
@login_required
def read(task_id: int):
    task = read_task(task_id)
    can_access(task)
    if current_user.is_student:
        return render_template("task/read_s.html", title=task.name, task=task, answer=task.answer)
    elif current_user.is_teacher:
        is_completed = bool(request.args.get("is_completed"))
        from app.answer.service import read_all_answers
        return render_template("task/read_t.html", title=task.name, task=task,
                               answers=read_all_answers(task, is_completed), is_completed=is_completed)


@bp.route("/<int:task_id>/update", methods=["GET", "POST"])
@role_required(Teacher)
def update(task_id: int):
    task = read_task(task_id)
    can_access(task)
    form = TaskForm("Сохранить")
    if form.validate_on_submit():
        task = update_task(task, form)
        if task:
            flash("Задание успешно изменено", "success")
            return redirect(url_for("task.read", task_id=task.id))
    else:
        populate_task_form(task, form)
    return render_template('task/update.html', title="Редактировать задание", form=form, task=task)


@bp.route("/<int:task_id>/delete", methods=["GET"])
@role_required(Teacher)
def delete(task_id: int):
    task = read_task(task_id)
    can_access(task)
    key = task.group.key
    if delete_task(task):
        flash("Задание успешно удалено", "dark")
    return redirect(url_for("group.read", key=key))
