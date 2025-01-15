from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# MongoDB class for connection
class Mongo:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGO_URI'))
        self.db = self.client["SECRAG"]

    def get_last_10_messages(self, user_id):
        # Query to fetch only the last 10 messages
        pipeline = [
            {"$match": {"_id": user_id}},  # Match the specific document by _id
            {"$project": {
                "last_10_messages": {"$slice": ["$chats.general.messages", -10]}  # Slice to get last 10 messages
            }}
        ]
        
        result = list(self.db["chats_dev"].aggregate(pipeline))

        if result:
            return result[0].get("last_10_messages", [])
        else:
            return []

    def load_more_messages(self, user_id, skip_count):
        print(skip_count)
        pipeline = [
            {"$match": {"_id": user_id}},  # Match the specific document by _id
            {"$project": {
                "messages_count": {"$size": "$chats.general.messages"},  # Count total messages
                "more_messages": {
                    "$slice": [
                        "$chats.general.messages",
                        {"$max": [0, {"$subtract": [{"$size": "$chats.general.messages"}, skip_count + 10]}]},
                        {"$min": [10, {"$subtract": [{"$size": "$chats.general.messages"}, skip_count]}]}
                    ]
                }
            }}
        ]
        
        result = list(self.db["chats_dev"].aggregate(pipeline))

        if result:
            return result[0].get("more_messages", [])
        else:
            return []

# Instantiate Mongo class
mongo = Mongo()

user_id = "zvvUapmFfFpjvrqX"

last_10_messages = mongo.get_last_10_messages(user_id)
print("\n\nLast 10 Messages:", len(last_10_messages))

more_messages = mongo.load_more_messages(user_id, skip_count=30)
print("\n\nMore Messages:", len(more_messages))
