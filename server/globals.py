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
