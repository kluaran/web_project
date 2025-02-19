from flask import render_template
from flask_login import current_user
from flask_mail import Message
from threading import Thread
from datetime import datetime
from random import randint, shuffle

from app_pack import app, mail
from app_pack.data_bases import db, Seasons, Series, UsersTitles


def async_send_mail(msg):
    with app.app_context():
        mail.send(msg)


def send_mail(subject:str, recipient:list, template:str, **kwargs):
    msg = Message(subject,      sender=app.config['MAIL_DEFAULT_SENDER'],  recipients=recipient)
    msg.body = render_template(template,  **kwargs)
    thr = Thread(target=async_send_mail,  args=[msg])
    thr.start()
    return thr


def create_random_password():
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
    seasons = db.session.query(Seasons).filter(Seasons.update_on == anime.update_on).all()
    if len(seasons) == 1:
        return seasons[0].id
    for season in anime.seasons:
        try:
            all_series = int(season.series_all)
        except ValueError:
            return season.id
        else:
            if int(season.series_now) < all_series:
                return season.id
    return anime.seasons[-1].id


def get_last_seria(anime):
    series = []
    for season in anime.seasons:
        series.append(season.series[-1].id)
    return max(series)


def get_stop_view_data(anime):
    seria = db.session.query(UsersTitles).filter(UsersTitles.user_id == current_user.id, UsersTitles.title_id == anime.id).first().seria_id
    seria = db.session.query(Series).get(seria)
    season = seria.season.season
    seria = seria.nomber
    return season + ' ' + seria

