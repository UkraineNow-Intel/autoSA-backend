import datetime
from bs4 import BeautifulSoup
import requests
import configparser


def get_latest(site):

    config = configparser.ConfigParser()
    config.read("scrapeConfig.ini")

    url = config[site]["url"]
    res = requests.get(url)
    soup = BeautifulSoup(res.content, "html.parser")

    items = soup.select(config[site]["items"])

    item_dicts = []

    for item in items:
        text = item.select(config[site]["text"])[0].text
        item_dicts.append(
            {
                "interface": config[site]["interface"],
                "source": config[site]["source"],
                "section": item.select(config[site]["section"]),
                "headline": item.select(config[site]["headline"]),
                "text": text,
                "language": config[site]["language"],
                "timestamp": item.select(config[site]["timestamp"]),
            }
        )

        return item_dicts
