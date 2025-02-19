import jwt
from time import time
from math import ceil

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user, login_required

from app_pack import app
from app_pack.forms import RegistrationForm, LoginForm, ChangePasswordForm
from app_pack.data_bases import db, TemporaryUser, User, Titles, Series, UsersTitles
from app_pack.utils import send_mail, get_ongoing, create_random_password, get_last_seria, get_stop_view_data


@app.route('/')
@app.route('/<int:id>/')
def main(id=1):
    amount_pages = db.session.query(Titles).count()
    amount_pages = ceil(amount_pages/10)
    if 1 <= id <= amount_pages:
        if current_user.is_authenticated:
            list_titles_id = db.session.query(UsersTitles.title_id).filter(UsersTitles.user_id == current_user.id).all()
        else:
            list_titles_id = None
        with open('app_pack/static/texts/genres.txt', 'r', encoding='utf-8') as file:
            genres_list = file.readlines()
        titles = db.session.query(Titles).order_by(Titles.update_on).all()
        if id == amount_pages:
            titles = titles[-10 * (id - 1)-1::-1]
        else:
            titles = titles[-10*(id-1)-1:-10*id-1:-1]
        return render_template('main.html',
                               titles=titles,
                               amount_pages=amount_pages,
                               id=id,
                               max_update=get_ongoing,
                               genres_list=genres_list,
                               list_titles_id=list_titles_id,
                               get_last_seria=get_last_seria)
    else:
        return redirect(url_for('main', id=1))


@app.route('/genres/<int:gen_id>/<int:id>/')
def genres(gen_id=1, id=1):
    if gen_id < 1 or gen_id > 27:
        return redirect(url_for('main', id=1))

    if current_user.is_authenticated:
        list_titles_id = db.session.query(UsersTitles.title_id).filter(UsersTitles.user_id == current_user.id).all()
    else:
        list_titles_id = None
    with open('app_pack/static/texts/genres.txt', 'r', encoding='utf-8') as file:
        genres_list = file.readlines()
    titles = db.session.query(Titles).filter(Titles.genre.like('%' + genres_list[gen_id-1][:-2].lower() + '%')).order_by(Titles.update_on).all()
    amount_pages = ceil(len(titles) / 10)
    if titles:
        if 1 <= id <= amount_pages:
            if id == amount_pages:
                titles = titles[-10 * (id - 1) - 1::-1]
            else:
                titles = titles[-10 * (id - 1) - 1:-10 * id - 1:-1]
        else:
            return redirect(url_for('main', id=1))
    else:
        titles = None
        amount_pages = 1
        id = 1
    return render_template('genres.html',
                           titles=titles,
                           amount_pages=amount_pages,
                           id=id,
                           gen_id=gen_id,
                           max_update=get_ongoing,
                           genres_list=genres_list,
                           list_titles_id=list_titles_id,
                           get_last_seria=get_last_seria)


@app.route('/my-titles/<category>/<int:id>/')
@login_required
def my_titles(category='in-viewing', id=1):
    if category not in ['already-viewed', 'in-viewing', 'want-to-view']:
        return redirect(url_for('main', id=1))

    if current_user.is_authenticated:
        list_titles_id = db.session.query(UsersTitles.title_id).filter(UsersTitles.user_id == current_user.id).all()
    else:
        list_titles_id = None
    with open('app_pack/static/texts/genres.txt', 'r', encoding='utf-8') as file:
        genres_list = file.readlines()

    user_titles = current_user.users_titles
    if user_titles and category == 'want-to-view':
        titles = []
        for elem in user_titles:
            if not elem.seria_id:
                titles.append(elem.title_id)
        titles = db.session.query(Titles).filter(Titles.id.in_(titles)).order_by(Titles.update_on).all()
    elif user_titles and category == 'already-viewed':
        titles = list(map(lambda x: x[0], list_titles_id))
        titles = db.session.query(Titles).filter(Titles.id.in_(titles)).all()
        last_series_list = list(map(get_last_seria, titles))
        titles = []
        for elem in user_titles:
            if elem.seria_id in last_series_list:
                titles.append(elem.title_id)
        titles = db.session.query(Titles).filter(Titles.id.in_(titles)).order_by(Titles.update_on).all()
    elif user_titles and category == 'in-viewing':
        titles = list(map(lambda x: x[0], list_titles_id))
        titles = db.session.query(Titles).filter(Titles.id.in_(titles)).all()
        last_series_list = list(map(get_last_seria, titles))
        titles = []
        for elem in user_titles:
            if elem.seria_id and elem.seria_id not in last_series_list:
                titles.append(elem.title_id)
        titles = db.session.query(Titles).filter(Titles.id.in_(titles)).order_by(Titles.update_on).all()
    else:
        titles = []

    amount_pages = ceil(len(titles) / 10)
    if titles:
        if 1 <= id <= amount_pages:
            if id == amount_pages:
                titles = titles[-10 * (id - 1) - 1::-1]
            else:
                titles = titles[-10 * (id - 1) - 1:-10 * id - 1:-1]
        else:
            return redirect(url_for('main', id=1))
    else:
        titles = None
        amount_pages = 1
        id = 1
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
    with open('app_pack/static/texts/genres.txt', 'r', encoding='utf-8') as file:
        genres_list = file.readlines()
    placeholders = {'password':'Придумайте новый пароль', 'confirm':'Повторите пароль', 'delete_acc':'УДАЛИТЬ'}
    form = ChangePasswordForm()
    if form.validate_on_submit():
        password = form.password.data
        user = db.session.query(User).filter(User.id == current_user.id).first()
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Пароль успешно изменён!',
              'success_change')
        return redirect(url_for('settings'))
    elif request.method=='POST' and request.form.get('delete_acc'):
        user = db.session.query(User).filter(User.id == current_user.id).first()
        logout_user()
        db.session.delete(user)
        db.session.commit()
        flash('Ваш аккаунт успешно удалён!','success_reg')
        return redirect(url_for('login'))

    return render_template('settings.html',
                           genres_list=genres_list,
                           form=form,
                           placeholders=placeholders)


