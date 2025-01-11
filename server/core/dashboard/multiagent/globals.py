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
    

supported_form_types = ["10-Q", "10-K", "8-K", "4", "3", "144", "SC 13", "DEF 14"]

toolset = [
    # Concierge tools
    'ticker_news', 
    'ticker_balance_sheet', 
    'ticker_income_statement', 
    'ticker_cash_flow_statement', 
    'ticker_analyst_price_targets', 
    'login', 
    'signup_email', 
    'forgot_password', 
    'widget_tradingview'
    # Archivist tools
    'retrieve_data_from_filing', 
    'get_available_filings', 
    'get_all_available_filings_tickers_and_years', 
    'search_tickers', 
    'get_current_time', 
    'stock_price_plotter', 
    'get_current_time', 
    'basic_treemap_plotter'
]

tools_triggering_plotter = [
    # Concierge tools
    'ticker_balance_sheet', 
    'ticker_income_statement', 
    'ticker_cash_flow_statement', 
    # Archivist tools
    'retrieve_data_from_filing', 
]