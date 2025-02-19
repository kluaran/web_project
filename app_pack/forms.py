from string import digits, punctuation, ascii_lowercase, ascii_uppercase, printable

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, BooleanField
from wtforms.validators import DataRequired, Email, Length, ValidationError, EqualTo

from app_pack.data_bases import db, TemporaryUser, User


class CheckEmail(Email):
    def __init__(self):
        super().__init__(message="Не верный формат ввода!", check_deliverability=True)
        self.field_flags = {'pattern':'^\S+@\S+\.\S+$'}

    def __call__(self, form, field):
        tu_email = db.session.query(TemporaryUser).filter(TemporaryUser.email == field.data).first()
        u_email = db.session.query(User).filter(User.email == field.data).first()
        if tu_email or u_email:
            field.errors[:] = []
            raise ValidationError('Пользователь с таким E-mail уже существует!')
        return super().__call__(form, field)


class CheckPrintable:
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
        else:
            if all(flags[0:4]):
                return
            else:
                message = 'Добавьте к паролю'
                args = ['строчные буквы', 'заглавные буквы', 'цифры', 'спец. символы']
                for i in range(4):
                    if not flags[i]:
                        if ':' not in message:
                            message += ': ' + args[i]
                        else:
                            message += ', ' + args[i]
                message += '!'
        field.errors[:] = []
        raise  ValidationError(message)


class RegistrationForm(FlaskForm):
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
    email = EmailField("E-mail: ", validators=[
        DataRequired(message='Обязательное поле для заполнения!')
    ])
    password = PasswordField("Пароль:", validators=[
        DataRequired(message="Обязательное поле для заполнения!")
    ])
    remember = BooleanField("Сохранить вход")
    submit = SubmitField("Войти")


class ChangePasswordForm(FlaskForm):
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
