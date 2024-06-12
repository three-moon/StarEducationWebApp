from app.extensions import db
from app.core.model import Column, relationship, CRUDMixin


class Answer(CRUDMixin, db.Model):
    __tablename__ = 'answers'
    id = Column(db.Integer, primary_key=True)
    body = Column(db.String, nullable=False)
    comment = Column(db.String)
    timestamp = Column(db.DateTime, nullable=False)
    mark = Column(db.Integer, default=0, nullable=False)
    student_id = Column(db.Integer, db.ForeignKey('students.id'))
    student = relationship('Student', back_populates='answers')
    task_id = Column(db.Integer, db.ForeignKey('tasks.id'))
    task = relationship('Task', back_populates='answers')

    def is_assessed(self):
        return self.mark != 0

    def is_expired(self) -> bool:
        return bool(self.task.due < self.timestamp)

    @property
    def badges(self):
        badges = []
        if self.is_expired():
            badges.append(("Ответ просрочен", "secondary"))
        if self.is_assessed():
            badges.append((self.mark, "primary"))
        else:
            badges.append(("На проверке", "primary"))
        return badges

    @property
    def pretty_timestamp(self) -> str:
        return self.timestamp.strftime("%d.%m.%Y %H:%M")
