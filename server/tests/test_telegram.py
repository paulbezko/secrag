import requests
import json
import os

# print(requests.get("https://api.telegram.org/bot7770656451:AAFxWbl8thravZhmk4OBCDkvDBb0yDrGwl4/getUpdates").text)

# requests.post(f"https://api.telegram.org/bot7770656451:AAFxWbl8thravZhmk4OBCDkvDBb0yDrGwl4/sendMessage", data={'chat_id': '-4506773539', 'text': "ass"})

# print(os.listdir(''))

with open('database/memory/filings_available.json', 'r') as file: filings = json.load(file)

print(filings)