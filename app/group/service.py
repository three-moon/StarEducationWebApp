import uuid
from typing import Optional, List

from flask_login import current_user

from app.group.forms import GroupForm, JoinGroupForm
from app.group.model import Group


def create_group(form: GroupForm) -> Optional[Group]:
    generated_key = uuid.uuid4().hex[:8]
    while Group.query.filter_by(key=generated_key).first():
        generated_key = uuid.uuid4().hex[:8]
    group = Group.create(name=form.name.data, teacher=current_user.teacher, key=generated_key)
    return group


def read_group(key: str) -> Group:
    group = Group.query.filter_by(key=key).first_or_404()
    return group


def read_all_groups() -> List[Group]:
    if current_user.is_student:
        groups = current_user.student.groups
    elif current_user.is_teacher:
        groups = current_user.teacher.groups
    else:
        raise AttributeError
    return sorted(groups, key=lambda group: group.name)


def update_group(group: Group, form: GroupForm) -> Optional[Group]:
    group.update(name=form.name.data)
    return group


def delete_group(group: Group, force=False) -> bool:
    for task in group.tasks:
        from app.task.service import delete_task
        delete_task(task, force)
    group.delete()
    return True


def join_group(form: JoinGroupForm) -> Optional[Group]:
    group = Group.query.filter_by(key=form.key.data).first()
    if not group:
        form.key.errors = ('Не существует группы с таким ключом', '')
        return None
    student = current_user.student
    if student in group.students:
        form.key.errors = ('Вы уже состоите в этой группе', '')
        return None
    group.add_student(student)
    return group


def leave_group(group: Group) -> bool:
    group.remove_student(current_user.student)
    return True


def exclude_from_group(group: Group, student) -> bool:
    group.remove_student(student)
    return True


def populate_group_form(group: Group, form: GroupForm) -> None:
    form.name.data = group.name
