"""Модуль с функциями представления и API"""


from time import time
from math import ceil

import jwt
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user, login_required

from app_pack import app
from app_pack.forms import RegistrationForm, LoginForm, ChangePasswordForm
from app_pack.data_bases import TemporaryUser, User, Titles, Series
from app_pack.utils import (send_mail, get_ongoing, create_random_password, get_last_seria, get_stop_view_data,
                            get_lando_url, get_user_titles, get_genres, get_want_to_view, get_already_viewed,
                            get_in_viewing, change_password, delete_acc, add_titles_to_users, add_new_series_to_users,
                            delete_titles_from_users, get_amount_for_pagination, get_titles_for_catalogs,
                            get_object_by_id, get_object_by_filter, registration_t_user, get_doc_page_text,
                            registration_user, add_to_db, trace_moe_api)


@app.route('/')
@app.route('/<int:id>/')
def main(id=1):
    """Функция представления для главной странички.
    Представляет собой каталог всех тайтлов (по 10 на каждой странице),
    отсортированных по дате последнего обновления и алфавиту."""

    amount_pages = get_amount_for_pagination()
    amount_pages = ceil(amount_pages / app.config['MAX_TIT'])
    if id < 1 or id > amount_pages:
        return redirect(url_for('main', id=1))

    list_titles_id = get_user_titles()
    genres_list = get_genres()
    titles = get_titles_for_catalogs(id)
    return render_template('main.html',
                            titles=titles,
                            amount_pages=amount_pages,
                            id=id,
                            max_update=get_ongoing,
                            genres_list=genres_list,
                            list_titles_id=list_titles_id,
                            get_last_seria=get_last_seria)


@app.route('/genres/<int:gen_id>/<int:id>/')
def genres(gen_id=1, id=1):
    """Функция представления для странички с жанрами.
    Представляет собой каталог всех тайтлов определённого жанра (по 10 на каждой странице),
    отсортированных по дате последнего обновления и алфавиту."""

    genres_list = get_genres()
    if gen_id < 1 or gen_id > len(genres_list):
        return redirect(url_for('main', id=1))

    genre = genres_list[gen_id-1][:-2].lower()
    amount_pages = get_amount_for_pagination(filter=Titles.genre.like('%'+genre+'%'))
    amount_pages = ceil(amount_pages / app.config['MAX_TIT'])
    if amount_pages == 0:
        amount_pages = 1
    if id < 1 or id > amount_pages:
        return redirect(url_for('main', id=1))

    list_titles_id = get_user_titles()
    titles = get_titles_for_catalogs(id, filter=Titles.genre.like('%'+genre+'%'))
    return render_template('genres.html',
                           titles=titles,
                           amount_pages=amount_pages,
                           id=id,
                           gen_id=gen_id,
                           max_update=get_ongoing,
                           genres_list=genres_list,
                           list_titles_id=list_titles_id,
                           get_last_seria=get_last_seria)


@app.route('/search-by-picture/', methods=['get', 'post'])
def search_by_picture():
    """Функция представление для странички поиска тайтла по скриншоту,
    с использованием стороннего API."""

    genres_list = get_genres()
    if request.method == 'GET' or not any([request.files['image'].filename, request.form.get('image')]):
        return render_template('search_by_picture.html',
                               animes_data=None,
                               genres_list=genres_list,
                               int=int)
    animes_data = trace_moe_api([request.files, request.form.get('image')])
    return render_template('search_by_picture.html',
                           animes_data=animes_data,
                           genres_list=genres_list,
                           int=int)


@app.route('/my-titles/<category>/<int:id>/')
@login_required
def my_titles(category='in-viewing', id=1):
    """Функция представления для странички с тайтлами пользователя.
    Представляет собой каталог всех тайтлов просмотренных пользователем,
    находящихся в просмотре на данный момент или запланированных к просмотру (по 10 на каждой странице),
    отсортированных по дате последнего обновления и алфавиту."""

    categories = {'want-to-view':get_want_to_view,
                  'already-viewed':get_already_viewed,
                  'in-viewing':get_in_viewing}
    if category not in categories:
        return redirect(url_for('main', id=1))

    func_titles = categories[category]
    titles, amount_pages = func_titles(id)
    amount_pages = ceil(amount_pages / app.config['MAX_TIT'])
    if amount_pages == 0:
        amount_pages = 1
    if id < 1 or id > amount_pages:
        return redirect(url_for('main', id=1))

    list_titles_id = get_user_titles()
    genres_list = get_genres()
    return render_template('my_titles.html',
                            titles=titles,
                            amount_pages=amount_pages,
                            id=id,
                            category=category,
                            max_update=get_ongoing,
                            genres_list=genres_list,
                            list_titles_id=list_titles_id,
                            get_last_seria=get_last_seria,
                            get_stop_view_data=get_stop_view_data)


