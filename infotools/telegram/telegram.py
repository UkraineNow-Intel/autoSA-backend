"""
Requires TELEGRAM_API_ID and TELEGRAM_API_HASH setting.
"""
import os.path

import pytz
from telethon import functions, types
from telethon.sync import TelegramClient

from infotools.utils import read_config

MESSAGES_PER_REQUEST = 100


def search_recent_messages(
    settings,
    start_time=None,
    end_time=None,
):
    """Yield Messages from Telegram for accounts specified in config.ini

    Parameters
    ----------
    settings: dict
        Dict containing TELEGRAM_API_ID and TELEGRAM_API_HASH
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
    if len(telegram_accounts) > 0:
        # scraping messages from specific accounts
        for account in telegram_accounts:
            for result in search_telegram_messages(
                settings, chat_name=account, start_time=start_time, end_time=end_time
            ):
                yield result
    else:
        # global search
        for result in search_telegram_messages(
            settings, chat_name=None, start_time=start_time, end_time=end_time
        ):
            yield result


def _create_client(settings) -> TelegramClient:
    telegram_api_id = settings["TELEGRAM_API_ID"]
    telegram_api_hash = settings["TELEGRAM_API_HASH"]
    return TelegramClient("uanow", telegram_api_id, telegram_api_hash)


def _format_message(msg, *, chats=None, users=None):
    """Create result dictionaries from messages.
    Uses dictionaries of  channel/user ids to names for lookup.
    """
    if hasattr(msg.peer_id, "channel_id"):
        origin = chats[msg.peer_id.channel_id]
    else:
        origin = users[msg.peer_id.user_id]
    return dict(
        external_id=f"{origin}:{msg.id}",
        timestamp=msg.date,
        text=msg.message,
        url=f"https://t.me/{origin}/{msg.id}",
        interface="telegram",
        language="en",  # TODO: does Telegram have this attribute?
        origin=origin,
        locations=[],
    )


def search_telegram_messages(
    settings, *, chat_name=None, search_term=None, start_time=None, end_time=None
):
    """Get Messages from Telegram, will block until async calls complete.

    Parameters
    ----------
    chat_name: str, optional
        Name of the chat to search in.
    search_term: str, optional
        Term to search, can be None as well.
    start_time: datetime, optional
        Earliest date of potential matched messages
    end_time: datetime, optional
        Last date of potential matched messages

    Yields
    -------
    result: dict
        Matched telegram message.
    """
    # Offset rate are needed for pagination/in case more than 100 messages
    # should be retrieved
    # offset rate is for global search
    # offset id for chat/peer-specific search
    # https://core.telegram.org/api/offsets
    # https://core.telegram.org/constructor/messages.messagesSlice
    offset_id = 0
    offset_rate = 0

    if start_time and not start_time.tzinfo:
        start_time = start_time.replace(tzinfo=pytz.UTC)

    if end_time and not end_time.tzinfo:
        end_time = end_time.replace(tzinfo=pytz.UTC)

    with _create_client(settings) as client:
        while True:
            if chat_name:
                request = functions.messages.SearchRequest(
                    q=search_term or "",
                    filter=types.InputMessagesFilterEmpty(),
                    peer=chat_name,
                    offset_id=offset_id,
                    add_offset=0,
                    min_date=start_time,
                    max_date=end_time,
                    limit=MESSAGES_PER_REQUEST,
                    max_id=0,
                    min_id=0,
                    hash=0,
                )
                response = client(request)
            else:
                request = functions.messages.SearchGlobalRequest(
                    q=search_term or "",
                    filter=types.InputMessagesFilterEmpty(),
                    offset_id=0,
                    min_date=start_time,
                    max_date=end_time,
                    offset_peer=types.InputPeerEmpty(),
                    offset_rate=offset_rate,
                    limit=MESSAGES_PER_REQUEST,
                )
                response = client(request)
                offset_rate = response.next_rate

            chats = {c.id: c.username for c in response.chats}
            users = {c.id: c.username for c in response.users}

            # we did a search, and there's no messages, time to exit.
            if len(response.messages) == 0:
                break

            for msg in response.messages:
                offset_id = msg.id
                yield _format_message(msg, chats=chats, users=users)

            # we did a global search, and there's no next page, time to exit.
            if not chat_name and offset_rate is None:
                break


def _read_config():
    curr_dir = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    config = read_config(os.path.join(curr_dir, "config.ini"))
    return config.get("main", "telegram_accounts").strip().split("\n")


if __name__ == "__main__":
    import datetime as dt
    from pprint import pprint

    from website.settings.base import TELEGRAM_API_HASH, TELEGRAM_API_ID

    def _print_results(results, description):
        total = 0
        for res in results:
            # print(f"{res['external_id']}: {res['timestamp']}")
            pprint(res)
            total += 1
            if total >= 1000:
                print("Too many messages. Exiting at 1000.")
                break
        print("-" * 40)
        print(f"Total with {description}: {total}")
        print("-" * 40)

    telegram_settings = {
        "TELEGRAM_API_ID": TELEGRAM_API_ID,
        "TELEGRAM_API_HASH": TELEGRAM_API_HASH,
    }
    start_time = dt.datetime(year=2022, month=4, day=29, hour=0)
    end_time = dt.datetime(year=2022, month=4, day=29, hour=1)

    print(f"Searching for {start_time} - {end_time}")

    def test_with_channel_term():
        results = search_telegram_messages(
            telegram_settings,
            chat_name="t.me/ukrainearmyforce",
            search_term="Харків",
        )
        _print_results(results, "channel with search term")

    def test_with_channel_term_dates():
        results = search_telegram_messages(
            telegram_settings,
            chat_name="t.me/ukrainearmyforce",
            search_term="Харків",
            start_time=start_time,
            end_time=end_time,
        )
        _print_results(results, "channel with search term and dates")

    def test_with_channel_dates():
        results = search_telegram_messages(
            telegram_settings,
            chat_name="t.me/ukrainearmyforce",
            start_time=start_time,
            end_time=end_time,
        )
        _print_results(results, "channel without search term")

    def test_configured_channels_dates():
        results = list(
            search_recent_messages(
                telegram_settings,
                start_time=start_time,
                end_time=end_time,
            )
        )
        _print_results(results, "chats from config without search term")

    def test_global_dates():
        results = search_telegram_messages(
            telegram_settings,
            start_time=start_time,
            end_time=end_time,
        )
        _print_results(results, "global without search term")

    # test_with_channel_dates()
    # test_global_dates()
    test_configured_channels_dates()
    # test_with_channel_term_dates()
    # test_with_channel_term()
