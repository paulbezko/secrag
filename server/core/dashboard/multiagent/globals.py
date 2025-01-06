from typing import Annotated, TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages

from dotenv import load_dotenv

load_dotenv(".env", override=True)

llm = ChatOpenAI(model="gpt-4o-mini")

class State(TypedDict):
    messages: Annotated[list, add_messages]
    latest_user_message: str
    user_profile: dict
    user_id: str
    