@app.route('/settings/', methods=['get', 'post'])
@login_required
def settings():
    """Функция представления для страницы настроек пользователя.
    Выполняет смену пароля пользователя и удаление аккаунта."""

    genres_list = get_genres()
    placeholders = {'password':'Придумайте новый пароль',
                    'confirm':'Повторите пароль',
                    'delete_acc':'УДАЛИТЬ'}
    form = ChangePasswordForm()
    if form.validate_on_submit():
        change_password(form)
        flash('Пароль успешно изменён!',
              'success_change')
        return redirect(url_for('settings'))

    elif request.method=='POST' and request.form.get('delete_acc'):
        delete_acc()
        flash('Ваш аккаунт успешно удалён!',
              'success_reg')
        return redirect(url_for('login'))

    return render_template('settings.html',
                           genres_list=genres_list,
                           form=form,
                           placeholders=placeholders)


@app.route('/search/<int:id>/', methods=['get', 'post'])
def search(id=1):
    """Функция представления для странички результатов поиска.
    Представляет собой каталог всех тайтлов (по 10 на каждой странице),
    удовлетворяющих критериям поиска,
    отсортированных по дате последнего обновления и алфавиту."""

    if request.method == 'POST':
        search_data = request.form.get('search_data')
    else:
        search_data = request.args.get('search_data')
    amount_pages = get_amount_for_pagination(filter=Titles.name.like('%'+search_data+'%'))
    amount_pages = ceil(amount_pages / app.config['MAX_TIT'])
    if amount_pages == 0:
        amount_pages = 1
    if id < 1 or id > amount_pages:
        return redirect(url_for('main', id=1))

    list_titles_id = get_user_titles()
    genres_list = get_genres()
    titles = get_titles_for_catalogs(id, filter=Titles.name.like('%'+search_data+'%'))
    return render_template('search.html',
                           titles=titles,
                           amount_pages=amount_pages,
                           id=id,
                           search_data=search_data,
                           max_update=get_ongoing,
                           genres_list=genres_list,
                           list_titles_id=list_titles_id,
                           get_last_seria=get_last_seria)


@app.route('/title/<int:id>/')
def title(id):
    """Функция представления для странички определённого тайтла."""

    list_titles_id = get_user_titles()
    genres_list = get_genres()
    anime = get_object_by_id(Titles, id)
    if not anime:
        return redirect(url_for('main', id=1))

    return render_template('title.html',
                           anime=anime,
                           max_update=get_ongoing,
                           genres_list=genres_list,
                           list_titles_id=list_titles_id,
                           get_last_seria=get_last_seria)


@app.route('/change_viewed_seria/', methods=['get', 'post', 'delete'])
def change_viewed_seria():
    """Функция для обработки запросов от клиентской стороны.
    Отправка url выбранной серии в плеер.
    Добавление тайтла в разделы 'просмотрено' или 'запланировано' при нажатии кнопок.
    Обновление последней просмотренной серии определённого тайтла для конкретного пользователя.
    Удаление тайтла из раздела 'запланировано' при нажатии кнопки."""

    if request.method == 'GET':
        seria = get_object_by_id(Series, dict(request.args)['seria_id'])
        lando_url = get_lando_url(seria.url)
        return f'http://video.animetop.info/{seria.url}.mp4, {lando_url}', 200

    if not current_user.is_authenticated:
        return '', 401

    if request.method == 'POST' and 'list_title' in dict(request.args):
        add_titles_to_users(dict(request.args)['list_title'])
    elif request.method == 'POST' and 'new_seria' in dict(request.args):
        seria_id = add_new_series_to_users(dict(request.args)['new_seria'])
        if str(seria_id) == dict(request.args)['new_seria']:
            return 'last_seria', 200

    elif request.method == 'DELETE' and 'delete_title' in dict(request.args):
        delete_titles_from_users(dict(request.args)['delete_title'])
    return '', 200


@app.route('/login/', methods=['get', 'post'])
def login():
    """Функция представления для странички авторизации.
    Проверяет корректность введённых данных, существование пользователя,
    подтверждён ли e-mail."""

    if current_user.is_authenticated:
        return redirect(url_for('main', id=1))

    placeholders = {'email': 'E-mail', 'password': 'Пароль'}
    form = LoginForm()
    if not form.validate_on_submit():
        return render_template('login.html',
                               form=form,
                               placeholders=placeholders)
    email = form.email.data
    password = form.password.data
    remember = form.remember.data
    user = get_object_by_filter(User, User.email == email)
    if user and user.check_password(password):
        login_user(user, remember=remember)
        return redirect(url_for('main', id=1))

    user = get_object_by_filter(TemporaryUser, TemporaryUser.email == email)
    if user and user.check_password(password):
        flash("Подтвердите регистрацию на своей почте!", 'error')
        return redirect(url_for('login'))

    flash("Не верный E-mail или Пароль!", 'error')
    return redirect(url_for('login'))


