from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.core.model import Column, relationship, CRUDMixin
from app.extensions import db, login


class User(UserMixin, CRUDMixin, db.Model):
    __tablename__ = 'users'
    id = Column(db.Integer, primary_key=True)
    login = Column(db.String)
    surname = Column(db.String)
    name = Column(db.String)
    patronymic = Column(db.String)
    password_hash: str = Column(db.String(128))
    teacher = relationship('Teacher', backref='user_as_teacher', uselist=False)
    student = relationship('Student', backref='user_as_student', uselist=False)

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        self.save()

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def can_access_group(self, group):
        if self.is_teacher:
            return group in self.teacher.groups
        elif self.is_student:
            return group in self.student.groups
        else:
            raise TypeError

    def can_access_task(self, task):
        return self.can_access_group(task.group)

    def can_access_answer(self, answer):
        if self.is_teacher:
            return self.can_access_task(answer.task)
        elif self.is_student:
            return self.student == answer.student
        else:
            raise TypeError

    @property
    def is_student(self):
        return self.student

    @property
    def is_teacher(self):
        return self.teacher

    @property
    def initials(self):
        if self.patronymic:
            return self.surname + " " + self.name[0] + "." + self.patronymic[0] + "."
        else:
            return self.surname + " " + self.name[0] + "."

    @property
    def full_name(self):
        if self.patronymic:
            return str(self.surname) + " " + str(self.name) + " " + str(self.patronymic)
        else:
            return str(self.surname) + " " + str(self.name)

    def get_role_repr(self):
        if self.is_student:
            return 'Студент'
        elif self.is_teacher:
            return 'Преподаватель'
        else:
            return 'Undefined'

    def __repr__(self):
        return "%s [%s]" % (self.full_name, self.get_role_repr())


class Student(CRUDMixin, db.Model):
    __tablename__ = 'students'
    id = Column(db.Integer, primary_key=True)
    user_id = Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    user = relationship("User")
    groups = relationship("Group", secondary="students_groups", back_populates="students")
    answers = relationship("Answer", back_populates="student")

    def __repr__(self):
        return str(self.user)


class Teacher(CRUDMixin, db.Model):
    __tablename__ = 'teachers'
    id = Column(db.Integer, primary_key=True)
    user_id = Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    user = relationship("User")
    groups = relationship("Group", back_populates="teacher")

    def __repr__(self):
        return str(self.user)


class AnonymousUser(AnonymousUserMixin):
    @property
    def is_student(self):
        return False

    @property
    def is_teacher(self):
        return False


login.anonymous_user = AnonymousUser


@login.user_loader
def load_user(id_) -> User:
    return User.query.get(int(id_))
