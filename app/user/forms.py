from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.validators import EqualTo, DataRequired, ValidationError
from app.core.forms import StrippedPasswordField, StrippedStringField
from app.constants import FIELD_REQUIRED_MESSAGE

message = FIELD_REQUIRED_MESSAGE


class LoginForm(FlaskForm):
    login = StrippedStringField("Логин", validators=[DataRequired(message)])
    password = StrippedPasswordField("Пароль", validators=[DataRequired(message)])
    submit = SubmitField("Войти")


class RegistrationForm(FlaskForm):
    login = StrippedStringField("Логин", validators=[DataRequired(message)])
    surname = StrippedStringField("Фамилия", validators=[DataRequired(message)])
    name = StrippedStringField("Имя", validators=[DataRequired(message)])
    patronymic = StrippedStringField("Отчество (при наличии)")
    password = StrippedPasswordField("Пароль", validators=[DataRequired(message)])
    password2 = StrippedPasswordField("Повторите пароль",
                                      validators=[DataRequired(message), EqualTo("password", "Пароли не совпадают")])
    submit = SubmitField("Зарегистрироваться")

    def validate_login(self, login):
        excluded_chars = " *?!'^+%&/()=}][{$#"
        for char in self.login.data:
            if char in excluded_chars:
                raise ValidationError(
                    f"Символ {char} запрещено использовать в логине")


class UpdateForm(FlaskForm):
    login = StrippedStringField("Логин", validators=[DataRequired(message)])
    surname = StrippedStringField("Фамилия", validators=[DataRequired(message)])
    name = StrippedStringField("Имя", validators=[DataRequired(message)])
    patronymic = StrippedStringField("Отчество (при наличии)")
    submit = SubmitField("Сохранить")

    def validate_login(self, login):
        excluded_chars = " *?!'^+%&/()=}][{$#"
        for char in self.login.data:
            if char in excluded_chars:
                raise ValidationError(
                    f"Символ {char} запрещено использовать в логине")


class PasswordForm(FlaskForm):
    password = StrippedPasswordField("Пароль", validators=[DataRequired(message)])
    password2 = StrippedPasswordField("Повторите пароль",
                                      validators=[DataRequired(message), EqualTo("password", "Пароли не совпадают")])
    submit = SubmitField("Сохранить")
