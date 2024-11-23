import asyncio
import traceback
from typing import Optional, Union
from langchain_core.documents import Document
import sys

# Add the path to custom libs
sys.path.append("server/lib_secrag")

from ...lib_secrag.edgar.xbrl.facts import XBRLInstance
from ...lib_secrag.edgar.xbrl.xbrldata import XBRLData
from ...globals import sec_rate_limit, sec_rate_limit_counter
from ...general.utils import try_except, atry_except, log
from ...lib_secrag.edgar.financials import Financials
from ...lib_secrag.edgar.htmltools import TableBlock
from ...lib_secrag.edgar.entities import EntityData, get_entity
from ...lib_secrag.edgar.core import set_identity

import pandas as pd
import re


# Launches async task and triggers rate limiter 
async def launch_rate_limited(function, num_of_func_requests: int = 1):
    global sec_rate_limit_counter
    while sec_rate_limit_counter >= sec_rate_limit:
        await asyncio.sleep(0)
    sec_rate_limit_counter += num_of_func_requests
    launch_rate_count_timer(num_of_func_requests)
    result = await function()
    return result

# Launches sync task and triggers rate limiter 
async def launch_rate_limited_sync_func(function, num_of_func_requests: int = 1):
    global sec_rate_limit_counter
    await asyncio.sleep(0)
    while sec_rate_limit_counter >= sec_rate_limit:
        await asyncio.sleep(0)
    sec_rate_limit_counter += num_of_func_requests    
    launch_rate_count_timer(num_of_func_requests)
    result = function()
    return result

# Launches task that decreases rate limit counter after some time
def launch_rate_count_timer(instances: int = 1):
    for i in range(instances):
        asyncio.create_task(elapse_rate_limit_count())

# Function that decreases rate limit counter after some time
async def elapse_rate_limit_count():
    global sec_rate_limit_counter
    await asyncio.sleep(0.2)
    sec_rate_limit_counter -= 1


# Creating a class for filing information
class FilingObject():
    def __init__(self, ticker, cik, filing_date, filing_type, filing_year) -> None:
        self.ticker = ticker
        self.cik = cik
        self.filing_date = filing_date
        self.filing_type = filing_type
        self.filing_year = filing_year

    def to_dict(self):
        return {
            'ticker': self.ticker,
            'cik': self.cik,
            'filing_date': self.filing_date,
            'filing_type': self.filing_type,
            'filing_year': self.filing_year
        }
    
    @staticmethod
    def from_dict(data):
        return FilingObject(
            ticker=data['ticker'],
            cik=data['cik'],
            filing_date=data['filing_date'],
            filing_type=data['filing_type'],
            filing_year=data['filing_year']
        )

# Creating a class for enhanced filing information
class SECFilingObject():
    def __init__(self, filing, markdown, file_number, filing_html, cik, ticker, filing_date, filing_year, company_name, filing_type, balance_sheet = None, income_statement = None, cash_flow_statement = None, statement_of_comprehensive_income = None, statement_of_changes_in_equity = None):
        self.filing = filing 
        self.ticker = ticker
        self.filing_type = filing_type
        self.markdown = markdown
        self.file_number = file_number
        self.filing_date = filing_date
        self.filing_year = filing_year
        self.cik = cik
        self.html = filing_html
        self.company_name = company_name
        self.balance_sheet = balance_sheet,
        self.statement_of_comprehensive_income = statement_of_comprehensive_income
        self.statement_of_changes_in_equity = statement_of_changes_in_equity
        self.income_statement = income_statement,
        self.cash_flow_statement = cash_flow_statement,
    
    def get_financials(self):
        """
        Returns a dictionary of the financials associated with this filing object
        
        The dictionary will contain the following keys: 
        - "balance_sheet": the balance sheet for this filing
        - "income_statement": the income statement for this filing
        - "cash_flow_statement": the cash flow statement for this filing
        - "statement_of_changes_in_equity": the statement of changes in equity for this filing
        - "statement_of_comprehensive_income": the statement of comprehensive income for this filing
        
        Returns:
            dict: A dictionary of financials associated with this filing object
        """
        return {
            "balance_sheet": self.balance_sheet,
            "income_statement": self.income_statement,
            "cash_flow_statement": self.cash_flow_statement,
            "statement_of_changes_in_equity": self.statement_of_changes_in_equity,
            "statement_of_comprehensive_income": self.statement_of_comprehensive_income
        }
    
    async def get_documents(self, chunk_size = 10000, chunk_overlap = 3, table_prepend_k = 3):
        """
        Converts the filing object into a list of Document objects for embedding.

        This function takes the filing object and its associated financials, and uses the `filing_splitter` function to split the filing into chunks.
        It then composes a list of `Document` objects, where each object contains the text content of a chunk and its associated metadata.

        Args:
            chunk_size (int, optional): The maximum size of each chunk. Defaults to 10000.
            chunk_overlap (int, optional): The number of rows to overlap between chunks. Defaults to 3.
            table_prepend_k (int, optional): The number of rows to prepend to each table chunk. Defaults to 3.

        Returns:
            list: A list of `Document` objects, where each object contains the text content of a chunk and its associated metadata.
        """
        
        # Use custom filing splitter for chunking
        list_chunks = await filing_splitter(self, self.get_financials(), chunk_size, chunk_overlap, table_prepend_k)
        list_documents = []
        for chunk in list_chunks:
            list_documents.append(Document(
                page_content=chunk["text"],
                metadata=chunk["metadata"]
            ))
        return list_documents

