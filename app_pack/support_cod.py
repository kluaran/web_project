from datetime import datetime
from bs4 import BeautifulSoup
import requests

from app_pack import app
from app_pack.data_bases import db, Titles, Seasons, Series


class WebPage():
    __domen = 'https://v5.vost.pw/'

    def __init__(self, url):
        with requests.Session() as session:
            page = session.get(self.__domen + url).text
            self.url = url
            self.page = BeautifulSoup(page, 'html.parser')


    def get_urls_from_main(self):
        self.list_urls = self.page.find_all('div', 'shortstoryHead')
        self.parsing_a()


    def parsing_a(self):
        for i in self.list_urls:
            a = i.find('a')
            a = str(a)
            if 'vost.pw/' in a:
                a = a[a.find('vost.pw/') + 8:a.find('.html')] + '.html'
            else:
                a = a[a.find('/')+1:a.find('.html')] + '.html'
            self.list_urls[self.list_urls.index(i)] = a


    def check_any_seasons(self):
        spoiler = self.page.find('div', {'class': 'text_spoiler'})
        self.list_urls = spoiler


    def get_spoilers(self):
        self.list_urls = self.list_urls.find_all('li')
        self.parsing_a()


    def get_title_name(self):
        self.title_name = self.page.find('div', 'shortstoryHead').getText().strip()
        if '[' not in self.title_name:
            self.amount_series = 2
            self.amount_series_now = 2
        elif '[1- из 1]' in self.title_name or 'Евангелион 2.22 Ты [Не] Пройдешь' in self.title_name:
            self.amount_series = 1
            self.amount_series_now = 1
        elif '[1-13 и 13]' in self.title_name:
            self.amount_series = 13
            self.amount_series_now = 13
        elif '[6 из 6]' in self.title_name:
            self.amount_series = 6
            self.amount_series_now = 6
        elif '[12 из 12]' in self.title_name or 'Закрыты в рамках. Геном [Прямая трансляция]' in self.title_name or 'Futsuu no Joshikousei ga [Locodol] Yattemita' in self.title_name:
            self.amount_series = 12
            self.amount_series_now = 12
        else:
            self.amount_series = self.title_name[self.title_name.find('['):self.title_name.find(']')]
            if '1 из' in self.amount_series:
                self.amount_series_now = 1
            else:
                self.amount_series_now = self.amount_series[
                                         self.amount_series.find('-') + 1:self.amount_series.find(' из')].strip()
            self.amount_series = self.amount_series[self.amount_series.find('из') + 2:].strip()
        self.title_name = self.title_name[:self.title_name.find('/')]


    def get_more_information(self):
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
        video = self.page.find('div', {'class':'shortstoryContent'})
        video = video.find_all('script')[1]
        video = str(video)
        video = video[video.find('{'):video.find('}')+1]
        if video[-2] != '"':
            video = video[:-2] + '}'
        self.dict_series = eval(video)


def parsing_main(id):
    page = WebPage(f'tip/page/{id}/')
    page.get_urls_from_main()
    return page


def parsing_titles_for_bd(page):
    for url in page.list_urls:
        print(url)
        if url == 'tip/tv/3192-kijin-gentoushou.html':
            continue
        if (url,) in db.session.query(Seasons.url_animevost).all():
            continue
        title = WebPage(url)
        title.check_any_seasons()
        if not title.list_urls:
            create_main_title(title)
        else:
            title.get_spoilers()
            if not title.list_urls:
                create_main_title(title)
                continue
            urls = db.session.query(Seasons.url_animevost).all()
            if (title.list_urls[0],) not in urls:
                main_title = WebPage(title.list_urls[0])
                title_db = create_main_title(main_title)
                for title_url in title.list_urls[1:]:
                    print('SUB_URL:', title_url)
                    if title_url == 'Non.html':
                        continue
                    sub_title = WebPage(title_url)
                    parsing_title(sub_title)
                    season_db = get_dict_season(sub_title)
                    season_db.title = title_db
                    db.session.add(season_db)
                    if sub_title.last_update > title_db.update_on:
                        title_db.update_on = sub_title.last_update
                    get_dict_series(sub_title, season_db)
                db.session.add(title_db)
                db.session.commit()


def parsing_title(title):
    title.get_title_name()
    title.get_more_information()
    title.get_last_update()
    title.get_viedo()


def create_main_title(title):
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
    title_db = Titles(name = title.title_name,
                      year = title.year,
                      genre = title.genres,
                      rating = title.rating,
                      description = title.description,
                      update_on = title.last_update,
                      cover = title.cover)
    return title_db


def get_dict_season(title):
    amount_series_now = max(int(title.amount_series_now), len(title.dict_series.values()))
    season_db = Seasons(season = title.title_name,
                        url_animevost = title.url,
                        series_now = amount_series_now,
                        series_all = title.amount_series,
                        update_on = title.last_update)
    return season_db


def get_dict_series(title, season_db):
    for key, value in title.dict_series.items():
        series_db = Series(nomber = key,
                           url = value,
                           season = season_db)
        db.session.add(series_db)


def update_titles():
    with app.app_context():
        for i in range(1, 3):
            page = parsing_main(i)
            for url in page.list_urls:
                season = db.session.query(Seasons).filter(Seasons.url_animevost == url).first()
                season_updates = WebPage(url)
                if season:
                    season_updates.get_title_name()
                    season_updates.get_last_update()
                    season_updates.get_viedo()
                    amount_series_now = max(int(season_updates.amount_series_now), len(season_updates.dict_series.values()))
                    if season_updates.last_update > season.update_on:
                        title = season.title
                        title.update_on = season_updates.last_update
                        season.update_on = season_updates.last_update
                    if amount_series_now > season.series_now:
                        season.series_now = amount_series_now
                    if season_updates.amount_series != season.series_all:
                        season.series_all = season_updates.amount_series
                    if len(season_updates.dict_series) > len(season.series):
                        for seria in season.series:
                            season_updates.dict_series.pop(seria.nomber)
                        for key, value in season_updates.dict_series.items():
                            series_db = Series(nomber=key,
                                               url=value,
                                               season=season)
                            db.session.add(series_db)
                    db.session.add_all([title, season])
                    db.session.commit()
                else:
                    try:
                        season_updates.get_viedo()
                    except SyntaxError:
                        continue
                    season_updates.check_any_seasons()
                    if not season_updates.list_urls:
                        create_main_title(season_updates)
                    else:
                        season_updates.get_spoilers()
                        if not season_updates.list_urls:
                            create_main_title(season_updates)
                        else:
                            for spoiler in season_updates.list_urls:
                                if spoiler != 'Non.html':
                                    season = db.session.query(Seasons).filter(Seasons.url_animevost == spoiler).first()
                                    break
                            title = season.title
                            season_updates.get_title_name()
                            season_updates.get_last_update()
                            season_updates.get_viedo()
                            season_db = get_dict_season(season_updates)
                            season_db.title = title
                            db.session.add(season_db)
                            if season_updates.last_update > title.update_on:
                                title.update_on = season_updates.last_update
                            get_dict_series(season_updates, season_db)
                            db.session.add(title)
                            db.session.commit()


# def append_titles_to_bd():
#     with app.app_context():
#         for i in range(0, 0, -1):
#             print(i)
#             page = parsing_main(i)
#             parsing_titles_for_bd(page)


# append_titles_to_bd()


if __name__ == '__main__':
    update_titles()



