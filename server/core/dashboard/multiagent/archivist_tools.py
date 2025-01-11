import traceback

from vectorstore import vectorstore_manager 

from pydantic import BaseModel, Field
from typing import Annotated, Literal, List, Optional, Type

from datetime import datetime
from user_profile_model import InvestorTraderProfile

from langchain.tools import StructuredTool
from langchain_openai import OpenAIEmbeddings

from langchain_community.vectorstores import FAISS
from langchain_core.tools import tool
from langchain_core.tools import BaseTool
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

ticker_vectorstore = FAISS.load_local("server/core/dashboard/multiagent/tickers_json_vectorstore", embeddings=OpenAIEmbeddings(), allow_dangerous_deserialization=True)

def get_current_time(*args) -> str:
    return datetime.now().strftime("%Y-%m-%d")
tool_get_current_time = StructuredTool.from_function(func=get_current_time, name="get_current_time", description="Returns the current time in YYYY-MM-DD format", return_direct=False)


@tool 
async def search_tickers(
    query: Annotated[str, "Query to search company ticker by"],
):
    """Use this to search for companies that have entries in the database."""
    results = ticker_vectorstore.similarity_search_with_relevance_scores(query, k=10, fetch_k=100000)
    formatted_results = ""
    for i in results:
        formatted_results+=str([i[0].page_content, f"relevance: {float(i[1])*100:.2f}%"])+"\n"


    return formatted_results

@tool 
async def stock_price_plotter(
    ticker: Annotated[str, "Company ticker"],
):
    """Use this to plot the stock price for the user. Returns a plot label ([SP_PLT]) if successful."""
    
    return f"[SP_PLT][{ticker.upper()}]"

@tool
async def get_available_filings(
    ticker: str | None = Field("Company ticker"),
    year: int = Field("Year. Example: 2024")
) -> List[List[str]]:
    """Use ticker that you found using search_tickers or from the message history, and a year to search for metadata on the filings that are available in the database for the input ticker and input year."""
    metadata = {"ticker": ticker.lower(), "year":str(year)}
    print("[get_available_filings] Metadata:", metadata)
    chunks = await vectorstore_manager.vectorstore.asimilarity_search("", k=1000, fetch_k=1000, filter=metadata) 
    if len(chunks) == 0:
        print("[get_available_filings]","No filings available for this ticker")
        return "No filings available for this ticker"
    else:
        print("[get_available_filings] chunks:",len(chunks))
    available_filings = []
    header = ["ticker", "filing_date", "filing_type"]
    
    for chunk in chunks:
        data = [chunk.metadata["ticker"], chunk.metadata["date"], chunk.metadata["form"]]
        if data not in available_filings:
            available_filings.append(data)
            
    sorted_filings = sorted(available_filings, key=lambda x: x[1], reverse=True)
    return header + sorted_filings

@tool
async def get_current_time(*args) -> str:
    """Returns the current time in YYYY-MM-DD format."""
    current_time = datetime.now().strftime("%Y-%m-%d")
    print("[get_current_time]",current_time)
    return current_time

@tool
async def get_all_available_filings_tickers_and_years(
*args
) -> List[List[str]]:
    """Get tickers and years for all filings available in the database."""

    chunks = await vectorstore_manager.vectorstore.asimilarity_search("", k=1000, fetch_k=1000) 
    if len(chunks) == 0:
        print("[get_available_filings]","No filings available for this ticker")
        return "No filings available for this ticker"
    else:
        print("[get_available_filings] chunks:",len(chunks))
    available_filings = []
    available_filings.append(["ticker", "year"])
    try:
        for chunk in chunks:
            if "ticker" not in chunk.metadata:
                continue
            data = [chunk.metadata["ticker"], chunk.metadata["year"]]
            if data not in available_filings:
                available_filings.append(data)
                print("[get_available_filings] data:",data)
    except Exception as e:
        print(traceback.format_exc())
        print(str(e))
        raise e
    return available_filings


class FilingDataRetrieverModel(BaseModel):
    query: str = Field("Ticker")
    ticker: str = Field("Company Ticker")
    filing_date: str = Field("Filing date. Format YYYY-MM-DD")
    filing_type: str = Field("Filing type") # type: ignore

class FilingDataRetrieverTool(BaseTool):
    name: str = "retrieve_data_from_filing"
    description: str = "Use filing_date and filing_type you found using get_available_filings or from the message history.\
    Use ticker that you found using search_tickers or from the message history.\
    Input\
    Returns chunks of data from the database on specific filing."
    args_schema: Type[BaseModel] = FilingDataRetrieverModel
    return_direct: bool = False
    
    def _run(
        self, 
        query: str, 
        ticker: str, filing_date: str, filing_type: str, 
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        
        metadata = {
            "ticker": ticker.lower(), 
            "date": filing_date,
            "form": filing_type,
        }
        """Use the tool."""
        print("[FilingDataRetriever] Metadata:", metadata)
        print("[FilingDataRetriever] Query:", query)
        chunks = vectorstore_manager.vectorstore.similarity_search(query, k=10, fetch_k=1000, filter=metadata)
        return "\n\n".join([chunk.page_content for chunk in chunks])

    async def _arun(
        self,
        query: str,
        ticker: str, filing_date: str, filing_type: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> List[str]:
        """Use the tool asynchronously."""
        metadata = {
            "ticker": ticker.lower(), 
            "date": filing_date,
            "form": filing_type,
        }
        """Use the tool."""
        print("[FilingDataRetriever] Metadata:", metadata)
        print("[FilingDataRetriever] Query:", query)
        chunks = await vectorstore_manager.vectorstore.asimilarity_search(query, k=10, fetch_k=1000, filter=metadata) 
        print(f"[FilingDataRetriever] Found {len(chunks)} chunks...")
        return "\n\n".join([chunk.page_content for chunk in chunks])


    query: str = Field("Ticker")




archivist_tools = [
    FilingDataRetrieverTool(),
    get_available_filings,
    get_all_available_filings_tickers_and_years,
    search_tickers,
    tool_get_current_time,
    stock_price_plotter,
    get_current_time
]