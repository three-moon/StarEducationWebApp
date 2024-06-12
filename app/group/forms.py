from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.validators import DataRequired

from app.constants import FIELD_REQUIRED_MESSAGE
from app.core.forms import StrippedStringField


class GroupForm(FlaskForm):
    name = StrippedStringField("Название", validators=[DataRequired(FIELD_REQUIRED_MESSAGE)])
    submit = SubmitField()

    def __init__(self, label, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        self.submit.label.text = label


class JoinGroupForm(FlaskForm):
    key = StrippedStringField("Код группы", validators=[DataRequired(FIELD_REQUIRED_MESSAGE)])
    submit = SubmitField("Присоединиться")
