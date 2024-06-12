from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.fields import RadioField
from wtforms.validators import DataRequired

from app.constants import FIELD_REQUIRED_MESSAGE
from app.core.forms import StrippedTextAreaField


class AnswerForm(FlaskForm):
    body = StrippedTextAreaField("Ответ", validators=[DataRequired(FIELD_REQUIRED_MESSAGE)])
    submit = SubmitField()

    def __init__(self, label, *args, **kwargs):
        super(AnswerForm, self).__init__(*args, **kwargs)
        self.submit.label.text = label


class AssessForm(FlaskForm):
    comment = StrippedTextAreaField("Комментарий")
    mark = RadioField("Оценка",
                      choices=[(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5"), (6, "6"), (7, "7"), (8, "8"), (9, "9"),
                               (10, "10")], validators=[DataRequired()])
    submit = SubmitField()

    def __init__(self, label, *args, **kwargs):
        super(AssessForm, self).__init__(*args, **kwargs)
        self.submit.label.text = label
