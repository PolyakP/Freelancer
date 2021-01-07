import requests
from bs4 import BeautifulSoup
import csv
import random
import time

URL = 'https://rezka.ag/films/arthouse/'
HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
}
PATH = 'save_films.csv'


def get_html(url, params=None):
    req = requests.get(url, headers=HEADERS, params=params)
    return req


def get_pages_count(html):
    soup = BeautifulSoup(html, 'lxml')
    pagination = soup.find_all('div', class_='b-navigation')
    if pagination:
        return int([i.text.split() for i in pagination][0][-1])
    else:
        return 1


def get_url(html):
    soup = BeautifulSoup(html, 'lxml')
    film_urls = soup.find_all('div', class_='b-content__inline_item-link')
    return [film.find('a').get('href') for film in film_urls]


def get_film_url(html):
    html = get_html(URL)
    films = []
    pages_count = get_pages_count(html.text)
    for page in range(1, pages_count + 1):
        html = get_html(URL, params={'page': page})
        films.extend(get_url(html.text))
    return films


def get_info(html):
    soup = BeautifulSoup(html, 'lxml')
    info = []
    try:
        title_rus = soup.find('h1').text
    except Exception:
        title_rus = '-'
    try:
        title_eng = soup.find('div', class_='b-post__origtitle').text
    except Exception:
        title_eng = '-'
    try:
        URL_film = soup.find('div', class_='b-footer__mirror').find('a').get('href')
    except Exception:
        URL_film = '-'
    try:
        rating = soup.find('span', class_='b-post__info_rates imdb').text
    except Exception:
        rating = '-'

    try:
        director = soup.find('div', class_='persons-list-holder').text
    except Exception:
        director = '-'
    try:
        genre = soup.find('span', itemprop='genre').text
    except Exception:
        genre = '-'
    try:
        actor = soup.find_all('span', itemprop='name')
        actors = [i.text for i in actor]
    except Exception:
        actors = '-'
    try:
        time = soup.find('td', itemprop='duration').text
    except Exception:
        time = '-'
    try:
        description = soup.find('div', class_='b-post__description_text').text
    except Exception:
        description = '-'
    info.append({
        'title_rus': title_rus,
        'title_eng': title_eng,
        'URL_film': URL_film,
        'rating': rating,
        'director': director,
        'genre': genre,
        'actors': actors,
        'time': time,
        'description': description
    })
    return info


def save_file(items, path):
    with open(path, 'w', newline='', encoding='UTF-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['title_rus', 'title_eng', 'URL_film', 'rating', 'director', 'genre', 'actors', 'time', 'description'])
        for item in items:
            writer.writerow([item['title_rus'], item['title_eng'], item['URL_film'], item['rating'], item['director'],
                             item['genre'], item['actors'], item['time'], item['description']])


def parse():
    URL = input('put_URL: ')
    URL = URL.strip()
    html = get_html(URL)
    if html.status_code == 200:
        films = []
        count_films = len(get_film_url(html.text))
        for film in range(1, count_films + 1):
            print(f'pars {film} film from {count_films}...')
            html = get_html(get_film_url(html)[int(film)-1])
            films.extend(get_info(html.text))
            save_file(films, path=PATH)
            time.sleep(random.randrange(2, 4))
        print(f'get {len(films)} films')
    else:
        print('error')


if __name__ == '__main__':
    parse()