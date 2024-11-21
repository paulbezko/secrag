# This file is needed to share the variable between the socket and the stream
stop_signals = {}
# This variable is used for current vectorstore embeddings processes book-keeping
embeddings_queue = []

class Config:
    def __init__(self):
        self.config = {
        }

    def get(self, key: str):
        return self.config[key]

    def set(self, data: dict):
        self.config = data

# Singleton instance
config = Config()
