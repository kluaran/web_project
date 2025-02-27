"""Модуль с формами для заполнения на сайте."""


from string import digits, punctuation, ascii_lowercase, ascii_uppercase, printable

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, BooleanField
from wtforms.validators import DataRequired, Email, Length, ValidationError, EqualTo

from app_pack.data_bases import TemporaryUser, User
from app_pack.utils import get_object_by_filter


class CheckEmail(Email):
    """Класс переопределяющий стандартную валидацию e-mail в WTForms.
    E-mail должен содержать в себе '@' и '.', а так же не должен содержаться
    в таблицах temporary_user и user. При невыполнении какого либо условия
    выводится соответствующая ошибка."""

    def __init__(self):
        super().__init__(message="Не верный формат ввода!", check_deliverability=True)
        self.field_flags = {'pattern':'^\S+@\S+\.\S+$'}

    def __call__(self, form, field):
        tu_email = get_object_by_filter(TemporaryUser, TemporaryUser.email == field.data)
        u_email = get_object_by_filter(User, User.email == field.data)
        if tu_email or u_email:
            field.errors[:] = []
            raise ValidationError('Пользователь с таким E-mail уже существует!')
        return super().__call__(form, field)


class CheckPrintable:
    """Класс определяющий валидацию пароля.
    Пароль должен содержать строчные и заглавные буквы латинского алфавита,
    цифры и символы. При несоответствии выводится соответсвующая ошибка."""

    def __init__(self):
        self.field_flags = {'pattern':'^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[_ \W]).{1,}'}

    def __call__(self, form, field):
        flags = [
            any(filter(lambda x: x in field.data, ascii_lowercase)),
            any(filter(lambda x: x in field.data, ascii_uppercase)),
            any(filter(lambda x: x in field.data, digits)),
            any(filter(lambda x: x in field.data, punctuation)),
            any(filter(lambda x: x not in printable, field.data))
            ]
        if flags[4]:
            message = 'Пароль содержит недопустимые символы!'
            field.errors[:] = []
            raise ValidationError(message)
        elif all(flags[0:4]):
            return
        message = 'Добавьте к паролю: '
        args = ['строчные буквы', 'заглавные буквы', 'цифры', 'спец. символы']
        args_m = []
        for i in range(4):
            if not flags[i]:
                args_m.append(args[i])
        args_m = ', '.join(args_m) +'!'
        message += args_m
        field.errors[:] = []
        raise  ValidationError(message)


class RegistrationForm(FlaskForm):
    """Класс для формы регистрации."""

    name = StringField("Имя: ", validators=[
        DataRequired(message='Обязательное поле для заполнения!')
    ])
    email = EmailField("E-mail: ", validators=[
        DataRequired(message='Обязательное поле для заполнения!'),
        CheckEmail()
    ])
    password = PasswordField("Придумайте пароль:", validators=[
        DataRequired(message="Обязательное поле для заполнения!"),
        Length(min=8, message="Пароль должен содержать не менее 8 символов!"),
        CheckPrintable()
    ])
    confirm = PasswordField("Повторите пароль:", validators=[
        DataRequired(message="Обязательное поле для заполнения!"),
        EqualTo("password", message="Пароли не совпадают!")
    ])
    check_box = BooleanField("Принимаю ", validators=[
        DataRequired(message="Обязательное поле для заполнения!")
    ])
    submit = SubmitField("Отправить")


class LoginForm(FlaskForm):
    """Класс для формы авторизации."""

    email = EmailField("E-mail: ", validators=[
        DataRequired(message='Обязательное поле для заполнения!')
    ])
    password = PasswordField("Пароль:", validators=[
        DataRequired(message="Обязательное поле для заполнения!")
    ])
    remember = BooleanField("Сохранить вход")
    submit = SubmitField("Войти")


class ChangePasswordForm(FlaskForm):
    """Класс для формы смены пароля."""

    password = PasswordField("Придумайте пароль:", validators=[
        DataRequired(message="Обязательное поле для заполнения!"),
        Length(min=8, message="Пароль должен содержать не менее 8 символов!"),
        CheckPrintable()
    ])
    confirm = PasswordField("Повторите пароль:", validators=[
        DataRequired(message="Обязательное поле для заполнения!"),
        EqualTo("password", message="Пароли не совпадают!")
    ])
    submit = SubmitField("Изменить")
