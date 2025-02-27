"""Модуль с моделями таблиц базы данных."""


from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from app_pack import db, login


@login.user_loader
def load_user(id):
    """Функция авторизующая пользователя."""

    return db.session.get(User, int(id))


class TemporaryUser(db.Model):
    """Модель временного пользователя.
    set_password устанавливает хэшированный пароль,
    check_password проверяет соответствие переданного и хэшированного паролей."""

    __tablename__ = 'temporary_users'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.now())

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class User(db.Model, UserMixin):
    """Модель постоянного пользователя.
    set_password устанавливает хэшированный пароль,
    check_password проверяет соответствие переданного и хэшированного паролей."""

    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    users_titles = db.relationship('UsersTitles', backref='user', cascade='all,delete-orphan')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Titles(db.Model):
    """Модель таблицы с тайтлами."""

    __tablename__ = 'titles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    cover = db.Column(db.String(255), nullable=False)
    year = db.Column(db.Integer(), nullable=False)
    genre = db.Column(db.String(255), nullable=False)
    rating = db.Column(db.Integer(), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    update_on = db.Column(db.DateTime(), nullable=False, default=datetime.now())
    seasons = db.relationship('Seasons', backref='title')
    users_titles = db.relationship('UsersTitles', backref='title')


class Seasons(db.Model):
    """Модель таблицы с сезонами."""

    __tablename__ = 'seasons'
    id = db.Column(db.Integer(), primary_key=True)
    title_id = db.Column(db.Integer(), db.ForeignKey('titles.id'), nullable=False)
    season = db.Column(db.String(255), nullable=False)
    url_animevost = db.Column(db.String(255), nullable=False)
    series_now = db.Column(db.Integer(), nullable=False)
    series_all = db.Column(db.String(255), nullable=False)
    update_on = db.Column(db.DateTime(), nullable=False, default=datetime.now())
    series = db.relationship('Series', backref='season')


class Series(db.Model):
    """Модель таблицы с сериями."""

    __tablename__ = 'series'
    id = db.Column(db.Integer(), primary_key=True)
    season_id = db.Column(db.Integer(), db.ForeignKey('seasons.id'), nullable=False)
    nomber = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    users_titles = db.relationship('UsersTitles', backref='seria')


class UsersTitles(db.Model):
    """Модель таблицы с тайтлами, добавленными пользователями в разделы
    'просмотрено', 'запланировано' и 'в процессе просмотра'."""

    __tablename__ = 'users_titles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'), nullable=False)
    title_id = db.Column(db.Integer(), db.ForeignKey('titles.id'), nullable=False)
    seria_id = db.Column(db.Integer(), db.ForeignKey('series.id'))
