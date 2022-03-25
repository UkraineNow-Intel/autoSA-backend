from datetime import datetime
import geopy
import numpy as np
import pandas as pd
from infotools.location_parsing import extract_locations_for_dataframe


def test_extract_locations_for_dataframe():
    dicts = [
        {
            "interface": "website",
            "source": "liveuamap.com",
            "id": None,
            "headline": None,
            "text": "Clashes and artillery shelling in Trostyanets, fires burning",
            "language": "en",
            "timestamp": int(
                round(
                    datetime(
                        2022,
                        3,
                        22,
                    ).timestamp()
                )
            ),
        },
        {
            "interface": "website",
            "source": "liveuamap.com",
            "id": None,
            "headline": None,
            "text": "Emergency situation regime introduced in two villages of the Bilhorod region due to a shell explosion",
            "language": "en",
            "timestamp": int(round(datetime(2022, 3, 23, 15).timestamp())),
        },
        {
            "interface": "website",
            "source": "liveuamap.com",
            "id": None,
            "headline": None,
            # Just for ukrainian example, actually text is there in english as well
            "text": "Російські військові обстріляли з артилерії одне з харчових підприємств у Чернігові. Стався витік аміаку, проте його концентрація в межах допустимої норми, розповів Суспільному голова ОВА Чаус",
            "language": "ua",
            "timestamp": int(
                round(
                    datetime(
                        2022,
                        3,
                        23,
                    ).timestamp()
                )
            ),
        },
        {
            "interface": "website",
            "source": "maphub.net",
            "id": None,
            "headline": None,
            "text": "Another video with a captured T-80U and two T-80BV tanks.",
            "language": "en",
            "timestamp": int(
                round(
                    datetime(
                        2022,
                        3,
                        24,
                    ).timestamp()
                )
            ),
        },
        {
            "interface": "website",
            "source": "somenewssite.net",
            "id": None,
            "headline": None,
            # Russian example from news
            "text": "В столице Болгарии Софии прошло массовое шествие в поддержку Украины.",
            "language": "ru",
            "timestamp": int(
                round(
                    datetime(
                        2022,
                        3,
                        25,
                    ).timestamp()
                )
            ),
        },
    ]

    df = pd.DataFrame(dicts)
    result = extract_locations_for_dataframe(df)

    expected = [
        [
            {
                "name": "Trostyanets",
                "geocode": geopy.Location(
                    "Trostineț-Тростянець-Тростянец, Подільський район, Одеська область, 67910, Україна",
                    (47.6054743, 29.259883, 0.0),
                    {},
                ),
            }
        ],
        [
            {
                "name": "Bilhorod",
                "geocode": geopy.Location(
                    "Білгород-Дністровський, Білгород-Дністровська міська громада, Білгород-Дністровський район, Одеська область, 67700-67719, Україна",
                    (46.1909823, 30.345784, 0.0),
                    {},
                ),
            }
        ],
        [
            {
                "name": "Чернігові",
                "geocode": geopy.Location(
                    "Управління Державної казначейської служби України у місті Чернігові, 9, Київська вулиця, Деснянський район, Чернігів, Чернігівська міська громада, Чернігівський район, Чернігівська область, 14000-14499, Україна",
                    (51.498392100000004, 31.291385200000008, 0.0),
                    {},
                ),
            }
        ],
        [],
        [
            {
                "name": "Болгарии",
                "geocode": geopy.Location(
                    "Бългaрия", (42.6073975, 25.4856617, 0.0), {}
                ),
            },
            {
                "name": "Софии",
                "geocode": geopy.Location(
                    "София, Столична, София-град, Бългaрия",
                    (42.6978634, 23.3221789, 0.0),
                    {},
                ),
            },
            # This is actually an error leading to this https://pl.wikipedia.org/wiki/Ukraina_(Sitnica)
            # instead of ukraine
            {
                "name": "Украины",
                "geocode": geopy.Location(
                    "Ukraina, Sitnica, gmina Biecz, powiat gorlicki, województwo małopolskie, 38-323, Polska",
                    (49.7647222, 21.1288889, 0.0),
                    {},
                ),
            },
        ],
    ]
    print(result[-1])
    assert len(result) == len(expected)
    for expected_list, actual_list in zip(expected, result):
        assert len(expected_list) == len(actual_list)
        for expected_loc, actual_loc in zip(expected_list, actual_list):
            assert expected_loc["name"] == actual_loc["name"]
            assert expected_loc["geocode"].address == actual_loc["geocode"].address
            assert np.allclose(
                list(expected_loc["geocode"].point), list(actual_loc["geocode"].point)
            )
