"""Модуль с классом для парсинга animevost."""


from datetime import datetime
from bs4 import BeautifulSoup
import requests


class WebPageParser():
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
