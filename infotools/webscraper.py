"""
Use BeautifulSoup to scrape relevant websites with news pertaining to Ukraine.

Each function should return a dataframe holding the relevant information for each source, which can be
accessed by the front end.

Dataframe will also be saved to a CSV file found in /infotools/CSVs/scraped.csv
"""

import pandas as pd
from bs4 import BeautifulSoup
import requests
import re


# not necessarily for situational updates, but for news stories
def get_latest_from_nbc():
    url = 'https://www.nbcnews.com/world/russia-ukraine-news'
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'html.parser')

    items = soup.select('ul.alacarte__items', limit=8)

    item_dicts = []
    for item in items:
        text = item.select('li.alacarte__item')[0].text
        item_dicts.append({
            "interface": "website",
            "source": "liveuamap.com",
            "section": item.select('h2.unibrow'),
            "headline": item.select('h2.alacarte__headline'),
            "text": text,
            "language": "en",
            "timestamp": None,
        })

    nbc_data = pd.DataFrame(item_dicts)
    nbc_data.to_csv('infotools/CSVs/scraped.csv')

    return nbc_data


# result of this will need to be translated to english
def get_latest_from_telegraf():
    url = 'https://telegraf.com.ua/specials/voyna-na-donbasse'
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'html.parser')

    items = soup.select('div.c-card-list__main', limit=5)

    item_dicts = []
    for item in items:
        text = item.select('div.c-card-list__title')[0].text
        item_dicts.append({
            "interface": "website",
            "source": "liveuamap.com",
            "headline": None,
            "text": text,
            "language": "en",
            "timestamp": None,
        })

    telegraf_data = pd.DataFrame(item_dicts)
    telegraf_data.to_csv('infotools/CSVs/scraped.csv')

    return telegraf_data


def get_latest_from_liveuamap():
    url = 'https://liveuamap.com'
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'html.parser')

    items = soup.select('div.news-lent div.event')

    item_dicts = []
    for item in items:
        text = item.select('div.title')[0].text
        item_dicts.append({
            "interface": "website",
            "source": "liveuamap.com",
            "id": item.attrs['data-id'],
            "headline": None,
            "text": text,
            "language": "en",
            "timestamp": None,  # theoretically information is there e.g.<span class="date_add">1 hour ago</span>
        })

    liveuamap_data = pd.DataFrame(item_dicts)
    liveuamap_data.to_csv('infotools/CSVs/scraped.csv')

    return liveuamap_data
