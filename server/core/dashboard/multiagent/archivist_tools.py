import json
from typing import Annotated, Literal, Union
from datetime import datetime
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

from langchain_core.tools import tool
from .globals import llm


years = []
for year in range(2000, datetime.now().year + 1):
    years.append(year)

# years = tuple(years)
# Fix: Use eval or explicit definition
YearLiteral = eval(f"Literal[{', '.join(map(str, years))}]")

vectorstore = FAISS.load_local("server/core/dashboard/multiagent/tickers_json_vectorstore", embeddings=OpenAIEmbeddings(), allow_dangerous_deserialization=True)

chain = llm

@tool
def get_filings(
    ticker_name_cik_filter: Annotated[str, "Either ticker, company name, or company cik to filter by."],
    filing_type_filter: Annotated[Union[Literal["10-K", "10-Q"], None], "Filing type"],
    filter_by_start_year: Annotated[int, "Start year to filter by"],
    filter_by_end_year: Annotated[Union[int, None], "End year to filter by (Higher than Start year)"]  
):
    """Use this to return available filings from the database based on ticker, name, cik, filing type (can be empty), start year, end year (can be empty)."""
    filtered_data = {}
    if filter_by_start_year:
        end_year = filter_by_end_year if filter_by_end_year else datetime.now().year
        year_filter = list(range(filter_by_start_year, end_year + 1))
    # print(ticker_name_cik_filter, filing_type_filter, year_filter)
    with open("server/memory/filings_available.json", "r") as f:
        data = dict(json.load(f))

    for key, filings_by_year in data.items():
        # Check if the top-level key matches the filter
        
        if ticker_name_cik_filter and ticker_name_cik_filter.upper() not in key:
            continue
        # print(key)
        matched_years = {}
        for year, filings in filings_by_year.items():
            # print(year == year_filter, type(year), type(year_filter))
            # Check if the year is in the filter list

            if year_filter and int(year) not in year_filter:
                continue
            # print(year, filings)
            # Filter filings by filing type if necessary
            filtered_filings = [
                filing for filing in filings
                if not filing_type_filter or filing.startswith(filing_type_filter)
            ]
            
            if filtered_filings:
                matched_years[year] = filtered_filings
                # print(filtered_filings)
        # Only add to result if there's a match
        if matched_years:
            filtered_data[key] = matched_years
    
    return json.dumps(filtered_data, indent=4)



@tool 
async def search_companies(
    search_term: Annotated[str, "Either ticker, company name, or company cik to filter by."],
):
    """Use this to search for companies that have entries in the database."""
    results = vectorstore.similarity_search_with_relevance_scores(search_term, k=10, fetch_k=100000)
    formatted_results = ""
    for i in results:
        formatted_results+=str([i[0].page_content, f"relevance: {float(i[1])*100:.2f}%"])+"\n"


    return formatted_results


@tool
def get_available_years(
    *args
):
    """Use this to return all the available years in the database."""   
    return years

archivist_tools = [get_available_years, search_companies, get_filings]