# Getting filing object
def get_filing(filing_id, filing_date, filing_cik) -> FilingObject:

    ticker, filing_year, filing_type = filing_id.split("-")
    if filing_type == "10K": filing_type = "10-K"
    elif "10Q" in filing_type: filing_type = "10-Q"
    else: raise Exception(f"Unsupported filing type {filing_type}")
    filing = FilingObject(ticker=ticker, cik=filing_cik, filing_date=filing_date, filing_type=filing_type, filing_year=filing_year)
    return filing 

# Getting SEC filing object
async def get_sec_filing_object(filing_info : FilingObject):
    """
    Load a custom CompanyFiling object from a ticker symbol and year
    
    Parameters
    ----------
    ticker : str
        The ticker symbol of the company to retrieve
    filing_date : int, optional
        The year of the filing to retrieve. If not provided, the latest filing will be retrieved
    
    Returns
    -------
    CustomCompanyFiling
        A custom CompanyFiling object with the specified ticker and year
    """
    global sec_rate_limit, sec_rate_limit_counter
    if sec_rate_limit_counter >= sec_rate_limit:
        print("SEC rate limit exceeded")

    while sec_rate_limit_counter >= sec_rate_limit:
        await asyncio.sleep(0)
    try:

        sec_rate_limit_counter += 1
        launch_rate_count_timer(1)
        
        set_identity("{} {}".format("SECRag", "secrag.info@gmail.com"))
        entity: EntityData = await launch_rate_limited(lambda: get_entity(filing_info.cik), 3)
        await asyncio.sleep(0.1)

        sec_filing = entity.get_filings(form=filing_info.filing_type, date=filing_info.filing_date)[0]
       
        await asyncio.sleep(0)
        # Try retrieving financials. If it fails, return None 
        xbrl: Optional[Union[XBRLData, XBRLInstance]] = await launch_rate_limited(lambda: atry_except(lambda: sec_filing.xbrl()))

        await asyncio.sleep(0.1)
        if xbrl: 
            financials = Financials(xbrl)
        else: financials = None

        balance_sheet = try_except(lambda: financials.get_balance_sheet().get_dataframe())
        await asyncio.sleep(0)
        income_statement = try_except(lambda: financials.get_income_statement().get_dataframe())
        await asyncio.sleep(0)
        cash_flow_statement = try_except(lambda: financials.get_cash_flow_statement().get_dataframe())
        await asyncio.sleep(0)
        statement_of_changes_in_equity = try_except(lambda: financials.get_statement_of_changes_in_equity().get_dataframe())
        await asyncio.sleep(0)
        statement_of_comprehensive_income = try_except(lambda: financials.get_statement_of_comprehensive_income().get_dataframe())
        await asyncio.sleep(0)

        # Initialize the CustomCompanyFiling object to return
        markdown = await launch_rate_limited_sync_func(lambda: sec_filing.markdown())        
        sec_filing_object = SECFilingObject(
            filing = sec_filing,
            file_number=sec_filing.file_number, 
            filing_html = "",
            markdown = markdown,
            cik=sec_filing.cik, 
            ticker=filing_info.ticker, 
            filing_type=filing_info.filing_type,
            filing_date=filing_info.filing_date, 
            filing_year=str(sec_filing.filing_date.year),
            company_name=sec_filing.company,
            balance_sheet=balance_sheet,
            income_statement=income_statement,
            cash_flow_statement=cash_flow_statement,
            statement_of_changes_in_equity=statement_of_changes_in_equity,
            statement_of_comprehensive_income=statement_of_comprehensive_income 
        )
        await asyncio.sleep(0)
        

        return sec_filing_object
    except Exception as e: 
        log('info', traceback.format_exc())
        log('info', str(e))
        print(traceback.format_exc(),str(e))


