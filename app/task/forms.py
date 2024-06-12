from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.fields.datetime import DateTimeLocalField
from wtforms.validators import DataRequired, ValidationError

from app.constants import FIELD_REQUIRED_MESSAGE
from app.core.forms import StrippedStringField, StrippedTextAreaField

message = FIELD_REQUIRED_MESSAGE


class TaskForm(FlaskForm):
    name = StrippedStringField("Название", validators=[DataRequired(message)])
    due = DateTimeLocalField("Срок сдачи", validators=[DataRequired(message)])
    description = StrippedTextAreaField("Описание")
    submit = SubmitField()

    def validate_due(self, due):
        if self.due.data < datetime.now():
            raise ValidationError("Дата сдачи должна быть позднее текущего момента")

    def __init__(self, label, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        self.submit.label.text = label
