import os.path

from decouple import config
from telethon import functions, types
from telethon.sync import TelegramClient

from api.models import INTERFACE_TELEGRAM, LANGUAGE_EN
from infotools.utils import read_config

TELEGRAM_API_ID = config("TELEGRAM_API_ID", cast=int)
TELEGRAM_API_HASH = config("TELEGRAM_API_HASH")


def search_recent_telegram_messages(
    start_time=None,
    end_time=None,
):
    """Yield Messages from Telegram for accounts specified in config.ini

    Parameters
    ----------
    start_date: datetime, optional
        Earliest date of potential matched messages
    end_date: datetime, optional
        Last date of potential matched messages

    Yields
    ------
    results: dict
        Matched telegram message.
    """

    telegram_accounts = _read_config()
    for account in telegram_accounts:
        results = search_telegram_messages(
            chat_name=account, min_date=start_time, max_date=end_time
        )
        for result in results:
            yield result


def search_telegram_messages(
    chat_name=None, search_term=None, min_date=None, max_date=None
):
    """Get Messages from Telegram, will block until async calls complete.

    Parameters
    ----------
    chat_name: str, optional
        Name of the chat to search in.
    search_term: str, optional
        Term to search, can be None as well.
    start_date: datetime, optional
        Earliest date of potential matched messages
    end_date: datetime, optional
        Last date of potential matched messages

    Yields
    -------
    result: dict
        Matched telegram message.
    """
    if search_term is None:
        search_term = ""
    with TelegramClient("uanow", TELEGRAM_API_ID, TELEGRAM_API_HASH) as client:
        n_messages_per_request = 100  # seems this is max number already
        # Offset rate are needed for pagination/in case more than 100 messages
        # should be retrieved
        # offset rate is for global search
        # offset id for chat/peer-specific search
        # https://core.telegram.org/api/offsets
        # https://core.telegram.org/constructor/messages.messagesSlice
        offset_rate = 0
        offset_id = 0

        received_max_nr_of_messages = True
        while received_max_nr_of_messages:
            if chat_name is None:
                api_response = client(
                    functions.messages.SearchGlobalRequest(
                        q=search_term,
                        filter=types.InputMessagesFilterEmpty(),
                        min_date=min_date,
                        max_date=max_date,
                        offset_id=0,  # offset_rate is used here
                        offset_peer=types.InputPeerEmpty(),
                        offset_rate=offset_rate,
                        limit=n_messages_per_request,
                    )
                )
                offset_rate = result.next_rate
            else:
                api_response = client(
                    functions.messages.SearchRequest(
                        peer=chat_name,
                        q=search_term,
                        filter=types.InputMessagesFilterEmpty(),
                        min_date=min_date,
                        max_date=max_date,
                        offset_id=offset_id,
                        add_offset=0,
                        limit=n_messages_per_request,
                        max_id=0,
                        min_id=0,
                        hash=0,
                        from_id=None,
                    )
                )
                if len(api_response.messages) > 0:
                    offset_id = api_response.messages[-1].id

            ## Iterate through messages and create result dictionaries
            # Create dictionary of  channel/user ids to names for lookup
            ch_ids_to_name = {c.id: c.username for c in api_response.chats}
            user_ids_to_name = {u.id: u.username for u in api_response.users}
            for msg in api_response.messages:
                if hasattr(msg.peer_id, "channel_id"):
                    origin = ch_ids_to_name[msg.peer_id.channel_id]
                else:
                    origin = user_ids_to_name[msg.peer_id.user_id]
                result = dict(
                    timestamp=msg.date,
                    text=msg.message,
                    interface=INTERFACE_TELEGRAM,
                    language=LANGUAGE_EN,
                    origin=origin,
                )
                yield result

            # Determine whether we are done.
            received_max_nr_of_messages = (
                len(api_response.messages) == n_messages_per_request
            )


def _read_config():
    curr_dir = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    config = read_config(os.path.join(curr_dir, "config.ini"))
    return config.get("main", "telegram_accounts").strip().split("\n")


if __name__ == "__main__":
    import datetime as dt

    from backports import zoneinfo

    TZ_UTC = zoneinfo.ZoneInfo("UTC")

    result = search_recent_telegram_messages(
        start_time=dt.datetime(2022, 4, 11, 23, 00, 0, tzinfo=TZ_UTC),
        end_time=dt.datetime(2022, 4, 12, 0, 0, 0, tzinfo=TZ_UTC),
    )
    result = list(result)
    print(len(result))
    print(result)

    print("No search term or chat name")
    result = search_telegram_messages(
        chat_name=None,
        search_term=None,
        min_date=dt.datetime(2022, 4, 11, 23, 50, 0, tzinfo=TZ_UTC),
        max_date=dt.datetime(2022, 4, 12, 0, 0, 0, tzinfo=TZ_UTC),
    )
    result = list(result)
    print(len(result))
    print(result)

    print("No min max date")
    result = search_telegram_messages(
        chat_name="t.me/ukrainearmyforce",
        search_term="Харків",
    )
    result = list(result)
    print(len(result))
    print(result)

    print("No search term")
    result = search_telegram_messages(
        chat_name="t.me/ukrainearmyforce",
        search_term=None,
        min_date=dt.datetime(2022, 4, 11, 0, 0, 0, tzinfo=TZ_UTC),
        max_date=dt.datetime(2022, 4, 12, 0, 0, 0, tzinfo=TZ_UTC),
    )
    result = list(result)
    print(len(result))
    print(result)

    print("Everything given")
    result = search_telegram_messages(
        chat_name="t.me/ukrainearmyforce",
        search_term="Харків",
        min_date=dt.datetime(2022, 4, 11, 0, 0, 0, tzinfo=TZ_UTC),
        max_date=dt.datetime(2022, 4, 12, 0, 0, 0, tzinfo=TZ_UTC),
    )
    result = list(result)
    print(len(result))
    print(result)
