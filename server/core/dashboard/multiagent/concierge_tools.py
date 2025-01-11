import sys

sys.path.append("")

from server.core.dashboard.multiagent.archivist_tools import ticker_vectorstore

import json

from typing import Any, Annotated

from langchain_core.tools import tool

from yfinance import Ticker


@tool
async def login(*args) -> str:
    """"Login tool. This tool adjusts the frontend so that the user could input his email and password."""
    return "Login tool executed."

@tool
async def signup_email(*args) -> str:
    """"Signup tool. This tool adjusts the frontend so that the user could input his email, after which a confirmation email will be sent."""
    return "Signup tool executed."

@tool
async def forgot_password(*args) -> str:
    """"Forgot Password tool. This tool adjusts the frontend so that the user could input his email, after which a confirmation email with password reset link will be sent."""
    return "Forgot Password tool executed."

@tool
async def widget_tradingview(ticker: Annotated[str, "Company ticker"]) -> str:
    """Use this to plot the stock price for the user. Returns a plot metadata json if successful."""
    return {'name': 'tradingview', 'ticker': ticker.upper()}

@tool 
async def ticker_news(
    query: Annotated[str, "Ticker to search news for"],
) -> list:
    """Search up-to-date news for ticker"""
    results = await ticker_vectorstore.asimilarity_search(query, k=1, fetch_k=100000)

    ticker = json.loads(results[0].page_content)["ticker"]
    return Ticker(ticker).news
       
@tool
async def ticker_balance_sheet(
    query: Annotated[str, "Ticker to search balance sheet for"],
) -> Any:
    """Search up-to-date balance sheet for ticker"""
    results = await ticker_vectorstore.asimilarity_search(query, k=1, fetch_k=100000)

    ticker = json.loads(results[0].page_content)["ticker"]
    return Ticker(ticker).get_balance_sheet(as_dict=True, freq="quarterly")

@tool
async def ticker_income_statement(
    query: Annotated[str, "Ticker to search income statement for"],
) -> Any:
    """Search up-to-date income statement for ticker"""
    results = await ticker_vectorstore.asimilarity_search(query, k=1, fetch_k=100000)

    ticker = json.loads(results[0].page_content)["ticker"]
    return Ticker(ticker).get_income_stmt(as_dict=True, freq="quarterly")

@tool 
async def ticker_cash_flow_statement(
    query: Annotated[str, "Ticker to search cash flow statement for"],
) -> Any:
    """Search up-to-date cash flow statement for ticker"""
    results = await ticker_vectorstore.asimilarity_search(query, k=1, fetch_k=100000)

    ticker = json.loads(results[0].page_content)["ticker"]
    return Ticker(ticker).get_cash_flow(as_dict=True, freq="quarterly")

@tool 
async def ticker_analyst_price_targets(
    query: Annotated[str, "Ticker to search analyst price targets for"],
) -> Any:
    """Search up-to-date analyst price targets for ticker"""
    results = await ticker_vectorstore.asimilarity_search(query, k=1, fetch_k=100000)

    ticker = json.loads(results[0].page_content)["ticker"]
    return Ticker(ticker).get_analyst_price_targets()

concierge_tools = [
    ticker_news,
    ticker_balance_sheet,
    ticker_income_statement,
    ticker_cash_flow_statement,
    ticker_analyst_price_targets,
    login,
    signup_email,
    forgot_password,
    widget_tradingview
]

concierge_toolnames = [tool.name for tool in concierge_tools]

if __name__ == "__main__":
    print(concierge_toolnames)