# Custom character text splitter for SEC filings
async def filing_splitter(filing : SECFilingObject, fin_statements, chunk_size = 10000, chunk_overlap = 3, table_prepend_k = 3, verbose = False):
    """
    Split a filing object into chunks based on its structure and financial statements.

    This function takes a filing object and its associated financial statements, and splits the filing into chunks based on its structure.
    It generates chunks for the intro, financials, and outro sections of the filing, and returns a list of final chunks.

    Args:
        filing (CustomCompanyFiling): The filing object to be split.
        fin_statements: The financial statements associated with the filing.
        chunk_size (int, optional): The maximum size of each chunk. Defaults to 10000.
        chunk_overlap (int, optional): The number of rows to overlap between chunks. Defaults to 3.
        table_prepend_k (int, optional): The number of rows to prepend to each table chunk. Defaults to 3.
        verbose (bool, optional): Whether to print verbose output. Defaults to False.

    Returns:
        list: A list of final chunks, where each chunk is a dictionary containing the chunk's metadata, length, and text.
    """
    metadata = "Misc" 
    data = [] # Stores EDGARTOOL chunks and their text lengths
    final_chunks = [] # Stores final chunks  

    filing_object = filing.filing.obj() # Convert filing to EDGARTOOLS filing object
    await asyncio.sleep(0)

    chunked_document = filing_object.chunked_document # Convert EDGARTOOLS object to EDGARTOOLS chunks
    await asyncio.sleep(0)

    structure = filing_object.structure # Retrieve EDGARTOOLS filing object's structure

    # Generate intro and outro chunks (outro chunks are not used)
    intro_chunks = [] # Intro chunks list
    outro_chunks = [] 
    chunk_buffer = "" 
    intro_complete = False
    rows = []

    # Convert chunked EDGARTOOLS object to dataframe
    chunked_document_df = chunked_document.as_dataframe()

    # Convert rows to list
    for _ , row in chunked_document_df.iterrows():
        await asyncio.sleep(0)
        rows.append(row)

    # Detects input and output sections in row
    for i, row in enumerate(rows):
        await asyncio.sleep(0)
        # Intro and outro rows have no noted filing Item number
        if row["Item"] == "" or row["Item"] == None:
            # Flag is not raised meaning we are currently processing Intro part
            if not intro_complete:
                # Add to buffer if it is shorter than set chunk size
                if len(chunk_buffer) < chunk_size:
                    chunk_buffer += row["Text"] + "\n"
                # Buffer is full
                else:
                    # Add to intro chunks list
                    intro_chunks.append(chunk_buffer)
                    # Empty the buffer
                    chunk_buffer = ""
                    # Prepend certain number of last EDGARTOOLS chunk of the created intro chunk
                    # to the buffer for creating an overlap between chunks 
                    for prep in range(chunk_overlap):
                        await asyncio.sleep(0)
                        if i - (chunk_overlap - prep) > 0:
                            chunk_buffer += rows[i - (chunk_overlap - prep)]["Text"]+"\n"
            # Flag is raised, therfore we are processing outro
            else:    
                if len(chunk_buffer) < chunk_size:
                    chunk_buffer += row["Text"] + "\n"
                # Buffer is full
                else:
                    # Add to outro chunks list
                    outro_chunks.append(chunk_buffer)
                    # Empty the buffer
                    chunk_buffer = ""
                    # Prepend certain number of last EDGARTOOLS chunk of the created outro chunk
                    # to the buffer for creating an overlap between chunks 
                    for prep in range(chunk_overlap):
                        await asyncio.sleep(0)
                        if i - (chunk_overlap - prep) > 0:
                            chunk_buffer += rows[i - (chunk_overlap - prep)]["Text"]+"\n"
                if i == len(rows) - 1:
                    outro_chunks.append(chunk_buffer)

        # We got to the first chunk that was identified to be a part of a filing's item
        else: 
            # Append the intro chunk buffer for the last time
            if not intro_complete: 
                intro_chunks.append(chunk_buffer)
                chunk_buffer = ""   
                intro_complete = True

    # Initialize metadata model
    chunk_metadata_model = {
        "ticker": filing.ticker, 
        "date": filing.filing_date,
        "form": filing.filing_type,
        "year": filing.filing_year,
        "chunk_description": "",
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        "table_prepend_k": table_prepend_k
    }

    # Generate chunks for financials
    for key, _ in fin_statements.items():
        await asyncio.sleep(0)
        # Sometimes it returns tuples
        if isinstance(fin_statements[key], tuple):
            # Process each element of a tuple
            for damn_tuple in fin_statements[key]:
                # If item is a dataframe, convert it to markdown
                # Otherwise, just return "no data"
                text = damn_tuple.to_markdown() if type(damn_tuple) is pd.DataFrame and not damn_tuple.empty  else "no data"
                # Update metadata model
                chunk_metadata_model["chunk_description"] = key
                # Create final chunk
                fin_chunk = {
                    "metadata": dict(chunk_metadata_model), # dict() is necessary
                    "length": len(text),
                    "text": text
                }
                final_chunks.append(fin_chunk)
        else:
            # If item is a dataframe, convert it to markdown
            # Otherwise, just return "no data"
            text = fin_statements[key].to_markdown() if type(fin_statements[key]) is pd.DataFrame and not fin_statements[key].empty  else "no data"
            # Update metadata model
            chunk_metadata_model["chunk_description"] = key
            # Create final chunk
            fin_chunk = {
                "metadata": dict(chunk_metadata_model), # dict() is necessary
                "length": len(text),
                "text": text
            }
            final_chunks.append(fin_chunk)

    # Process intro chunks
    for intro in intro_chunks:
        await asyncio.sleep(0)
        chunk_metadata_model["chunk_description"] = "Overview_of_the_document"
        intro_chunk = {
                "metadata": dict(chunk_metadata_model),
                "length": len(intro),
                "text": intro
            }
        final_chunks.append(intro_chunk)

    # Process filing's items chunks
    for item in chunked_document.list_items():
        await asyncio.sleep(0)
        # Get item chapter description
        item_data = structure.get_item(item)
        if item_data != None: 
            metadata = item_data["Description"] 

        # Get EDGARTOOLS chunks for particular filing item
        chunks = chunked_document.chunks_for_item(item)

        # Create data list
        for _, chunk in enumerate(chunks):
                await asyncio.sleep(0)
                for j, row in enumerate(chunk):
                    await asyncio.sleep(0)
                    data.append({
                        "object": row,
                        "len": len(row.to_markdown())
                    })
                
        # Initialize item chunk buffer
        item_chunk_buffer = {
            "objects": [],
            "len": 0
        }

        chunk_number = 0
        i = 0
        max_items = len(data)

        # Process item chunks
        while i < max_items:
            # If we are not in the beginning of the chunk and the current EDGARTOOLS chunk is a table
            if i != 0 and len(item_chunk_buffer["objects"]) == 0 and isinstance(data[i]["object"], TableBlock):
                # Prepend some EDGARTOOLS chunks to this chunk
                # This ensures that if table had headings they are included in the chunk
                for prep in range(table_prepend_k):
                    # Avoid index out of range
                    if i - (table_prepend_k - prep) <= 0:
                        continue
                    # Avoid table chunks
                    if isinstance(data[i-(table_prepend_k - prep)]["object"], TableBlock):
                        continue
                    # Append text chunks that might be table headers
                    else:
                        item_chunk_buffer["objects"].append(data[i-(table_prepend_k - prep)]["object"])
                        item_chunk_buffer["len"] += data[i-(table_prepend_k - prep)]["len"]

                item_chunk_buffer["objects"].append(data[i]["object"])
                item_chunk_buffer["len"] += data[i]["len"]

            else: 
                # Just a regular chunk, add it to the buffer
                item_chunk_buffer["objects"].append(data[i]["object"])
                item_chunk_buffer["len"] += data[i]["len"]
            
            # Check if buffer is full
            if item_chunk_buffer["len"] > chunk_size: 
                # Append some EDGARTOOLS chunks for overlap
                for app in range(chunk_overlap):
                    await asyncio.sleep(0)
                    # Avoid index out of range
                    if i + app + 1 >= max_items:
                        break
                    # Avoid table chunks
                    if isinstance(data[i+app+1]["object"], TableBlock):
                        break
                    # Append chunks
                    else:
                        item_chunk_buffer["objects"].append(data[i+app+1]["object"])
                        item_chunk_buffer["len"] += data[i+app+1]["len"]
                
                # Update metadata model. Make sure to special characters with underscores
                chunk_metadata_model["chunk_description"] = re.sub(r'[^A-Za-z0-9 ]+', '', metadata).replace(" ", "_")
                
                # Store chunk
                final_chunks.append(
                    {
                        "metadata": dict(chunk_metadata_model),
                        "length": item_chunk_buffer["len"],
                        "text": "\n".join([obj.to_markdown() for obj in item_chunk_buffer["objects"]])
                    }
                )

                # Reset buffer
                item_chunk_buffer["objects"] = []
                item_chunk_buffer["len"] = 0
                # Increment chunk count
                chunk_number += 1
            # Go to next EDGARTOOLS chunk
            i += 1
            await asyncio.sleep(0)  # This yields control back to the event loop
        # Ended processing EDGARTOOLS chunks for Item 
        # Reset buffer 
        data = []

    # Process outro chunks
    for outro in outro_chunks:
        await asyncio.sleep(0)
        chunk_metadata_model["chunk_description"] = "Miscellaneous"
        outro_chunk = {
                "metadata": dict(chunk_metadata_model),
                "length": len(outro),
                "text": outro
            }
        final_chunks.append(outro_chunk)
    
    return final_chunks
