from datetime import datetime
from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv
import os
load_dotenv()

stop_signals = {}
embeddings_queue = [] # This variable is used for current vectorstore embeddings processes book-keeping

class Config:
    def __init__(self):
        self.config = {
        }

    def get(self, key: str):
        return self.config[key]

    def set(self, data: dict):
        self.config = data

class Mongo:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGO_URI'))
        self.db = self.client["SECRAG"]

# Singleton instance
config = Config()
mongo = Mongo()

sec_rate_limit = 7
sec_rate_limit_counter = 0


def mongo_insert_message(collection, uuid, chat_id, role, content, widgets=None):
    try:
        result = collection.update_one(
            {"_id": uuid},
            {"$push": {f"chats.{chat_id}.messages": {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "role": role, "content": content, "widgets": widgets}}}
        )
        if result.modified_count > 0: 
            return {"message": f"Message added to chat '{chat_id}' for user '{uuid}'."}
        else: 
            return {"error": f"Chat '{chat_id}' not found for user '{uuid}'."}
    except Exception as e:
        return {"error": f"Error inserting message for '{uuid}' and chat '{chat_id}' and message '{content}': {str(e)}"}

widgets = [
  {
    "id": "SP_PLT",
    "type": "treemap",
    "params": {
      "series": [
        {
          "name": "TICKERS",
          "data": [
            {
              "x": "AAPL",
              "y": 100
            },
            {
              "x": "MSFT",
              "y": 50
            },
            {
              "x": "GOOG",
              "y": 25
            }
          ]
        },
        {
          "name": "PRICE",
          "data": [
            {
              "x": "AAPL",
              "y": 100
            },
            {
              "x": "MSFT",
              "y": 50
            },
            {
              "x": "GOOG",
              "y": 25
            }
          ]
        }
      ]
    }
  }
]

mongo_insert_message(mongo.db[f"chats_dev"], 'J6IBC79NCYK2K4HJ', 'general', 'assistant', "Hello Paul!<br>[SP_PLT]<br>How can I help you today?", widgets)

message = {
  "role": "user",
  "content": "What is the company's balance sheet?",
  "widgets": [
    {
      "id": "SP_PLT",
      "type": "treemap",
      "params": {
        "series": [
          {
            "name": "TICKERS",
            "data": [
              {
                "x": "AAPL",
                "y": 100
              },
              {
                "x": "MSFT",
                "y": 50
              },
              {
                "x": "GOOG",
                "y": 25
              }
            ]
          },
          {
            "name": "PRICE",
            "data": [
              {
                "x": "AAPL",
                "y": 100
              },
              {
                "x": "MSFT",
                "y": 50
              },
              {
                "x": "GOOG",
                "y": 25
              }
            ]
          }
        ]
      }
    }
  ]
}