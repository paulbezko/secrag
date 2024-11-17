
import asyncio
from io import StringIO
from math import sqrt
import multiprocessing
import re
import sys
from .vectorstore import vectorstore_manager
from .google_search import google_search

from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, Type

from langchain_core.tools import BaseTool, Tool
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)


class FinancialsTableSelection(BaseModel):
    query: str = Field("""choose from the following options:
        "balance_sheet", 
        "income_statement", 
        "cash_flow_statement", 
        "statement_of_changes_in_equity", 
        "statement_of_comprehensive_income"
                               """)


class FinancialsRAGTool(BaseTool):
    name: str = "financial_data_filing_retriever"
    description: str = """Retrieves one of the financials for the current document if they exist."""
    args_schema: Type[BaseModel] = FinancialsTableSelection
    return_direct: bool = False

    # Initialize annotated custom variable
    chunk_metadata_model: Dict[str, Any]

    def __init__(self, chunk_metadata_model: dict, *args, **kwargs):        
        # pass custom variable down to the initialization of the inheritted class
        super(FinancialsRAGTool, self).__init__(chunk_metadata_model=chunk_metadata_model)

    def _run(
        self, 
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        output = []
        chunk_metadata_model = {
            "ticker": self.chunk_metadata_model["ticker"], 
            "year": self.chunk_metadata_model["year"],
            "chunk_size": self.chunk_metadata_model["chunk_size"],
            "chunk_overlap": self.chunk_metadata_model["chunk_overlap"],
            "table_prepend_k": self.chunk_metadata_model["table_prepend_k"],
            "chunk_description": remove_special_characters(query),  # In case if special characters like \n leak in the query
        }
        list_retrieved_chunks = vectorstore_manager.vectorstore.similarity_search("", k=1, fetch_k=10000, filter=chunk_metadata_model)
        for chunk in list_retrieved_chunks:
            output.append(chunk.page_content)
        return output

    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        output = []
        chunk_metadata_model = {
            "ticker": self.chunk_metadata_model["ticker"], 
            "year": self.chunk_metadata_model["year"],
            "chunk_size": self.chunk_metadata_model["chunk_size"],
            "chunk_overlap": self.chunk_metadata_model["chunk_overlap"],
            "table_prepend_k": self.chunk_metadata_model["table_prepend_k"],
            "chunk_description": remove_special_characters(query), # In case if special characters like \n leak in the query
        }
        list_retrieved_chunks = vectorstore_manager.vectorstore.similarity_search("", k=1, fetch_k=10000, filter=chunk_metadata_model)
        for chunk in list_retrieved_chunks:
            output.append(chunk.page_content)
        return output


class FilingRAGQuery(BaseModel):
    query: str = Field("Query to non-financial data filing retriever")

class FilingRAGTool(BaseTool):
    name: str = "non-financial_data_filing_retriever"
    description: str = "Retrieve data from the current SEC 10-K filing. In case if abbreviation is in the query, pass it and its expanded version"
    args_schema: Type[BaseModel] = FilingRAGQuery
    return_direct: bool = False

    # Initialize annotated custom variable
    chunk_metadata_model: Dict[str, Any]    

    def __init__(self, chunk_metadata_model):
        # pass custom variable down to the initialization of the inheritted class
        super(FilingRAGTool, self).__init__(chunk_metadata_model=chunk_metadata_model)
    
    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        list_retrieved_chunks = vectorstore_manager.vectorstore.similarity_search_with_score(query, k=8, filter=self.chunk_metadata_model, fetch_k=10000)
        list_context_chunks = ""
        for chunk in list_retrieved_chunks:
            list_context_chunks += chunk[0].page_content + "\n"
        
        return list_context_chunks


    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        list_retrieved_chunks = vectorstore_manager.vectorstore.similarity_search_with_score(query, k=8, filter=self.chunk_metadata_model, fetch_k=10000)
        list_context_chunks = ""
        for chunk in list_retrieved_chunks:
            list_context_chunks += chunk[0].page_content + "\n"
        
        return list_context_chunks

class GoogleSearchQuery(BaseModel):
    query: str = Field("Query to google search")

class GoogleSearchTool(BaseTool):
    name: str = "google_search"
    description: str = "Search up-to-date data"
    args_schema: Type[BaseModel] = GoogleSearchQuery
    return_direct: bool = False
    
    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        return google_search(query=query)


    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        return google_search(query=query)


def remove_special_characters(input_string):
    # Keep only alphanumeric characters and underscores
    cleaned_string = ''.join(char for char in input_string if char.isalnum() or char == '_')
    return cleaned_string

# Initialize google_search tool globally since it does not need extra initialization
google_search_tool = GoogleSearchTool()