

key = "AIzaSyDQMl7clb1OI61AtDyDyUjyO7sGdcXwoog"

import requests

with open("server/tests/test.md", "r") as f:
    text = f.read()

prompt = f"""
Summarize the most unusual and noteworthy aspects of the 10-K filing in the form of a LinkedIn post, written from the perspective of an independent analyst.

- Start with a catchy two-sentence hook.
- Highlight key anomalies, unexpected trends, or unique details.
- Keep the tone analytical and engaging, while avoiding excessive jargon.
- Limit the summary to a few sentences.

Input text:
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