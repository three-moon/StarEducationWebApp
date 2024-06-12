from datetime import datetime
from typing import Optional, List

from flask_login import current_user
from werkzeug.exceptions import NotFound

from app.answer.forms import AnswerForm, AssessForm
from app.core.exceptions import TaskDueException
from app.answer.model import Answer
from app.task.model import Task
from app.user.model import Student


def create_answer(form: AnswerForm, task: Task) -> Optional[Answer]:
    if task.answer:
        form.body.errors = ("Вы уже ответили на задание", "")
        return None
    answer = Answer.create(body=form.body.data, timestamp=datetime.now(), task=task, student=current_user.student)
    return answer


def read_answer(answer_id: int) -> Answer:
    answer = Answer.query.get_or_404(answer_id)
    return answer


def read_all_answers(task: Task, is_completed: bool = False) -> List[Answer]:
    if not is_completed:
        answers = sorted([a for a in task.answers if not a.is_assessed()], key=lambda a: a.timestamp)
        return answers
    else:
        answers = sorted([a for a in task.answers if a.is_assessed()], key=lambda a: a.timestamp)
        return answers


def update_answer(answer: Answer, form: AnswerForm) -> Optional[Answer]:
    if answer.task.is_expired():
        raise TaskDueException
    answer.update(body=form.body.data, timestamp=datetime.now())
    return answer


def delete_answer(answer: Answer, force=False) -> bool:
    if not force and answer.task.is_expired():
        raise TaskDueException
    answer.delete()
    return True


def assess_answer(answer: Answer, form: AssessForm) -> Optional[Answer]:
    if not answer.task.is_expired():
        raise TaskDueException
    answer.update(comment=form.comment.data, mark=form.mark.data)
    return answer


def populate_answer_form(answer: Answer, form: AnswerForm) -> None:
    form.body.data = answer.body


def populate_assess_form(answer: Answer, form: AssessForm) -> None:
    form.comment.data = answer.comment
    form.mark.data = answer.mark
