from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, TextAreaField


class Stripped(object):
    def process_formdata(self, valuelist):
        if valuelist:
            self.data = valuelist[0].strip()
        else:
            self.data = ''


class StrippedStringField(Stripped, StringField):
    pass


class StrippedPasswordField(Stripped, PasswordField):
    pass


class StrippedTextAreaField(Stripped, TextAreaField):
    pass
