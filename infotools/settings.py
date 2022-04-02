import os

# Tweepy Settings

TWITTER_API_KEY = os.environ.get("TWITTER_API_KEY")

TWITTER_API_SECRET_KEY = os.environ.get("TWITTER_API_SECRET_KEY")

TWITTER_BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN")

TWITTER_SOURCE_ACCOUNTS = [
    "phildstewart",
    "DefenceHQ",
    "DanLamothe",
    "ukr_satflash",
    "JominiW",
    "WarintheFuture",
    "anders_aslund",
    "The_IntelHub",
    "JohnBrennan",
    "IntelDoge",
    "bellingcat",
    "ZelenskyyUa",
    "DmytroKuleba",
    "NATOinUkraine",
    "DefenceU",
    "PowerOutage_com",
    "War_Mapper",
    "mschwirtz",
    "GeneralStaffUA",
    "DFRLab",
    "KofmanMichael",
    "TheStudyofWar",
    "Liveuamap",
    "IAPonomarenko",
    "SOFNewsUpdate",
    "sbreakintl",
    "NewUkraineNews",
    "KyivIndependent",
    "ChristopherJM",
    "christogrozev",
    "MarQs__",
    "Now_in_Ukraine",
    "sentdefender",
    "JoeBiden",
    "CNN",
    "RFERL",
    "ukr_satflash",
    "PowerOutage_us",
    "CAT_UXO"
]


# Optional adding of a locals.py settings, for development purposes only.
# In production, environment variables should be used.
try:
    from .locals import *
except ImportError:
    pass
