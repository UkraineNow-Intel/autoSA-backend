from decouple import config
from telethon.sync import TelegramClient
from telethon import functions, types
from api.models import INTERFACE_TELEGRAM, LANGUAGE_EN

TELEGRAM_API_ID = config("TELEGRAM_API_ID", cast=int)
TELEGRAM_API_HASH = config("TELEGRAM_API_HASH")


class TelegramSearch:
    def __init__(self, api_id, api_hash):
        self.api_id = api_id
        self.api_hash = api_hash

    def search_telegram_messages(
        self, chat_name=None, search_term=None, min_date=None, max_date=None
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

        Returns
        -------
        results: list of dicts
            Matched telegram messages.
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

            api_responses = []
            while len(api_responses) == 0 or (
                len(result.messages) == n_messages_per_request
            ):
                if chat_name is None:
                    result = client(
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
                    result = client(
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
                    if len(result.messages) > 0:
                        offset_id = result.messages[-1].id
                api_responses.append(result)
        results = []
        for result in api_responses:
            # Create dictionary of  channel/user ids to names for lookup
            ch_ids_to_name = {c.id: c.username for c in result.chats}
            user_ids_to_name = {u.id: u.username for u in result.users}
            for msg in result.messages:
                if hasattr(msg.peer_id, "channel_id"):
                    origin = ch_ids_to_name[msg.peer_id.channel_id]
                else:
                    origin = user_ids_to_name[msg.peer_id.user_id]
                results.append(
                    dict(
                        timestamp=msg.date,
                        text=msg.message,
                        interface=INTERFACE_TELEGRAM,
                        language=LANGUAGE_EN,
                        origin=origin,
                    )
                )
        return results


if __name__ == "__main__":
    import datetime as dt
    from backports import zoneinfo

    TZ_UTC = zoneinfo.ZoneInfo("UTC")
    t = TelegramSearch(TELEGRAM_API_ID, TELEGRAM_API_HASH)

    print("No search term or chat name")
    result = t.search_telegram_messages(
        chat_name=None,
        search_term=None,
        min_date=dt.datetime(2022, 4, 11, 0, 0, 0, tzinfo=TZ_UTC),
        max_date=dt.datetime(2022, 4, 12, 0, 0, 0, tzinfo=TZ_UTC),
    )
    print(len(result))
    print(result)

    print("No min max date term")
    result = t.search_telegram_messages(
        chat_name="t.me/ukrainearmyforce",
        search_term="Харків",
    )
    print(len(result))
    print(result)

    print("No search term")
    result = t.search_telegram_messages(
        chat_name="t.me/ukrainearmyforce",
        search_term="Харків",
        min_date=dt.datetime(2022, 4, 11, 0, 0, 0, tzinfo=TZ_UTC),
        max_date=dt.datetime(2022, 4, 12, 0, 0, 0, tzinfo=TZ_UTC),
    )
    print(len(result))
    print(result)

    print("Everything given")
    result = t.search_telegram_messages(
        chat_name="t.me/ukrainearmyforce",
        search_term=None,
        min_date=dt.datetime(2022, 4, 11, 0, 0, 0, tzinfo=TZ_UTC),
        max_date=dt.datetime(2022, 4, 12, 0, 0, 0, tzinfo=TZ_UTC),
    )
    print("No search term")
    print(len(result))
    print(result)
