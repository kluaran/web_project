"""Модуль для парсинга animevost и автоматического обновления
базы данных с тайтлами."""


from datetime import datetime
from bs4 import BeautifulSoup
import requests

from app_pack import app
from app_pack.data_bases import db, Titles, Seasons, Series
from app_pack.utils import get_object_by_filter


class WebPage():
    """Класс для парсинга страничек с тайтлами."""

    __domen = 'https://v5.vost.pw/'

    def __init__(self, url):
        """Инициализация объекта web_page с атрибутами url
        и page в виде кода html."""

        with requests.Session() as session:
            page = session.get(self.__domen + url).text
            self.url = url
            self.page = BeautifulSoup(page, 'html.parser')


    def get_urls_from_main(self):
        """Метод для получения списка url всех тайтлов с главной странички."""

        self.list_urls = self.page.find_all('div', 'shortstoryHead')
        self.parsing_a()


    def parsing_a(self):
        """Метод для извлечения url из блока <a> в html."""

        for i in self.list_urls:
            a = i.find('a')
            a = str(a)
            if 'vost.pw/' in a:
                a = a[a.find('vost.pw/') + 8:a.find('.html')] + '.html'
            else:
                a = a[a.find('/')+1:a.find('.html')] + '.html'
            self.list_urls[self.list_urls.index(i)] = a


    def check_any_seasons(self):
        """Метод проверяющий наличие других сезонов в тайтле."""

        spoiler = self.page.find('div', {'class': 'text_spoiler'})
        self.list_urls = spoiler


    def get_spoilers(self):
        """Метод для получения списка url всех сезонов данного тайтла."""

        self.list_urls = self.list_urls.find_all('li')
        self.parsing_a()


    def get_title_name(self):
        """Метод для прасинга названия тайтла.
        Сохраняет в атрибуты название сезона,
        текущее количество серий и общее количество серий."""

        self.title_name = self.page.find('div', 'shortstoryHead').getText().strip()
        self.amount_series = self.title_name[self.title_name.find('['):self.title_name.find(']')]
        if '1 из' in self.amount_series:
            self.amount_series_now = 1
        else:
            self.amount_series_now = self.amount_series[self.amount_series.find('-') + 1:self.amount_series.find(' из')].strip()
        self.amount_series = self.amount_series[self.amount_series.find('из') + 2:].strip()
        self.title_name = self.title_name[:self.title_name.find('/')]


    def get_more_information(self):
        """Метод для добавления в атрибуты ссылки на обложку сезона,
        года выхода, жанра, описания и рейтинга."""

        inf_blok = self.page.find('div', 'shortstoryContent')
        inf_blok = inf_blok.find('td')

        self.cover = str(inf_blok.find('img'))
        self.cover = self.cover[self.cover.find('src')+6:]
        self.cover = self.cover[:self.cover.find('"')-1]

        list_p = inf_blok.find_all('p')
        for p in list_p:
            cotegory = p.getText()
            if 'Год выхода:' in cotegory:
                self.year = cotegory[12:]
            elif 'Жанр:' in cotegory:
                self.genres = cotegory[6:]
            elif 'Описание:' in cotegory:
                self.description = cotegory[10:]

        self.rating = int(inf_blok.find('li', {'class':'current-rating'}).getText())/20


    def get_last_update(self):
        """Метод для добавления в атрибут последней даты обновления сезона."""

        last_update = self.page.find('span', 'staticInfoLeftData').getText()
        months = {'январь' : '01',
                  'февраль' : '02',
                  'март' : '03',
                  'апрель' : '04',
                  'май' : '05',
                  'июнь' : '06',
                  'июль' : '07',
                  'август' : '08',
                  'сентябрь' : '09',
                  'октябрь' : '10',
                  'ноябрь' : '11',
                  'декабрь' : '12',}
        day = last_update[:last_update.find(' ')]
        last_update = last_update.replace(day+' ', '')
        month = last_update[:last_update.find(' ')]
        year = last_update.replace(month+' ', '')
        month = months[month]
        self.last_update = datetime.strptime(day+'-'+month+'-'+year, '%d-%m-%Y')

    def get_viedo(self):
        """Метод для добавления в атрибут словаря с номерами серий и ссылками на них."""

        video = self.page.find('div', {'class':'shortstoryContent'})
        video = video.find_all('script')[1]
        video = str(video)
        video = video[video.find('{'):video.find('}')+1]
        if video[-2] != '"':
            video = video[:-2] + '}'
        self.dict_series = eval(video)


