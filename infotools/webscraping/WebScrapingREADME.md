# Web Scraping
Our web scraping tool scrapes sites with BeautifulSoup4 to retrieve constant live updates.

### get_latest()
Takes a str as an argument, the str represents the desired site to be scraped. Returns a dict containing site attributes.
Site attibutes are as follows:
- Interface: source type
- Source: website being scraped
- Section: title of each section
- Headline: article headline
- Text: article contents
- Language: original language website is written in
- Timestamp: time at which the source was accessed

### Config File
The config file holds multiple site profiles formatted like this:

```
[site label]
url = https://example.com/
items = html selector
text = html selector
interface = website
source = site title
section = html selector
headline = html selector
language = en
timestamp = None
```
Timestamp should be filled in as None in the config file by default.

Not all of these attributes may be present in every site! If one is missing, fill in NA in the config file.

### Limitations
- Currently, location data is not associated with articles
- Timestamps is set for when the site is accessed, getting article publish date needs some more attention.
- Accessing attributes is very inconsistent