from flask import flash, url_for, redirect
from flask_login import current_user
from functools import wraps

from app.constants import BASE_URL
from app.user.model import Student, Teacher


def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if (
                    role == Student and not current_user.is_student or
                    role == Teacher and not current_user.is_teacher
            ):
                flash(
                    "Вы не можете совершить данное действие",
                    "warning",
                )
                return redirect(url_for(BASE_URL))
            return f(*args, **kwargs)

        return decorated_function

    return decorator
