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


def get_latest_from_nbc():
    global content
    url = 'https://www.nbcnews.com/world/russia-ukraine-news'
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'html.parser')

    headlines = soup.findChildren('h2', text=re.compile(r'Ukraine'), limit=8)

    for i in range(len(headlines)):
        content = headlines[i].text

    nbc_data = pd.DataFrame(headlines)
    nbc_data.to_csv('infotools/CSVs/scraped.csv')

    return nbc_data


# result of this will need to be translated to english
def get_latest_from_telegraf():
    global content
    url = 'https://telegraf.com.ua/specials/voyna-na-donbasse'
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'html.parser')

    headlines = soup.find_all('div', {'class': 'c-card-list__title'}, limit=5)

    for i in range(len(headlines)):
        content = headlines[i].text

    telegraf_data = pd.DataFrame(headlines)
    telegraf_data.to_csv('infotools/CSVs/scraped.csv')

    return telegraf_data


def get_from_liveuamap():
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
