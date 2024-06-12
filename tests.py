import unittest

from app import create_app, db
from app.answer.service import *
from app.user.service import *
from app.group.service import *
from app.task.service import *


class TestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite+pysqlite:///:memory:"
        self.app.config['LOGGING'] = False
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        with self.app.test_request_context():
            form = RegistrationForm()
            form.login.data = "teacher"
            form.password.data = "password"
            form.password2.data = "password"
            form.name.data = "name"
            form.surname.data = "surname"
            form.patronymic.data = "patronymic"
            create_user("t", form)
            self.teacher_user = read_user("teacher")

            form.login.data = "student"
            create_user("s", form)
            self.student_user = read_user("student")

            login_user(self.teacher_user)
            form = GroupForm("")
            form.name.data = "group"
            self.group = create_group(form)

            login_user(self.student_user)
            form = JoinGroupForm()
            form.key.data = self.group.key
            join_group(form)

            login_user(self.teacher_user)
            form = TaskForm("")
            form.name.data = "task"
            form.description.data = "task_description"
            form.due.data = datetime.now().replace(datetime.now().year + 1)
            self.task = create_task(form, self.group)

    def tearDown(self):
        db.drop_all()
        self.app_context.pop()
        self.app = None
        self.app_context = None

    def test_app(self):
        assert self.app is not None
        assert current_app == self.app

    def test_password_hashing(self):
        u = User.create(name="Name")
        u.password = 'cat'
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_user(self):
        with self.app.test_request_context():
            form = RegistrationForm()
            form.login.data = "login"
            form.password.data = "password"
            form.password2.data = "password"
            form.name.data = "name"
            form.surname.data = "surname"
            form.patronymic.data = "patronymic"

            # Успешная регистрация
            self.assertTrue(create_user("s", form))
            self.assertFalse(form.errors)
            self.assertTrue(read_user("login"))

            # Логин уже занят
            self.assertFalse(create_user("t", form))
            self.assertTrue(form.errors)

            # Обновление данных пользователя
            form = UpdateForm()
            form.login.data = "login1"
            form.name.data = "name1"
            form.surname.data = "surname1"
            form.patronymic.data = "patronymic1"
            self.assertTrue(update_user(current_user, form))
            self.assertFalse(form.errors)

            # Обновление пароля
            form = PasswordForm()
            form.password.data = "password1"
            form.password2.data = "password1"
            self.assertTrue(update_password(current_user, form))
            self.assertFalse(form.errors)

            # Удаление пользователя
            self.assertTrue(delete_user(current_user))

    def test_group(self):
        with self.app.test_request_context():
            login_user(self.teacher_user)

            # Создание группы
            form = GroupForm("")
            form.name.data = "test_group"
            group = create_group(form)
            self.assertIsInstance(group, Group)

            # Получение группы по ключу
            self.assertIsInstance(read_group(group.key), Group)
            with self.assertRaises(NotFound):
                read_group("key")

            # Получение всех групп для преподавателя
            self.assertTrue(len(read_all_groups()) == 2)

            # Обновление данных группы
            form.name.data = "test_group1"
            update_group(group, form)
            self.assertTrue(group.name == "test_group1")

            login_user(self.student_user)

            # Присоединение к несуществующей группе
            form = JoinGroupForm()
            form.key.data = "key"
            self.assertIsNone(join_group(form))
            self.assertTrue(form.errors)

            # Присоединение к существующей группе
            form = JoinGroupForm()
            form.key.data = group.key
            self.assertIsInstance(join_group(form), Group)
            self.assertFalse(form.errors)

            # Повторное присоединение к группе
            self.assertIsNone(join_group(form))
            self.assertTrue(form.errors)

            # Получение всех групп для студента
            self.assertTrue(len(read_all_groups()) == 2)

            # Выход из группы
            self.assertTrue(leave_group(group))

            login_user(self.teacher_user)

            # Удаление группы
            self.assertTrue(delete_group(group))

    def test_task(self):
        with self.app.test_request_context():
            login_user(self.teacher_user)

            # Создание задания
            form = TaskForm("")
            form.name.data = "test_task"
            form.description.data = "test_task_description"
            form.due.data = datetime.now().replace(datetime.now().year + 1)
            task = create_task(form, self.group)
            self.assertIsInstance(task, Task)

            # Получение задания
            self.assertIsInstance(read_task(task.id), Task)
            with self.assertRaises(NotFound):
                read_task(1000)

            # Получение всех заданий для преподавателя
            self.assertTrue(len(read_all_tasks(self.group)) == 2)

            # Обновление данных задания
            form.name.data = "test_task1"
            form.description.data = "test_task_description1"
            form.due.data = task.due.replace(task.due.year + 1)
            update_task(task, form)
            self.assertTrue(task.name == form.name.data)
            self.assertTrue(task.description == form.description.data)
            self.assertTrue(task.due == form.due.data)

            login_user(self.student_user)

            # Получение всех заданий для студента
            self.assertTrue(len(read_all_tasks(self.group)) == 2)

            login_user(self.teacher_user)

            # Удаление задания
            self.assertTrue(delete_task(task))

    def test_answer(self):
        with self.app.test_request_context():
            login_user(self.student_user)

            # Создание ответа
            form = AnswerForm("")
            form.body.data = "test_answer_body"
            answer = create_answer(form, self.task)
            self.assertIsInstance(answer, Answer)

            # Получение ответа
            self.assertIsInstance(read_answer(answer.id), Answer)
            with self.assertRaises(NotFound):
                read_answer(1000)

            # Изменение ответа до окончания срока выполнения
            form.body.data = "test_answer_body1"
            update_answer(answer, form)
            self.assertTrue(answer.body == form.body.data)

            login_user(self.teacher_user)

            # Получение всех ответов для преподавателя
            self.assertTrue(len(read_all_answers(self.task)) == 1)

            # Оценка ответа
            form = AssessForm("")
            form.comment.data = "test_answer_comment"
            form.mark.data = 5

            # Оценка ответа до окончания срока выполнения
            with self.assertRaises(TaskDueException):
                assess_answer(answer, form)

            self.task.update(due=datetime.now().replace(datetime.now().year - 1))

            # Оценка ответа после окончания срока выполнения
            assess_answer(answer, form)
            self.assertTrue(answer.comment == form.comment.data)
            self.assertTrue(answer.mark == form.mark.data)

            login_user(self.student_user)

            # Изменение ответа после окончания срока выполнения
            form = AnswerForm("")
            form.body.data = "test_answer_body1"
            with self.assertRaises(TaskDueException):
                update_answer(answer, form)

            # Удаление ответа после окончания срока выполнения
            with self.assertRaises(TaskDueException):
                delete_answer(answer)

            self.task.update(due=datetime.now().replace(datetime.now().year + 1))

            # Удаление ответа до окончания срока выполнения
            self.assertTrue(delete_answer(answer))


if __name__ == '__main__':
    unittest.main(verbosity=2)
