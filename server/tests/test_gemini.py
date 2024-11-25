

key = "AIzaSyDQMl7clb1OI61AtDyDyUjyO7sGdcXwoog"

import requests

with open("server/tests/test.md", "r") as f:
    text = f.read()

prompt = f"""
You are given a full 10-K filing in a markdown form. Split it into appropriate chunks and provide a contextural summary of the chunk. Output a python list of these chunks and their summaries.

{text}
"""

url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
api_key = "AIzaSyDQMl7clb1OI61AtDyDyUjyO7sGdcXwoog"

headers = {
    "Content-Type": "application/json"
}

data = {
    "contents": [
        {
            "parts": [
                {
                    "text": prompt
                }
            ]
        }
    ]
}

response = requests.post(url, headers=headers, json=data, params={"key": api_key})

print(response.status_code)
# print(response.json())

import json
with open("server/tests/test_output.json", "w") as f:
    json.dump(response.json(), f, indent=2)