import datetime as dt
import os

import dateparser
import requests
import tzlocal
from bs4 import BeautifulSoup

from infotools.utils import read_config


def parse_text_timestamp(ts):
    """Parse timestamp, possibly humanized."""
    try:
        return dateparser.parse(ts).replace(second=0, microsecond=0)
    except:
        return dt.datetime.utcnow()


def get_or_eval(site_config, key, item):
    """Retrieve item attribute using selector, if key is
    specified in config. Otherwise, use eval expression."""
    selector_val = site_config.get(key, None)
    selector_eval = site_config.get(f"{key}_eval", None)
    res = None
    if selector_val:
        res = item.select(selector_val)
    elif selector_eval:
        res = eval(selector_eval)
    return res


def get_latest(site):
    """Scrape data from the website configured under specified key.
    param site: str key in scrapeConfig.ini"""
    curr_dir = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    config = read_config(os.path.join(curr_dir, "scrapeConfig.ini"))

    url = config[site]["url"]
    res = requests.get(url)
    soup = BeautifulSoup(res.content, "html.parser")

    items = soup.select(config[site]["items"])
    local_timezone = tzlocal.get_localzone()

    item_dicts = []

    for item in items:
        timestamp = item.select_one(config[site]["timestamp"]).text
        timestamp = parse_text_timestamp(timestamp).replace(tzinfo=local_timezone)
        headline = get_or_eval(config[site], "headline", item)[:250]
        external_id = get_or_eval(config[site], "external_id", item)

        if not external_id:
            # we need a unique ID to update items if needed
            external_id = f"{site}|{timestamp.isoformat()}|{headline[:50]}"

        item_dicts.append(
            {
                "external_id": external_id,
                "interface": config[site]["interface"],
                "origin": config[site]["source"],
                "headline": headline,
                "url": get_or_eval(config[site], "item_url", item),
                "text": get_or_eval(config[site], "text", item),
                "language": config[site]["language"],
                "timestamp": timestamp,
            }
        )

    return item_dicts
