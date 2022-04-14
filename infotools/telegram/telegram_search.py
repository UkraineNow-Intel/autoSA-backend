from decouple import config
from telethon.sync import TelegramClient
from telethon import functions, types
from api.models import INTERFACE_TELEGRAM

TELEGRAM_API_ID = config("TELEGRAM_API_ID", cast=int)
TELEGRAM_API_HASH = config("TELEGRAM_API_HASH")


def search_telegram_messages(chat_name, search_term, min_date, max_date):
    """Get Messages from Telegram, will block until async calls complete.

    Parameters
    ----------
    chat_name: str
        Name of the chat to search in.
    search_term: str
        Term to search, can be None as well.
    start_date: datetime
        Earliest date of potential matched messages
    end_date: datetime
        Last date of potential matched messages

    Returns
    -------
    results: list of dicts
        Matched telegram messages.
    """

    with TelegramClient("uanow", TELEGRAM_API_ID, TELEGRAM_API_HASH) as client:
        result = client(
            functions.messages.SearchRequest(
                peer=chat_name,
                q=search_term,
                filter=types.InputMessagesFilterEmpty(),
                min_date=min_date,
                max_date=max_date,
                offset_id=0,
                add_offset=0,
                limit=100,
                max_id=0,
                min_id=0,
                hash=0,
                from_id=None,
            )
        )

    results = []
    for msg in result.messages:
        results.append(
            dict(
                timestamp=msg.date,
                text=msg.message,
                pinned=msg.pinned,
                interface=INTERFACE_TELEGRAM,
            )
        )
    return results


if __name__ == "__main__":
    import datetime as dt
    from backports import zoneinfo

    TZ_UTC = zoneinfo.ZoneInfo("UTC")
    result = search_telegram_messages(
        chat_name="t.me/ukrainearmyforce",
        search_term="Харків",
        min_date=dt.datetime(2022, 4, 11, 0, 0, 0, tzinfo=TZ_UTC),
        max_date=dt.datetime(2022, 4, 12, 0, 0, 0, tzinfo=TZ_UTC),
    )
    print(result)
