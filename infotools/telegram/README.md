### Telegram search

This uses Telegram API through Telethon to retrieve telegram messages:

https://tl.telethon.dev/methods/messages/search.html

At this point, we simply retrieve messages from specified accounts. The list of accounts 
is configured in [config.ini](config.ini).

The following variables should be present in `.env`:

```ini
TELEGRAM_API_ID=<your api id>
TELEGRAM_API_HASH=<your api hash>
# has to be absolute path
TELEGRAM_MEDIA_PATH=/absolute/path/for/downloading/images
# can be relative path under website
TELEGRAM_MEDIA_PATH_URL=/static/telegram
```


Before calling the Django `/api/refresh` endpoint, you need to initialize the client session. Unfortunately, this has to be done interactively.

Run the Telegram script and answer the prompts to create a session file: 

```shell
PYTHONPATH=. python /Users/irinatruong/src/autoSA-backend/infotools/telegram/telegram.py
```
