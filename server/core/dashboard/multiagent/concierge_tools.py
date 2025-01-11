from langchain.tools import StructuredTool
import sys

sys.path.append("")

from server.core.dashboard.multiagent.archivist_tools import ticker_vectorstore

import asyncio
import json

from pydantic import BaseModel, Field
from typing import Optional, Type, Annotated

from langchain_core.tools import BaseTool
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

from yfinance import Ticker

def sign_up(*args) -> str:
    # print("Switching to Signup input...")
    return {'status': 'success', 'message': 'Switching to Signup input...'}

def sign_in(*args) -> str:
    # print("Switching to Login input...")
    return {'status': 'success', 'message': 'Switching to Login input...'}

def forgot_password(*args) -> str:
    # print("Switching to Password Reset input...")
    return {'status': 'success', 'message': 'Switching to Password Reset input...'}

def widget_tradingview(ticker: Annotated[str, "Company ticker"],) -> str:
    # print("Switching to Tradingview widget...")
    return {'type': 'tradingview', 'ticker': ticker.upper()}

class TickerNews(BaseModel):
    query: str = Field("Ticker")

class TickerNewsTool(BaseTool):
    name: str = "ticker_news"
    description: str = "Search up-to-date news for ticker"
    args_schema: Type[BaseModel] = TickerNews
    return_direct: bool = False
    
    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        return Ticker(query).news


    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        results = await ticker_vectorstore.asimilarity_search(query, k=1, fetch_k=100000)

        ticker = json.loads(results[0].page_content)["ticker"]
        return Ticker(ticker).news

class ProfileExtractor(BaseModel):
    query: str = Field("User id")

class ProfileExtractorTool(BaseTool):
    name: str = "profile_extractor"
    description: str = "Returns current user profile"
    args_schema: Type[BaseModel] = ProfileExtractor
    return_direct: bool = False
    user_id: str

    def __init__(self, user_id: str, *args, **kwargs):        
        # pass custom variable down to the initialization of the inheritted class
        super(ProfileExtractorTool, self).__init__(user_id=user_id)
    
    def _run(
        self, query: Optional[str] = None, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        with open("server/memory/trader_profiles.json", "r") as f:
            data = json.load(f)
        if self.user_id not in data:
            return "No profile found"

        return json.dumps(data[self.user_id], indent=2)


    async def _arun(
        self,
        query: Optional[str] = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        with open("server/memory/trader_profiles.json", "r") as f:
            data = json.load(f)
        if self.user_id not in data:
            return "No profile found"

        return json.dumps(data[self.user_id], indent=2)
    
class TickerBalanceSheet(BaseModel):
    query: str = Field("Ticker")

class TickerBalanceSheetTool(BaseTool):
    name: str = "ticker_balance_sheet"
    description: str = "Search up-to-date balance sheet for ticker"
    args_schema: Type[BaseModel] = TickerNews
    return_direct: bool = False
    
    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        return Ticker(query).get_balance_sheet(as_dict=True, freq="quarterly")


    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        results = await ticker_vectorstore.asimilarity_search(query, k=1, fetch_k=100000)

        ticker = json.loads(results[0].page_content)["ticker"]
        return Ticker(ticker).get_balance_sheet(as_dict=True, freq="quarterly")
    
class TickerIncomeStatement(BaseModel):
    query: str = Field("Ticker")

class TickerIncomeStatementTool(BaseTool):
    name: str = "ticker_income_statement"
    description: str = "Search up-to-date income statement for ticker"
    args_schema: Type[BaseModel] = TickerNews
    return_direct: bool = False
    
    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        return Ticker(query).get_income_stmt(as_dict=True, freq="quarterly")


    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        await asyncio.sleep(0.5)
        results = await ticker_vectorstore.asimilarity_search(query, k=1, fetch_k=100000)

        ticker = json.loads(results[0].page_content)["ticker"]
        return Ticker(ticker).get_income_stmt(as_dict=True, freq="quarterly")
    
class TickerCashFlowStatement(BaseModel):
    query: str = Field("Ticker")

class TickerCashFlowStatementTool(BaseTool):
    name: str = "ticker_cash_flow_statement"
    description: str = "Search up-to-date cash flow statement for ticker"
    args_schema: Type[BaseModel] = TickerNews
    return_direct: bool = False
    
    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        return Ticker(query).get_cash_flow(as_dict=True, freq="quarterly")


    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        await asyncio.sleep(0.5)
        results = await ticker_vectorstore.asimilarity_search(query, k=1, fetch_k=100000)

        ticker = json.loads(results[0].page_content)["ticker"]
        return Ticker(ticker).get_cash_flow(as_dict=True, freq="quarterly")
    
class TickerAnalystPriceTargets(BaseModel):
    query: str = Field("Ticker")

class TickerAnalystPriceTargetsTool(BaseTool):
    name: str = "ticker_analyst_price_targets"
    description: str = "Search up-to-date analyst price targets for ticker"
    args_schema: Type[BaseModel] = TickerNews
    return_direct: bool = False
    
    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        
        return Ticker(query).get_analyst_price_targets()


    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        await asyncio.sleep(0.5)
        results = await ticker_vectorstore.asimilarity_search(query, k=1, fetch_k=100000)

        ticker = json.loads(results[0].page_content)["ticker"]
        return Ticker(ticker).get_analyst_price_targets()




tool_sign_in = StructuredTool.from_function(func=sign_in, name="tool_login", description="Login tool. This tool adjusts the frontend so that the user could input his email and password. Invoke if user asks to login or sign in.", return_direct=False)
tool_sign_up = StructuredTool.from_function(func=sign_up, name="tool_signup_email", description="Signup tool. This tool adjusts the frontend so that the user could input his email, after which a confirmation email will be sent. Invoke if user asks to create account or sign up.", return_direct=False)
tool_forgot_password = StructuredTool.from_function(func=forgot_password, name="tool_forgot_password", description="Forgot Password tool. This tool adjusts the frontend so that the user could input his email, after which a confirmation email with password reset link will be sent.", return_direct=False)
tool_widget_tradingview = StructuredTool.from_function(func=widget_tradingview, name="widget_tradingview", description="Use this to plot the stock price for the user. Returns a plot label ([SP_PLT]) if successful.", return_direct=False)

concierge_tools = [
    TickerNewsTool(),
    TickerBalanceSheetTool(),
    TickerIncomeStatementTool(),
    TickerCashFlowStatementTool(),
    TickerAnalystPriceTargetsTool(),
    tool_sign_in,
    tool_sign_up,
    tool_forgot_password,
    tool_widget_tradingview
]

concierge_toolnames = [tool.name for tool in concierge_tools]

if __name__ == "__main__":
    print(concierge_toolnames)