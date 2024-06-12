from flask import render_template, flash, redirect, url_for

from app.answer import bp
from app.answer.service import *
from app.core.decorators import role_required
from app.core.exceptions import TaskDueException
from app.core.validators import can_access
from app.user.model import Teacher, Student


@bp.route("/create/<int:task_id>", methods=["GET", "POST"])
@role_required(Student)
def create(task_id: int):
    from app.task.service import read_task
    task = read_task(task_id)
    can_access(task)
    form = AnswerForm("Создать")
    if form.validate_on_submit():
        answer = create_answer(form, task)
        if answer:
            flash("Ответ успешно принят", "success")
            return redirect(url_for("task.read", task_id=task_id))
    return render_template('answer/create.html', title="Ответить на задание", form=form, task=task)


@bp.route('/<int:answer_id>', methods=['GET'])
@role_required(Teacher)
def read(answer_id: int):
    answer = read_answer(answer_id)
    can_access(answer)
    return render_template("answer/read.html", answer=answer)


@bp.route("/<int:answer_id>/update", methods=["GET", "POST"])
@role_required(Student)
def update(answer_id: int):
    answer = read_answer(answer_id)
    can_access(answer)
    form = AnswerForm("Сохранить")
    if form.validate_on_submit():
        try:
            answer = update_answer(answer, form)
            if answer:
                flash("Ответ успешно изменен", "success")
                return redirect(url_for("task.read", task_id=answer.task.id))
        except TaskDueException:
            flash("Срок выполнения задания истек. Изменить ответ нельзя", "warning")
            return redirect(url_for("task.read", task_id=answer.task.id))
    else:
        populate_answer_form(answer, form)
    return render_template('answer/update.html', title="Редактировать задание", form=form, answer=answer)


@bp.route("/<int:answer_id>/delete", methods=["GET"])
@role_required(Student)
def delete(answer_id: int):
    answer = read_answer(answer_id)
    can_access(answer)
    task_id = answer.task.id
    try:
        if delete_answer(answer):
            flash("Ответ успешно удален", "dark")
    except TaskDueException:
        flash("Срок выполнения задания истек. Изменить ответ нельзя", "warning")
        return redirect(url_for("task.read", task_id=answer.task.id))
    return redirect(url_for("task.read", task_id=task_id))


@bp.route("/<int:answer_id>/assess", methods=["GET", "POST"])
@role_required(Teacher)
def assess(answer_id: int):
    answer = read_answer(answer_id)
    can_access(answer)
    form = AssessForm("Отправить")
    if form.validate_on_submit():
        try:
            answer = assess_answer(answer, form)
            if answer:
                flash("Ответ успешно оценен", "success")
                return redirect(url_for("answer.read", answer_id=answer.id))
        except TaskDueException:
            flash("Срок выполнения задания не истек. Оценить ответ нельзя", "warning")
            return redirect(url_for("task.read", task_id=answer.task.id))
    else:
        populate_assess_form(answer, form)
    return render_template('answer/assess.html', title="Оценить ответ", form=form, answer=answer)
