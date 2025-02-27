"""Модуль со вспомогательными функциями."""


from threading import Thread
from random import randint, shuffle

import requests
from bs4 import BeautifulSoup
from flask import render_template
from flask_login import current_user, logout_user
from flask_mail import Message
from sqlalchemy import desc, func

from app_pack import app, mail
from app_pack.data_bases import db, Titles, Seasons, Series, UsersTitles, User, TemporaryUser


def get_amount_for_pagination(filter=True):
    """Функция для получения количества всех тайтлов для
    определённого раздела каталога."""

    amount_pages = (db.session.query(Titles).
                    filter(filter).
                    count())
    return amount_pages


def get_titles_for_catalogs(id, filter=True):
    """Функция для получения списка всех тайтлов для определённого
    раздела каталога (по 10 штук на странице), отсортированных по дате
    последнего обновления и названию."""

    titles = (db.session.query(Titles).
              filter(filter).
              order_by(desc(Titles.update_on), Titles.name).
              limit(app.config['MAX_TIT']).
              offset(app.config['MAX_TIT'] * (id - 1)).
              all())
    return titles


def get_user_titles():
    """Функция для получения списка с id всех тайтлов авторизованного пользователя,
    включая: просмотренные, запланированные и в процессе просмотра."""

    if current_user.is_authenticated:
        list_titles_id = (db.session.query(UsersTitles.title_id).
                          filter(UsersTitles.user_id == current_user.id).
                          all())
        return list_titles_id
    return None


def get_genres():
    """Функция для получения списка всех жанров."""

    with open('app_pack/static/texts/genres.txt', 'r', encoding='utf-8') as file:
        genres_list = file.readlines()
    return genres_list


def get_titles_and_amount(list_titles_id, id):
    """Функция для получения списка всех тайтлов (по 10 штук на странице), отсортированного по дате
    последнего обновления и названию, чьи id находятся в списке list_titles_id,
    а так же получения количества этих тайтлов."""

    list_titles_id = list(map(lambda x: x[0], list_titles_id))
    amount_pages = len(list_titles_id)
    titles = get_titles_for_catalogs(id, Titles.id.in_(list_titles_id))
    return titles, amount_pages


def get_want_to_view(id):
    """Функция для получения списка id всех тайтлов, находящихся в разделе
    'запланировано' у авторизованного пользователя."""

    list_titles_id = (db.session.query(UsersTitles.title_id).
                      filter(UsersTitles.user_id == current_user.id, UsersTitles.seria_id.is_(None)).
                      all())
    return get_titles_and_amount(list_titles_id, id)



def get_already_viewed(id):
    """Функция для получения списка id всех тайтлов, находящихся в разделе
    'просмотрено' у авторизованного пользователя."""

    list_titles_id = (db.session.query(Titles.id, UsersTitles.seria_id).
                      join(UsersTitles, Titles.id == UsersTitles.title_id).
                      join(Seasons, Titles.id == Seasons.title_id).
                      join(Series, Seasons.id == Series.season_id).
                      filter(UsersTitles.user_id == current_user.id).
                      group_by(Titles.id, UsersTitles.seria_id).
                      having(UsersTitles.seria_id == func.max(Series.id)).
                      all())
    return get_titles_and_amount(list_titles_id, id)


def get_in_viewing(id):
    """Функция для получения списка id всех тайтлов, находящихся в разделе
    'в процессе просмотра' у авторизованного пользователя."""

    list_titles_id = (db.session.query(Titles.id, UsersTitles.seria_id).
                      join(UsersTitles, Titles.id == UsersTitles.title_id).
                      join(Seasons, Titles.id == Seasons.title_id).
                      join(Series, Seasons.id == Series.season_id).
                      filter(UsersTitles.user_id == current_user.id).
                      group_by(Titles.id, UsersTitles.seria_id).
                      having(UsersTitles.seria_id != func.max(Series.id)).
                      all())
    return get_titles_and_amount(list_titles_id, id)


def get_object_by_id(model, id):
    """Функция для получения объекта по id."""

    obj = db.session.get(model, id)
    return obj


def add_to_db(obj):
    """Функция добавляющая/обновляющая запись в бд."""

    db.session.add(obj)
    db.session.commit()


def delete_from_db(obj):
    """Функция удаляющая запись из бд."""

    db.session.delete(obj)
    db.session.commit()


def change_password(form):
    """Функция для изменения пароля авторизованного пользователя."""

    password = form.password.data
    user = get_object_by_id(User, current_user.id)
    user.set_password(password)
    add_to_db(user)


def delete_acc():
    """Функция для удаления аккаунта авторизованного пользователя."""

    user = get_object_by_id(User, current_user.id)
    logout_user()
    delete_from_db(user)