@app.route('/search/<int:id>/', methods=['get', 'post'])
def search(id=1):
    if request.method != 'POST' and not request.args:
        return redirect(url_for('main', id=1))
    elif request.method == 'POST':
        search_data = request.form.get('search_data')
        if not search_data:
            return redirect(url_for('main', id=1))
    else:
        search_data = request.args.get('search_data')

    if current_user.is_authenticated:
        list_titles_id = db.session.query(UsersTitles.title_id).filter(UsersTitles.user_id == current_user.id).all()
    else:
        list_titles_id = None
    with open('app_pack/static/texts/genres.txt', 'r', encoding='utf-8') as file:
        genres_list = file.readlines()
    titles = db.session.query(Titles).filter(Titles.name.like('%'+search_data+'%')).order_by(Titles.update_on).all()
    if titles:
        amount_pages = ceil(len(titles)/ 10)
        if 1 <= id <= amount_pages:
            if id == amount_pages:
                titles = titles[-10 * (id - 1) - 1::-1]
            else:
                titles = titles[-10 * (id - 1) - 1:-10 * id - 1:-1]
        else:
            return redirect(url_for('main', id=1))
    else:
        titles = None
        amount_pages = 1
        id = 1
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
    if current_user.is_authenticated:
        list_titles_id = db.session.query(UsersTitles.title_id).filter(UsersTitles.user_id == current_user.id).all()
    else:
        list_titles_id = None
    with open('app_pack/static/texts/genres.txt', 'r', encoding='utf-8') as file:
        genres_list = file.readlines()
    anime = db.session.query(Titles).filter(Titles.id==id).first()
    if not anime:
        return redirect(url_for('main', id=1))
    return render_template('title.html',
                           anime=anime,
                           max_update=get_ongoing,
                           genres_list=genres_list,
                           list_titles_id=list_titles_id,
                           get_last_seria=get_last_seria                           )


@app.route('/change_viewed_seria/', methods=['get', 'post', 'delete'])
def change_viewed_seria():
    if request.method == 'GET':
        seria_url = db.session.query(Series.url).filter(Series.id==dict(request.args)['seria_id']).first()
        return f'http://video.animetop.info/{seria_url[0]}.mp4', 200
    elif request.method == 'POST' and 'list_title' in dict(request.args):
        if current_user.is_authenticated:
            title = dict(request.args)['list_title']
            user = current_user.id
            if 'viewed' in title:
                title = title.replace('viewed_', '')
                title = db.session.query(Titles).filter(Titles.id == title).first()
                series = []
                for season in title.seasons:
                    series.append(season.series[-1].id)
                seria = max(series)
                title = title.id
            elif 'want' in title:
                title = title.replace('want_', '')
                seria = None

            user_title = db.session.query(UsersTitles).filter(UsersTitles.user_id == user, UsersTitles.title_id == title).first()
            if user_title:
                user_title.seria_id = seria
            else:
                user_title = UsersTitles(user_id=user,
                                         title_id=title,
                                         seria_id=seria)
            db.session.add(user_title)
            db.session.commit()
    elif request.method == 'POST' and 'new_seria' in dict(request.args):
        if current_user.is_authenticated:
            user = current_user.id
            seria = db.session.query(Series).get(dict(request.args)['new_seria'])
            title = seria.season.title
            series_id = []
            for season in title.seasons:
                series_id.append(season.series[-1].id)
            seria_id = max(series_id)
            user_title = db.session.query(UsersTitles).filter(UsersTitles.user_id == user, UsersTitles.title_id == title.id).first()
            if user_title:
                if user_title.seria_id != seria_id:
                    user_title.seria_id = seria.id
            else:
                user_title = UsersTitles(user_id=user,
                                         title_id=title.id,
                                         seria_id=seria.id)
            db.session.add(user_title)
            db.session.commit()
            if str(seria_id) == dict(request.args)['new_seria']:
                return 'last_seria', 200
    elif request.method == 'DELETE' and 'delete_title' in dict(request.args):
        if current_user.is_authenticated:
            title = dict(request.args)['delete_title'].replace('delete_from_my_', '')
            user = current_user.id
            user_title = db.session.query(UsersTitles).filter(UsersTitles.user_id == user, UsersTitles.title_id == title).first()
            db.session.delete(user_title)
            db.session.commit()
    return '', 200