def parsing_main(id):
    """Функция для создания объектов главных страничек."""

    page = WebPage(f'tip/page/{id}/')
    page.get_urls_from_main()
    return page


def parsing_page(page):
    """Функция для парсинга тайтлов с главных страничек."""

    for url in page.list_urls:
        season = get_object_by_filter(Seasons, Seasons.url_animevost == url)
        season_updates = WebPage(url)
        if season:
            parsing_exist_season(season, season_updates)
        else:
            parsing_not_exist_season(season, season_updates)


def parsing_exist_season(season, season_updates):
    """Функция для обновления уже существующего сезона."""

    parsing_title(season_updates)
    amount_series_now = max(int(season_updates.amount_series_now), len(season_updates.dict_series.values()))
    if season_updates.last_update > season.update_on:
        title = season.title
        title.update_on = season_updates.last_update
        season.update_on = season_updates.last_update
        db.session.add(title)
    if amount_series_now > season.series_now:
        season.series_now = amount_series_now
    if season_updates.amount_series != season.series_all:
        season.series_all = season_updates.amount_series
    if len(season_updates.dict_series) > len(season.series):
        for seria in season.series:
            season_updates.dict_series.pop(seria.nomber)
        for key, value in season_updates.dict_series.items():
            series_db = Series(nomber=key, url=value, season=season)
            db.session.add(series_db)
    db.session.add(season)
    db.session.commit()


def parsing_not_exist_season(season, season_updates):
    """Функция для домабления в базу данных нового сезона."""

    try:
        season_updates.get_viedo()
    except SyntaxError:
        return

    season_updates.check_any_seasons()
    if not season_updates.list_urls:
        create_main_title(season_updates)
        return

    season_updates.get_spoilers()
    if not season_updates.list_urls:
        create_main_title(season_updates)
        return

    for spoiler in season_updates.list_urls:
        if spoiler != 'Non.html':
            season = get_object_by_filter(Seasons, Seasons.url_animevost == spoiler)
            break
    title = season.title
    parsing_title(season_updates)
    season_db = get_dict_season(season_updates)
    season_db.title = title
    db.session.add(season_db)
    if season_updates.last_update > title.update_on:
        title.update_on = season_updates.last_update
    get_dict_series(season_updates, season_db)
    db.session.add(title)
    db.session.commit()


def parsing_title(title):
    """Функция для создания всех необходимых атрибутов для тайтла."""

    title.get_title_name()
    title.get_more_information()
    title.get_last_update()
    title.get_viedo()


def create_main_title(title):
    """Функция для добавления нового тайтла в базу данных."""

    parsing_title(title)
    title_db = get_dict_title(title)
    db.session.add(title_db)
    season_db = get_dict_season(title)
    season_db.title = title_db
    db.session.add(season_db)
    get_dict_series(title, season_db)
    db.session.commit()
    return title_db


def get_dict_title(title):
    """Функция для создания экземпляра модели Titles."""

    title_db = Titles(name = title.title_name,
                      year = title.year,
                      genre = title.genres,
                      rating = title.rating,
                      description = title.description,
                      update_on = title.last_update,
                      cover = title.cover)
    return title_db


def get_dict_season(title):
    """Функция для создания экземпляра модели Seasons."""

    amount_series_now = max(int(title.amount_series_now), len(title.dict_series.values()))
    season_db = Seasons(season = title.title_name,
                        url_animevost = title.url,
                        series_now = amount_series_now,
                        series_all = title.amount_series,
                        update_on = title.last_update)
    return season_db


def get_dict_series(title, season_db):
    """Функция для создания экземпляров модели Series."""

    for key, value in title.dict_series.items():
        series_db = Series(nomber = key,
                           url = value,
                           season = season_db)
        db.session.add(series_db)


def update_titles():
    """Функция для обновления базы данных тайтлов."""

    with app.app_context():
        for i in range(1, 5):
            page = parsing_main(i)
            parsing_page(page)


if __name__ == '__main__':
    update_titles()


