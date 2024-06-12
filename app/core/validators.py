from typing import Any

from flask_login import current_user
from werkzeug.exceptions import NotFound


def can_access(obj: Any):
    from app.answer.model import Answer
    from app.group.model import Group
    from app.task.model import Task
    if isinstance(obj, Group):
        if current_user.can_access_group(obj):
            return
    elif isinstance(obj, Task):
        if current_user.can_access_task(obj):
            return
    elif isinstance(obj, Answer):
        if current_user.can_access_answer(obj):
            return
    else:
        raise TypeError
    raise NotFound
