from typing import Optional, List

from flask_login import current_user
from werkzeug.exceptions import NotFound

from app.group.model import Group
from app.task.model import Task
from app.task.forms import TaskForm


def create_task(form: TaskForm, group: Group) -> Optional[Task]:
    task = Task.create(name=form.name.data, due=form.due.data, description=form.description.data, group=group)
    return task


def read_task(task_id: int) -> Task:
    task = Task.query.get_or_404(task_id)
    return task


def read_all_tasks(group: Group, is_completed: bool = False) -> List[Task]:
    if not is_completed:
        tasks = sorted([task for task in group.tasks if not task.is_expired()], key=lambda task: task.due)
        if current_user.is_student:
            return [task for task in tasks if task.answer is None]
        elif current_user.is_teacher:
            return tasks
    else:
        tasks = sorted(group.tasks, key=lambda task: task.due, reverse=True)
        if current_user.is_student:
            return [task for task in tasks if task.answer is not None or task.is_expired()]
        elif current_user.is_teacher:
            return [task for task in tasks if task.is_expired()]


def update_task(task: Task, form: TaskForm) -> Optional[Task]:
    task.update(name=form.name.data, due=form.due.data, description=form.description.data)
    return task


def delete_task(task: Task, force=False) -> bool:
    for answer in task.answers:
        from app.answer.service import delete_answer
        delete_answer(answer, force)
    task.delete()
    return True


def populate_task_form(task: Task, form: TaskForm) -> None:
    form.name.data = task.name
    form.description.data = task.description
    form.due.data = task.due