def get_specific_user_title(user_id, title_id):
    """Функция для получения конкретного тайтла у конкретного пользователя."""

    user_title = (db.session.query(UsersTitles).
                  filter(UsersTitles.user_id == user_id, UsersTitles.title_id == title_id).
                  first())
    return user_title


def add_titles_to_users(args):
    """Функция для добавления тайтла авторизованному пользователю
    в раздел 'просмотрено' или 'запланировано', в зависимости
    от нажатой кнопки."""

    title = args
    user = current_user.id
    if 'viewed' in title:
        title = title.replace('viewed_', '')
        seria = get_last_seria(title)
    elif 'want' in title:
        title = title.replace('want_', '')
        seria = None
    user_title = get_specific_user_title(user, title)
    if user_title:
        user_title.seria_id = seria
    else:
        user_title = UsersTitles(user_id=user, title_id=title, seria_id=seria)
    add_to_db(user_title)


def add_new_series_to_users(args):
    """Функция для обновления последней просмотренной серии определённого тайтла
    у авторизованного пользователя."""

    user = current_user.id
    seria = get_object_by_id(Series, args)
    title = seria.season.title
    last_seria = get_last_seria(title)
    user_title = get_specific_user_title(user, title.id)
    if user_title and user_title.seria_id != last_seria:
        user_title.seria_id = seria.id
    elif not user_title:
        user_title = UsersTitles(user_id=user, title_id=title.id, seria_id=seria.id)
    add_to_db(user_title)
    return last_seria


def delete_titles_from_users(args):
    """Функция для удаления тайтла авторизованного пользователя
    из раздела 'запланировано'."""

    title = args.replace('delete_from_my_', '')
    user = current_user.id
    user_title = get_specific_user_title(user, title)
    delete_from_db(user_title)


def async_send_mail(msg):
    """Функция для отправки e-mail."""

    with app.app_context():
        mail.send(msg)


def send_mail(subject:str, recipient:list, template:str, **kwargs):
    """Функция для создания e-mail."""

    msg = Message(subject, sender=app.config['MAIL_DEFAULT_SENDER'], recipients=recipient)
    msg.body = render_template(template, **kwargs)
    thr = Thread(target=async_send_mail, args=[msg])
    thr.start()
    return thr


def create_random_password():
    """Функция для генерации временного пароля."""

    password = [chr(randint(97, 122)),
                chr(randint(65, 90)),
                str(randint(0, 9)),
                chr(randint(33, 47)),
                chr(randint(97, 122)),
                chr(randint(65, 90)),
                str(randint(0, 9)),
                chr(randint(33, 47))
                ]
    shuffle(password)
    return ''.join(password)


def get_ongoing(anime):
    """Функция для получения id последнего сезона конкретного тайтла."""

    last_seria = get_last_seria(anime)
    seria = get_object_by_id(Series, last_seria)
    return seria.season.id


def get_last_seria(anime):
    """Функция для получения id последней серии конкретного тайтла."""

    if isinstance(anime, Titles):
        anime = anime.id
    seria = (db.session.query(func.max(Series.id)).
             join(Seasons).
             join(Titles).
             filter(Titles.id == anime).
             first())[0]
    return seria


def get_stop_view_data(anime):
    """Функция для получения названия сезона и номера серии конкретного тайтла,
    на просмотре которой остановился пользователь."""

    seria = get_specific_user_title(current_user.id, anime.id)
    seria = get_object_by_id(Series, seria.seria_id)
    season = seria.season.season
    seria = seria.nomber
    return season + ' ' + seria


def get_lando_url(seria_url):
    """Функция для получения полного url серии с токеном
    от animevost по series.url конкретной серии."""

    with requests.Session() as session:
        page = session.get(f'https://v5.vost.pw/frame5.php?play={seria_url}').text
    page = BeautifulSoup(page, 'html.parser')
    try:
        page = str(page.find_all('script')[2])
    except IndexError:
        return f'https://lando.animedia.pro/{seria_url}.mp4'
    page = page[page.find('"file":'):]
    page = page[page.find('http'):]
    page = page[:page.find(' ')]
    return page


def get_object_by_filter(model, filter):
    """Функция для получения объекта по фильтру."""

    obj = (db.session.query(model).
            filter(filter).
            first())
    return obj


def registration_t_user(form):
    """Функция для регистрации временного пользователя."""

    name = form.name.data
    email = form.email.data
    password = form.password.data
    t_user = TemporaryUser(name=name, email=email)
    t_user.set_password(password)
    add_to_db(t_user)
    user = get_object_by_filter(TemporaryUser, TemporaryUser.email == email)
    return user


def get_doc_page_text(path):
    """Функция для извлечения текста из файла."""

    with open(path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text


def registration_user(conf_user):
    """Функция для регистрации постоянного пользователя."""

    user = User(name=conf_user.name,
                email=conf_user.email,
                password=conf_user.password)
    add_to_db(user)
    delete_from_db(conf_user)