@app.route('/logout/')
@login_required
def logout():
    """Функция для выхода пользователя."""

    logout_user()
    return redirect(url_for('login'))


@app.route('/registration/', methods=['get', 'post'])
def registration():
    """Функция представления для странички регистрации.
    Проверяет корректность введённых данных, создаёт временного пользователя,
    оправляет пользователю на почту ссылку с токеном для подтверждения e-mail."""

    placeholders = {'name':'Вася', 'email':'vasy@gmail.com', 'password':'aaAA11!!', 'confirm':'aaAA11!!'}
    form = RegistrationForm()
    if not form.validate_on_submit():
        return render_template('registration.html',
                               form=form,
                               placeholders=placeholders)

    user = registration_t_user(form)
    token = jwt.encode({'registration_confirmation': user.id, 'exp': time()+3600*24},
                        app.config['SECRET_KEY'],
                        algorithm='HS256')
    url = url_for('regconf', token=token, _external=True)
    send_mail('Подтверждение регистрации',
              [user.email],
              'email.txt',
              **{'email_head':f'Уважаемый(ая) {user.name},',
                 'email_body':f'для подтверждения регистрации перейдите по ссылке: {url}'})

    flash('Для окончания регистрации, мы выслали вам на почту письмо со ссылкой, пожалуйста перейдите по ней.',
          'success_reg')
    return redirect(url_for('login'))


@app.route('/oferta/')
def oferta():
    """Функция представления для странички пользовательского соглашения."""

    text = get_doc_page_text('app_pack/static/texts/oferta.txt')
    return render_template('text_page.html',
                           title='Пользовательское соглашение',
                           head='Пользовательское соглашение',
                           body=text)


@app.route('/privacy/')
def privacy():
    """Функция представления для странички политики конфиденциальности."""

    text = get_doc_page_text('app_pack/static/texts/konf.txt')
    return render_template('text_page.html',
                           title='Политика конфиденциальности',
                           head='Политика конфиденциальности персональных данных',
                           body=text)


@app.route('/right-holders/')
def right_holders():
    """Функция представления для странички правообладателей."""

    text = get_doc_page_text('app_pack/static/texts/right_holders.txt')
    return render_template('text_page.html',
                           title='Для правообладателей',
                           head='Для правообладателей',
                           body=text)


@app.route('/regconf/<token>/')
def regconf(token):
    """Функция представления для странички подтверждения e-mail.
    Проверяет корректность токена и время его использования.
    Переносит временного пользователя в постоянные."""

    try:
        user_id = jwt.decode(token,
                             app.config['SECRET_KEY'],
                             algorithms='HS256')['registration_confirmation']
    except:
        return render_template('text_page.html',
                               title='Ошибка',
                               head='ОШИБКА',
                               body='Такой страницы не существует')

    conf_user = get_object_by_filter(TemporaryUser, TemporaryUser.id == user_id)
    registration_user(conf_user)
    return render_template('text_page.html',
                           title='Подтверждение регистрации',
                           head='Успех!',
                           body='Поздравляем с успешным завершением регистрации!')


@app.route('/reset-password/', methods=['get', 'post'])
def reset_password():
    """Функция представления для странички восстановления пароля.
    Проверяет корректность введённого e-mail,
    генерирует новый пароль и отправляет его на почту пользователя."""

    if current_user.is_authenticated:
        return redirect(url_for('main', id=1))

    if request.method == 'GET' or not request.form.get('email'):
        return render_template('reset_password.html')

    user = get_object_by_filter(User, User.email == request.form.get('email'))
    if  not user:
        flash('E-mail указан не верно!', 'error_email')
        return redirect(url_for('reset_password'))

    password = create_random_password()
    send_mail('Восстановление пароля',
              [user.email],
              'email.txt',
              **{'email_head': f'Уважаемый(ая) {user.name},',
                 'email_body': f'Ваш пароль сброшен! Для авторизации воспользуйтесь временным паролем: {password}\n'
                               f'После авторизации перейдите в настройки и смените его!'})
    user.set_password(password)
    add_to_db(user)
    flash('Вам на почту отправлен временный пароль для входа!', 'success_reg')
    return redirect(url_for('login'))
