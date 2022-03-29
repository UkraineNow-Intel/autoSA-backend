"""
Use BeautifulSoup to scrape relevant websites with news pertaining to Ukraine
"""

import pandas as pd
from bs4 import BeautifulSoup
import requests
import re


#
def get_from_nbc():
    url = 'https://www.nbcnews.com/world/russia-ukraine-news'
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'html.parser')

    headlines = soup.findChildren('h2', text=re.compile(r'Ukraine'), limit=8)

    for i in range(len(headlines)):
        print(headlines[i].text)

    nbc_data = pd.DataFrame(headlines)
    nbc_data.to_csv('infotools/CSVs/scraped.csv')


get_from_nbc()
