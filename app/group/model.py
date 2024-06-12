from flask_login import current_user

from app.core.model import Column, relationship, CRUDMixin
from app.extensions import db


class Group(CRUDMixin, db.Model):
    __tablename__ = 'groups'
    id = Column(db.Integer, primary_key=True)
    key = Column(db.String(8), unique=True, nullable=False)
    name = Column(db.String, nullable=False)
    description = Column(db.String)
    teacher_id = Column(db.Integer, db.ForeignKey('teachers.id'))
    teacher = relationship("Teacher", back_populates="groups")
    students = relationship("Student", secondary="students_groups", back_populates="groups")
    tasks = relationship("Task", back_populates="group")

    def add_student(self, student):
        self.students.append(student)
        self.save()

    def remove_student(self, student):
        self.students.remove(student)
        self.save()

    @property
    def teacher_initials(self):
        return self.teacher.user.initials

    @property
    def footer(self):
        if current_user.is_student:
            return self.teacher_initials
        elif current_user.is_teacher:
            return self.key


students_groups = db.Table(
    "students_groups",
    db.Model.metadata,
    Column("student_id", db.ForeignKey("students.id"), primary_key=True),
    Column("group_id", db.ForeignKey("groups.id"), primary_key=True)
)
