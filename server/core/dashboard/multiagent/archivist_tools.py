import traceback

from vectorstore import vectorstore_manager 

from pydantic import BaseModel, Field
from typing import Annotated, List

from datetime import datetime

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.tools import tool

ticker_vectorstore = FAISS.load_local("server/core/dashboard/multiagent/tickers_json_vectorstore", embeddings=OpenAIEmbeddings(), allow_dangerous_deserialization=True)
DEBUG = False

def debug_print(any):
    if DEBUG: print(any)

@tool
def get_current_time(*args) -> str:
    """Returns the current time in YYYY-MM-DD format"""
    return datetime.now().strftime("%Y-%m-%d")

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
    debug_print("[get_available_filings] Metadata:", metadata)
    chunks = await vectorstore_manager.vectorstore.asimilarity_search("", k=1000, fetch_k=1000, filter=metadata) 
    if len(chunks) == 0:
        debug_print("[get_available_filings]","No filings available for this ticker")
        return "No filings available for this ticker"
    else:
        debug_print("[get_available_filings] chunks:",len(chunks))
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
    debug_print("[get_current_time]",current_time)
    return current_time

@tool
async def get_all_available_filings_tickers_and_years(
*args
) -> List[List[str]]:
    """Get tickers and years for all filings available in the database."""

    chunks = await vectorstore_manager.vectorstore.asimilarity_search("", k=1000, fetch_k=1000) 
    if len(chunks) == 0:
        debug_print("[get_available_filings]","No filings available for this ticker")
        return "No filings available for this ticker"
    else:
        debug_print("[get_available_filings] chunks:",len(chunks))
    available_filings = []
    available_filings.append(["ticker", "year"])
    try:
        for chunk in chunks:
            if "ticker" not in chunk.metadata:
                continue
            data = [chunk.metadata["ticker"], chunk.metadata["year"]]
            if data not in available_filings:
                available_filings.append(data)
                debug_print("[get_available_filings] data:",data)
    except Exception as e:
        debug_print(traceback.format_exc())
        debug_print(str(e))
        raise e
    return available_filings


class FilingDataRetrieverModel(BaseModel):
    query: str = Field("Ticker")
    ticker: str = Field("Company Ticker")
    filing_date: str = Field("Filing date. Format YYYY-MM-DD")
    filing_type: str = Field("Filing type") # type: ignore

@tool
async def retrieve_data_from_filing(
    tool_input: FilingDataRetrieverModel    
) -> List[str]:
    """Use filing_date and filing_type you found using get_available_filings or from the message history.\
    Use ticker that you found using search_tickers or from the message history.\
    Input.\
    Returns chunks of data from the database on specific filing."""
    metadata = {
        "ticker": tool_input.ticker.lower(), 
        "date": tool_input.filing_date,
        "form": tool_input.filing_type,
    }

    debug_print("[FilingDataRetriever] Metadata:", metadata)
    debug_print("[FilingDataRetriever] Query:", tool_input.query)
    chunks = await vectorstore_manager.vectorstore.asimilarity_search(tool_input.query, k=10, fetch_k=1000, filter=metadata) 
    debug_print(f"[FilingDataRetriever] Found {len(chunks)} chunks...")
    return "\n\n".join([chunk.page_content for chunk in chunks])


archivist_tools = [
    retrieve_data_from_filing,
    get_available_filings,
    get_all_available_filings_tickers_and_years,
    search_tickers,
    get_current_time,
    stock_price_plotter,
    get_current_time
]

archivist_toolnames = [tool.name for tool in archivist_tools]

if __name__ == "__main__":
    print(archivist_toolnames)