import requests

print(requests.get("https://api.telegram.org/bot7770656451:AAFxWbl8thravZhmk4OBCDkvDBb0yDrGwl4/getUpdates").text)

# requests.post(f"https://api.telegram.org/bot7770656451:AAFxWbl8thravZhmk4OBCDkvDBb0yDrGwl4/sendMessage", data={'chat_id': '-4506773539', 'text': "ass"})