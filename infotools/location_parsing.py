import geopy
import numpy as np
import spacy
from geopy.extra.rate_limiter import RateLimiter


def extract_locations_for_dataframe(dataframe):
    """Extract location names and geocodes from the texts in the dataframe.

    Parameters
    ----------
    dataframe: pandas DataFrame
        Dataframe with `text` and `language` columns

    Returns
    -------
    locations: list of list dict
        List of detected locations, for each row a list of dicts with names and geocodes.
    """

    return extract_locations(np.array(dataframe.text), np.array(dataframe.language))


def extract_locations(texts, languages):
    """Extract location names and geocodes from the texts.

    Parameters
    ----------
    texts: list of str
        List of texts to extract locations from.
    languages: list of str
        Language codes (e.g., ua/en/ru for each text.

    Returns
    -------
    locations: list of list dict
        List of detected locations, for each text a list of dicts
        with names and geocodes.
    """
    location_names_per_text = extract_location_names(texts, languages)
    geocodes_per_text = extract_geocodes(location_names_per_text)

    locations = []
    for location_names, geocodes in zip(
        location_names_per_text,
        geocodes_per_text,
    ):
        this_text_locations = [
            {"name": l_name, "geocode": l_geocode}
            for l_name, l_geocode in zip(location_names, geocodes)
        ]
        locations.append(this_text_locations)
    return locations


def extract_location_names(texts, languages):
    """Extract location names the texts.

    Parameters
    ----------
    texts: list of str
        List of texts to extract locations from.
    languages: list of str
        Language codes (e.g., ua/en/ru for each text.

    Returns
    -------
    location_names_per_text: list of list of str
        List of detected location names, for each text a list of names.
    """
    location_names_per_text = []
    spacy_en_model = spacy.load("en_core_web_sm")
    # At the moment no proper language model for ukrainian,
    # and russian language model seems to occasionally work for location
    # detection in ukrainian text?
    spacy_ru_model = spacy.load("ru_core_news_sm")  # some false positives with lg
    for text, language in zip(
        texts,
        languages,
    ):
        spacy_model = {
            "en": spacy_en_model,
            "ru": spacy_ru_model,
            "ua": spacy_ru_model,  # no proper ua model exists in spacy
        }[language]
        location_names = extract_location_strings(spacy_model, text)
        location_names_per_text.append(location_names)
    return location_names_per_text


def extract_location_strings(spacy_model, text):
    """Extract strings that contain locations from the text using the given spacy model.

    Parameters
    ----------
    spacy_model:
        Spacy model of a given language.
    text: str
        Text to extract locations from.

    Returns
    -------
    location_strings: list of str
        List of detected location names.
    """

    doc = spacy_model(text)
    location_strings = [str(e) for e in doc.ents if e.label_ in ("LOC", "GPE")]
    return location_strings


def extract_geocodes(location_names_per_text):
    """Extract geocodes for location names.

    Parameters
    ----------
    location_names_per_text: list of list of str
        List of detected location names, for each previously parsed text a list of names.

    Returns
    -------
    geocodes_per_text: list of list of geocodes
        List of list of geocodes, for each location name list a
        corresponding list of geocodes.
    """
    locator = geopy.geocoders.Nominatim(user_agent="mygeocoder")
    geocode = RateLimiter(locator.geocode, min_delay_seconds=0.2)
    geocodes_per_text = []
    for location_names in location_names_per_text:
        geocodes = [geocode(l_name) for l_name in location_names]
        geocodes_per_text.append(geocodes)
    return geocodes_per_text
