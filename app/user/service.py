from flask import current_app
from flask_login import login_user, logout_user

from app.answer.service import delete_answer
from app.user.forms import RegistrationForm, LoginForm, UpdateForm, PasswordForm
from app.user.model import User, Student, Teacher


def create_user(role: str, form: RegistrationForm) -> bool:
    login = form.login.data
    if User.query.filter_by(login=login.strip()).count():
        current_app.logger.info(
            'Пользователь "%s" не зарегистрирован, данное имя пользователя занято' % login)
        form.login.errors = ("Такой логин уже используется", "Придумайте другой логин")
        return False
    created_user = User.create(login=login, name=form.name.data, surname=form.surname.data,
                               patronymic=form.patronymic.data)
    current_app.logger.info('Зарегистрирован пользователь "%s"' % login)
    created_user.password = form.password.data
    if role == "s":
        Student.create(user=created_user)
        current_app.logger.info('Student over the user was created  "%s"' % login)
    elif role == "t":
        Teacher.create(user=created_user)
        current_app.logger.info('Teacher over the user was created  "%s"' % login)
    else:
        raise AttributeError
    login_user(created_user)
    return True


def read_user(login: str) -> User:
    user = User.query.filter_by(login=login).first_or_404()
    return user


def read_student(student_id: int) -> Student:
    student = Student.query.get_or_404(student_id)
    return student


def update_user(user: User, form: UpdateForm) -> bool:
    login = form.login.data
    if form.login.data != user.login and User.query.filter_by(login=login.strip()).count():
        form.login.errors = ("Такой логин уже используется", "Придумайте другой логин")
        return False
    user.update(login=login, name=form.name.data, surname=form.surname.data,
                patronymic=form.patronymic.data)
    return True


def update_password(user: User, form: PasswordForm) -> bool:
    user.password = form.password.data
    return True


def delete_user(user: User) -> bool:
    if user.is_teacher:
        for group in user.teacher.groups:
            from app.group.service import delete_group
            delete_group(group, force=True)
        user.teacher.delete()
    elif user.is_student:
        for answer in user.student.answers:
            delete_answer(answer, force=True)
        for group in user.student.groups:
            group.remove_student(user.student)
        user.student.delete()
    user.delete()
    logout_user()
    return True


def login_user_role_username_password(role: str, form: LoginForm) -> bool:
    login = form.login.data
    user = User.query.filter_by(login=login.strip()).first()
    if user is None:
        current_app.logger.info('Invalid username "%s"', login)
        form.login.errors = ("Такого логина не существует", "Проверьте правильность ввода")
        return False
    if (role == "s" and not user.is_student or
            role == "t" and not user.is_teacher):
        current_app.logger.info('Invalid user type "%s", expected "%s" on login "%s"',
                                role, user.get_role_repr(), user.login)
        form.login.errors = ("Неправильный тип пользователя для данного логина",
                             "Проверьте правильность выбора типа пользователя")
        return False
    if not user.check_password(form.password.data):
        current_app.logger.info('Invalid password for user "%s"', login)
        form.password.errors = ("Некорректный пароль", "")
        return False
    login_user(user)
    current_app.logger.info('User "%s" logged in', login)
    return True


def populate_update_form(user: User, form: UpdateForm):
    form.login.data = user.login
    form.name.data = user.name
    form.surname.data = user.surname
    form.patronymic.data = user.patronymic
