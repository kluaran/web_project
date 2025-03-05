"""Модуль для парсинга animevost и автоматического обновления
базы данных с тайтлами."""


from app_pack import app
from app_pack.web_page_parser import WebPageParser
from app_pack.data_bases import db, Titles, Seasons, Series
from app_pack.utils import get_object_by_filter


def parsing_main(id):
    """Функция для создания объектов главных страничек."""

    page = WebPageParser(f'tip/page/{id}/')
    page.get_urls_from_main()
    return page


def parsing_page(page):
    """Функция для парсинга тайтлов с главных страничек."""

    for url in page.list_urls:
        season = get_object_by_filter(Seasons, Seasons.url_animevost == url)
        season_updates = WebPageParser(url)
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