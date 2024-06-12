from datetime import datetime

from flask_login import current_user

from app.extensions import db
from app.core.model import Column, relationship, CRUDMixin

from app.answer.model import Answer


class Task(CRUDMixin, db.Model):
    __tablename__ = "tasks"
    id = Column(db.Integer, primary_key=True)
    name = Column(db.String, nullable=False)
    description = Column(db.String, nullable=False)
    due = Column(db.DateTime, nullable=False)
    group_id = Column(db.Integer, db.ForeignKey("groups.id"))
    group = relationship("Group", back_populates="tasks")
    answers = relationship("Answer", back_populates="task")

    @property
    def badges(self):
        badges = []
        if current_user.is_teacher:
            if self.has_answers:
                badges.append(("Непроверенные ответы", "primary"))
        if self.is_expired():
            badges.append(("Закрыто", "secondary"))
        return badges

    @property
    def badges_with_answer(self):
        badges = []
        if current_user.is_student:
            if self.answer:
                badges += self.answer.badges
        return badges + self.badges

    @property
    def answer(self):
        if current_user.is_student:
            return Answer.query.filter_by(task=self, student=current_user.student).first()
        else:
            raise AttributeError

    @property
    def has_answers(self):
        if current_user.is_teacher:
            return Answer.query.filter_by(task=self, mark=0).count()
        else:
            raise AttributeError

    def is_expired(self) -> bool:
        return bool(self.due < datetime.now())

    @property
    def pretty_due(self) -> str:
        return self.due.strftime("%d.%m.%Y %H:%M")
