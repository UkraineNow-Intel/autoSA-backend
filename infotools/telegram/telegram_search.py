import datetime as dt
from backports import zoneinfo
from telethon.sync import TelegramClient
from telethon import functions, types
import configparser

TZ_UTC = zoneinfo.ZoneInfo("UTC")


def main():
    # channel = await client.get_input_entity("t.me/ukrainearmyforce")
    # print(channel.stringify())

    config = configparser.ConfigParser()
    config.read("telegramConfig.ini")

    api_id = config["Telegram"]["api_id"]
    api_hash = config["Telegram"]["api_hash"]

    api_id = int(api_id)
    api_hash = str(api_hash)

    result = None
    with TelegramClient("uanow", api_id, api_hash) as client:
        result = client(
            functions.messages.SearchRequest(
                peer="t.me/ukrainearmyforce",
                q="Харків",
                filter=types.InputMessagesFilterEmpty(),
                min_date=dt.datetime(2022, 4, 11, 0, 0, 0, tzinfo=TZ_UTC),
                max_date=dt.datetime(2022, 4, 12, 0, 0, 0, tzinfo=TZ_UTC),
                offset_id=0,
                add_offset=0,
                limit=100,
                max_id=0,
                min_id=0,
                hash=0,
                from_id=None,
            )
        )
        print(result.stringify())


if __name__ == "__main__":
    main()


# def get_messages_sync(searchterm, chat_name, start_date, end_date):
#     """Get Messages from Telegram, will block until async calls complete.
#
#     Parameters
#     ----------
#     searchterm: str
#         Term to search.
#     chat_name: str, optional
#         Name of the chat to search in, can be None as well for global search.
#     start_date: datetime, optional
#         Earliest date of potential matched messages
#     end_date: datetime, optional
#         Last date of potential matched messages
#
#     Returns
#     -------
#     messages: Telethon messages
#         Matched messages.
#     """
#
#     loop = asyncio.get_event_loop()
#     messages = loop.run_until_complete(
#         get_messages_async(searchterm, chat_name, start_date, end_date)
#     )
#     return messages
#
#
# async def get_messages_async(searchterm, chat_name, start_date, end_date):
#     """Get Messages from Telegram, async version.
#
#     Parameters
#     ----------
#     searchterm: str
#         Term to search.
#     chat_name: str, optional
#         Name of the chat to search in, can be None as well for global search.
#     start_date: datetime, optional
#         Earliest date of potential matched messages
#     end_date: datetime, optional
#         Last date of potential matched messages
#
#     Returns
#     -------
#     messages: Telethon messages
#         Matched messages.
#     """
#     # reading config
#     config = configparser.ConfigParser()
#     config.read("config.ini")
#
#     # setting values
#     api_id = config["Telegram"]["api_id"]
#     api_hash = config["Telegram"]["api_hash"]
#
#     api_hash = str(api_hash)
#     api_id = int(api_id)
#     client = TelegramClient("session_id", api_id=api_id, api_hash=api_hash)
#     async with client:
#         # Client needs to see the chat we want to search in,
#         # here we try via get_dialogs
#         dialogs = await client.get_dialogs()
#         messages = await get_messages_from_client(
#             client, searchterm, chat_name, start_date, end_date
#         )
#     return messages
#
#
# async def get_messages_from_client(client, searchterm, chat_name, start_date, end_date):
#     """Get Messages from Telegram given the client.
#
#     Parameters
#     ----------
#     client: Telethon client
#     searchterm: str
#         Term to search.
#     chat_name: str, optional
#         Name of the chat to search in, can be None as well for global search.
#     start_date: datetime, optional
#         Earliest date of potential matched messages
#     end_date: datetime, optional
#         Last date of potential matched messages
#
#     Returns
#     -------
#     messages: Telethon messages
#         Matched messages.
#     """
#     # We loop through messages until we reach the start date
#     # or until there are no more matching messages
#     start_date_reached = False
#     messages = []
#     async with client:
#         # 20 is the limit on how many messages to fetch at once.
#         # Remove or change for more.
#         # Not sure if this extra buffering is even necessary
#         n_buffer_messages = 20
#         # In each iteration we go further back in time by setting end_date to date of last returned message
#         # (messages are returned from newest to oldest message)
#         while not start_date_reached:
#             this_messages = []
#             async for msg in client.iter_messages(
#                 chat_name, n_buffer_messages, search=searchterm, offset_date=end_date
#             ):
#                 if start_date is not None:
#                     start_date_reached = msg.date < start_date.replace(
#                         tzinfo=msg.date.tzinfo
#                     )
#                 if start_date_reached:
#                     break
#                 this_messages.append(msg)
#             if len(this_messages) > 0:
#                 end_date = msg.date
#             start_date_reached = start_date_reached or (len(this_messages) == 0)
#             messages.extend(this_messages)
#     return messages
#
#
# if __name__ == "__main__":
#     chat_name = "Ukraine NOW [English]"  # UkraineNow English public group
#     searchterm = "mykolaiv"
#     end_date = datetime(2022, 4, 8)
#     start_date = datetime(2022, 3, 20)
#     messages = get_messages_sync(searchterm, chat_name, start_date, end_date)
#     for msg in messages:
#         print(msg.date)
#         if msg.text:
#             print(msg.text)
#             print("\n")