@app.route('/login/', methods=['get', 'post'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main', id=1))

    placeholders = {'email': 'E-mail', 'password': 'Пароль'}
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        remember = form.remember.data
        user = db.session.query(User).filter(User.email == email).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            return redirect(url_for('main', id=1))

        user = db.session.query(TemporaryUser).filter(TemporaryUser.email == email).first()
        if user and user.check_password(password):
            flash("Подтвердите регистрацию на своей почте!", 'error')
            return redirect(url_for('login'))

        flash("Не верный E-mail или Пароль!", 'error')
        return redirect(url_for('login'))

    return render_template('login.html', form = form, placeholders=placeholders)


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/registration/', methods=['get', 'post'])
def registration():
    placeholders = {'name':'Вася', 'email':'vasy@gmail.com', 'password':'aaAA11!!', 'confirm':'aaAA11!!'}
    form = RegistrationForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        t_user = TemporaryUser(name=name, email=email)
        t_user.set_password(password)
        db.session.add(t_user)
        db.session.commit()

        user = db.session.query(TemporaryUser).filter(TemporaryUser.email==email).first()

        token = jwt.encode(
            {'registration_confirmation': user.id, 'exp': time()+3600*24},
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )

        url = url_for('regconf', token=token, _external=True)
        send_mail(
            'Подтверждение регистрации',
            [email],
            'email.txt',
            **{'email_head':f'Уважаемый(ая) {name},', 'email_body':f'для подтверждения регистрации перейдите по ссылке: {url}'}
        )

        flash('Для окончания регистрации, мы выслали вам на почту письмо со ссылкой, пожалуйста перейдите по ней.', 'success_reg')
        return redirect(url_for('login'))

    return render_template('registration.html', form=form, placeholders=placeholders)


@app.route('/oferta/')
def oferta():
    with open('app_pack/static/texts/oferta.txt', 'r', encoding='utf-8') as file:
        text = file.read()
    return render_template('text_page.html',
                           title='Пользовательское соглашение',
                           head='Пользовательское соглашение',
                           body=text)


@app.route('/privacy/')
def privacy():
    with open('app_pack/static/texts/konf.txt', 'r', encoding='utf-8') as file:
        text = file.read()
    return render_template('text_page.html',
                           title='Политика конфиденциальности',
                           head='Политика конфиденциальности персональных данных',
                           body=text)


@app.route('/right-holders/')
def right_holders():
    with open('app_pack/static/texts/right_holders.txt', 'r', encoding='utf-8') as file:
        text = file.read()
    return render_template('text_page.html',
                           title='Для правообладателей',
                           head='Для правообладателей',
                           body=text)


@app.route('/regconf/<token>/')
def regconf(token):
    try:
        user_id = jwt.decode(
            token,
            app.config['SECRET_KEY'],
            algorithms='HS256'
        )['registration_confirmation']
    except:
        user_id = None

    conf_user = db.session.query(TemporaryUser).filter(TemporaryUser.id == user_id).first()
    if user_id and conf_user:
        user = User(name=conf_user.name,
                    email=conf_user.email,
                    password=conf_user.password)
        db.session.add(user)
        db.session.delete(conf_user)
        db.session.commit()
        return render_template('text_page.html',
                               title='Подтверждение регистрации',
                               head='Успех!',
                               body='Поздравляем с успешным завершением регистрации!')
    return render_template('text_page.html',
                           title='Ошибка',
                           head='ОШИБКА',
                           body='Такой страницы не существует')


@app.route('/reset-password/', methods=['get', 'post'])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('main', id=1))
    if request.method == 'POST' and request.form.get('email'):
        user = db.session.query(User).filter(User.email == request.form.get('email')).first()
        if  user:
            password = create_random_password()
            send_mail('Восстановление пароля',
                      [user.email],
                      'email.txt',
                      **{'email_head': f'Уважаемый(ая) {user.name},',
                         'email_body': f'Ваш пароль сброшен! Для авторизации воспользуйтесь временным паролем: {password}\n'
                                       f'После авторизации перейдите в настройки и смените его!'}
                      )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Вам на почту отправлен временный пароль для входа!', 'success_reg')
            return redirect(url_for('login'))
        else:
            flash('E-mail указан не верно!', 'error_email')
            return redirect(url_for('reset_password'))
    return render_template('reset_password.html')


