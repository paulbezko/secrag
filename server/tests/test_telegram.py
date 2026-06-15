import requests
import json
import os

_BOT = os.getenv("TELEGRAM_BOT_KEY")
_CHAT = os.getenv("TELEGRAM_CHAT_ID")
# print(requests.get(f"https://api.telegram.org/bot{_BOT}/getUpdates").text)

# requests.post(f"https://api.telegram.org/bot{_BOT}/sendMessage", data={'chat_id': _CHAT, 'text': "test"})

# print(os.listdir(''))

with open('database/memory/filings_available.json', 'r') as file: filings = json.load(file)

print(filings)