from bs4 import BeautifulSoup
import os
import requests
import configparser
import dateparser


def read_config():
    curr_dir = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    config_file = os.path.join(curr_dir, "scrapeConfig.ini")
    config = configparser.ConfigParser()
    config.read(config_file)
    return config


def parse_human_timestamp(ts):
    """Parse timestamp out of humanized ts."""
    return dateparser.parse(ts).replace(second=0, microsecond=0)


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
    :param site: str key in scrapeConfig.ini"""
    config = read_config()
    url = config[site]["url"]
    res = requests.get(url)
    soup = BeautifulSoup(res.content, "html.parser")

    items = soup.select(config[site]["items"])
    timestamp_humanized = config[site]["timestamp_humanized"] or False

    item_dicts = []

    for item in items:
        timestamp = item.select_one(config[site]["timestamp"]).text
        if timestamp_humanized:
            timestamp = parse_human_timestamp(timestamp)
        headline = get_or_eval(config[site], "headline", item)
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
