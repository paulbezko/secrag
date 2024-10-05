import os
import re
from edgar.core import set_identity
from edgar.entities import Company
from edgar.htmltools import TableBlock
from edgar.financials import Financials
import pandas as pd
import json
from token_count import TokenCount
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .misc_utils import try_or, compare_year

# Get the current directory of the script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Go one level up (parent directory)
parent_dir = os.path.dirname(current_dir)

# Convert to string if needed
parent_dir = str(parent_dir)

# This class is made for convenience. It stores all important filing data for the project's implementation
class CustomCompanyFiling():
    def __init__(self, filing, markdown, file_number, filing_html, cik, ticker, filing_date, company_name, filing_year, balance_sheet = None, income_statement = None, cash_flow_statement = None, statement_of_comprehensive_income = None, statement_of_changes_in_equity = None):
        self.filing = filing 
        self.ticker = ticker
        self.markdown = markdown
        self.file_number = file_number
        self.filing_date = filing_date
        self.cik = cik
        self.html = filing_html
        self.company_name = company_name
        self.filing_year = filing_year
        self.balance_sheet = balance_sheet,
        self.statement_of_comprehensive_income = statement_of_comprehensive_income
        self.statement_of_changes_in_equity = statement_of_changes_in_equity
        self.income_statement = income_statement,
        self.cash_flow_statement = cash_flow_statement,
    
    def as_documents(self, chunk_size = 10000, chunk_overlap = 3, table_prepend_k = 3):
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
        return filing_to_embeddings_input(self, self.get_financials(), chunk_size, chunk_overlap, table_prepend_k)
   
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
    


def get_filing_years_for_ticker(ticker):
    """
    Gets all the filing years for a given ticker
    
    Args:
        ticker (str): The ticker symbol for the company
    
    Returns:
        list: A list of strings of the years for which there are filings for the given ticker
    """
    set_identity("{} {}".format("marks", "marksdocenko@outlook.com"))

    filings = Company(ticker).get_filings(form="10-K")
    
    years = []

    for i in filings:
        years.append(str(i.filing_date.year))

    return years

def get_filing_for_a_year(filings, year):
    """
    Finds a filing for a given year
    
    Args:
        filings (list): A list of filing objects
        year (str): The year for which to find a filing
    
    Returns:
        CompanyFiling: A CompanyFiling object for the given year
    """
    for filing in filings:
        if compare_year(filing.filing_date, year):
            return filing


# Load SEC filing
def load_sec(ticker, filing_year = None):
    """
    Load a custom CompanyFiling object from a ticker symbol and year
    
    Parameters
    ----------
    ticker : str
        The ticker symbol of the company to retrieve
    filing_year : int, optional
        The year of the filing to retrieve. If not provided, the latest filing will be retrieved
    
    Returns
    -------
    CustomCompanyFiling
        A custom CompanyFiling object with the specified ticker and year
    """

    # Lowercase the ticker
    ticker = ticker.lower()
    
    filing_tl = sec_search(ticker=ticker, name="marks", email="marksdocenko@outlook.com", filing_year=filing_year)

    # Try retrieving financials. If it fails, return None    
    financials = try_or(lambda: Financials(filing_tl.xbrl()))
    balance_sheet = try_or(lambda: financials.get_balance_sheet().get_dataframe())
    income_statement = try_or(lambda: financials.get_income_statement().get_dataframe())
    cash_flow_statement = try_or(lambda: financials.get_cash_flow_statement().get_dataframe())
    statement_of_changes_in_equity = try_or(lambda: financials.get_statement_of_changes_in_equity().get_dataframe())
    statement_of_comprehensive_income = try_or(lambda: financials.get_statement_of_comprehensive_income().get_dataframe())
    
    # Initialize the CustomCompanyFiling object to return
    custom_filing = CustomCompanyFiling(
        filing = filing_tl,
        file_number=filing_tl.file_number, 
        filing_html = "",
        markdown = filing_tl.markdown(),
        cik=filing_tl.cik, 
        ticker=ticker, 
        filing_date=filing_tl.filing_date, 
        filing_year = filing_year,
        company_name=filing_tl.company,
        balance_sheet=balance_sheet,
        income_statement=income_statement,
        cash_flow_statement=cash_flow_statement,
        statement_of_changes_in_equity=statement_of_changes_in_equity,
        statement_of_comprehensive_income=statement_of_comprehensive_income 
    )

    return custom_filing


def sec_search(ticker, name, email, filing_year = None):
    """
    Search for a company's latest 10-K filing using the EDGAR API.

    Parameters
    ----------
    ticker : str
        The ticker symbol of the company to search for
    name : str
        The name of the person making the query
    email : str
        The email address of the person making the query
    filing_year : int, optional
        The year of the filing to search for. If not provided, the latest filing will be returned

    Returns
    -------
    CompanyFiling
        A CompanyFiling object of the latest 10-K filing found
    """
    
    set_identity("{} {}".format(name, email))

    try:
        filings = Company(ticker).get_filings(form="10-K")
        if filing_year:
            return get_filing_for_a_year(filings, filing_year)
        else:
            return filings[0]
        return filings
    except AttributeError:
        raise Exception("Invalid ticker - {}".format(ticker))


def save_financial_data(data, name, ticker):
    """
    Save financial data to a file in the financials directory.

    Parameters
    ----------
    data : pandas.DataFrame
        A DataFrame containing financial data
    name : str
        A descriptive name for the data
    ticker : str
        The ticker symbol of the company the data is for

    Returns
    -------
    None
    """

    json_string = df_to_nested_json(data) 
    with open(parent_dir + "/financials/{}_{}.json".format(ticker, name), 'w+', encoding='utf-8') as file:
        json.dump(json_string, file, indent=4)


def df_to_nested_json(df):
    """
    Convert a pandas DataFrame to a nested JSON object.
    
    Can be used for returning financials as JSON upon request.

    This function takes a DataFrame and creates a nested JSON object where the first level of keys
    are the column headers that end with a colon (:). The second level of keys are the column headers
    that do not end with a colon (:). The value of the second level of keys is the row of data from the
    DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame to convert to a nested JSON object

    Returns
    -------
    result : dict
        A nested JSON object where the first level of keys are the column headers that end with a colon (:)
        and the second level of keys are the column headers that do not end with a colon (:). The value of
        the second level of keys is the row of data from the DataFrame
    """
    result = {}
    current_category = None

    # Iterate through the dataframe
    for label, row in df.iterrows():
        # Check if the label ends with ":"
        if label.endswith(":"):
            current_category = label
            result[current_category] = {}
        else:
            # If no category is found, just continue
            if current_category is None:
                continue
            # Add the row to the current category
            result[current_category][label] = row.to_dict()
    
    return result


def filing_intro_outro_generator(chunked_document, chunk_size = 10000, chunk_overlap = 3):
    """
    Generate intro and outro chunks from a chunked EDGARTOOLS document.

    This function takes a chunked EDGARTOOLS document, splits it into intro and outro sections,
    and returns the intro chunks and outro text.

    Args:
        chunked_document: A chunked EDGARTOOLS object.
        chunk_size (int, optional): The maximum size of each intro chunk. Defaults to 10000.
        chunk_overlap (int, optional): The number of rows to overlap between intro chunks. Defaults to 3.

    Returns:
        tuple: A tuple containing two elements:
            - intro (list): A list of intro chunks.
            - outro (str): The outro text.
    """

    intro = [] # Intro chunks list
    intro_chunk_buffer = "" 
    outro = ""
    intro_complete = False
    rows = []

    # Convert chunked EDGARTOOLS object to dataframe
    chunked_document_df = chunked_document.as_dataframe()

    # Convert rows to list
    for _ , row in chunked_document_df.iterrows():
        rows.append(row)

    # Detects input and output sections in row
    for i, row in enumerate(rows):
        # Intro and outro rows have no noted filing Item number
        if row["Item"] == "" or row["Item"] == None:
            # Flag is not raised meaning we are currently processing Intro part
            if not intro_complete:
                # Add to buffer if it is shorter than set chunk size
                if len(intro_chunk_buffer) < chunk_size:
                    intro_chunk_buffer += row["Text"] + "\n"
                # Buffer is full
                else:
                    # Add to intro chunks list
                    intro.append(intro_chunk_buffer)
                    # Empty the buffer
                    intro_chunk_buffer = ""
                    # Prepend certain number of last EDGARTOOLS chunk of the created intro chunk
                    # to the buffer for creating an overlap between chunks 
                    for prep in range(chunk_overlap):
                        if i - (chunk_overlap - prep) > 0:
                            intro_chunk_buffer += rows[i - (chunk_overlap - prep)]["Text"]+"\n"
            # Flag is raised, therfore we are processing outro
            else:    
                outro += row["Text"] + "\n"
        # We got to the first chunk that was identified to be a part of a filing's item
        else: 
            # Append the intro chunk buffer for the last time
            if not intro_complete: 
                intro.append(intro_chunk_buffer)
                intro_chunk_buffer = ""   
                intro_complete = True
    
    return intro, outro


def filing_to_embeddings_input(filing, financials, chunk_size = 10000, chunk_overlap = 3, table_prepend_k = 3):
    """
    Convert a filing object and its associated financials into a list of Document objects for embedding.

    This function takes a filing object and its associated financials, and uses the `filing_splitter` function to split the filing into chunks.
    It then composes a list of `Document` objects, where each object contains the text content of a chunk and its associated metadata.

    Args:
        filing (CustomCompanyFiling): The filing object to be converted.
        financials (Financials): The associated financials object.
        chunk_size (int, optional): The maximum size of each chunk. Defaults to 10000.
        chunk_overlap (int, optional): The number of rows to overlap between chunks. Defaults to 3.
        table_prepend_k (int, optional): The number of rows to prepend to each table chunk. Defaults to 3.

    Returns:
        list: A list of `Document` objects, where each object contains the text content of a chunk and its associated metadata.
    """

    # Use custom filing splitter for chunking
    final_chunks = filing_splitter(filing, financials, chunk_size, chunk_overlap, table_prepend_k)

    output = []

    # Compose list of documents objects
    for i in final_chunks:
        output.append(Document(
            page_content=i["text"],
            metadata=i["metadata"]
        ))
    
    return output
    

def filing_splitter(filing : CustomCompanyFiling, fin_statements, chunk_size = 10000, chunk_overlap = 3, table_prepend_k = 3, verbose = False):
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

    # Convert filing to EDGARTOOLS filing object
    filing_object = filing.filing.obj()
    # Convert EDGARTOOLS object to EDGARTOOLS chunks
    chunked_document = filing_object.chunked_document
    # Retrieve EDGARTOOLS filing object's structure
    structure = filing_object.structure

    # Generate intro and outro chunks (outro chunks are not used)             
    intro_chunks, _ = filing_intro_outro_generator(chunked_document, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    
    # Initialize metadata model
    metadata_model = {
        "ticker": filing.ticker, 
        "year": filing.filing_year,
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        "table_prepend_k": table_prepend_k,
        "chapter_description": ""
    }

    # Generate chunks for financials
    for key, _ in fin_statements.items():
        # Sometimes it returns tuples
        if isinstance(fin_statements[key], tuple):
            # Process each element of a tuple
            for damn_tuple in fin_statements[key]:
                # If item is a dataframe, convert it to markdown
                # Otherwise, just return "no data"
                text = damn_tuple.to_markdown() if type(damn_tuple) is pd.DataFrame and not damn_tuple.empty  else "no data"
                # Update metadata model
                metadata_model["chapter_description"] = key
                # Create final chunk
                fin_chunk = {
                    "metadata": dict(metadata_model), # dict() is necessary
                    "length": len(text),
                    "text": text
                }
                final_chunks.append(fin_chunk)
        else:
            # If item is a dataframe, convert it to markdown
            # Otherwise, just return "no data"
            text = fin_statements[key].to_markdown() if type(fin_statements[key]) is pd.DataFrame and not fin_statements[key].empty  else "no data"
            # Update metadata model  
            metadata_model["chapter_description"] = key
            # Create final chunk
            fin_chunk = {
                "metadata": dict(metadata_model), # dict() is necessary
                "length": len(text),
                "text": text
            }
            final_chunks.append(fin_chunk)

    # Process intro chunks
    for intro in intro_chunks:
        metadata_model["chapter_description"] = "Overview_of_the_document"
        intro_chunk = {
                "metadata": dict(metadata_model),
                "length": len(intro),
                "text": intro
            }
        if verbose:
            print("----------\n\n",intro_chunk)
        final_chunks.append(intro_chunk)


    # Process filing's items chunks
    for item in chunked_document.list_items():
        # Get item chapter description
        item_data = structure.get_item(item)
        if item_data != None: 
            metadata = item_data["Description"] 

        # Get EDGARTOOLS chunks for particular filing item
        chunks = chunked_document.chunks_for_item(item)

        # Create data list
        for _, chunk in enumerate(chunks):
                for j, row in enumerate(chunk):
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
                
                if verbose:
                    print("------\n\n",item, "Chunk", chunk_number )
                    for j in item_chunk_buffer["objects"]:
                        print(j)
                    print("Len:",item_chunk_buffer["len"])
                
                # Update metadata model. Make sure to special characters with underscores
                metadata_model["chapter_description"] = re.sub(r'[^A-Za-z0-9 ]+', '', metadata).replace(" ", "_")
                
                # Store chunk
                final_chunks.append(
                    {
                        "metadata": dict(metadata_model),
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
        # Ended processing EDGARTOOLS chunks for Item 
        # Reset buffer 
        data = []

    return final_chunks
    

def sec_chunker_text_size(chuncked_document):

    """
    (Used for performance testing)
    Compute the total text size of all EDGARTOOL chunks in a chunked document.

    Args:
        chuncked_document (ChunkedDocument): The chunked document to compute the total text size for.

    Returns:
        int: The total text size of all chunks in the chunked document.
    """
    chunked_document_df = chunked_document.as_dataframe()
    rows = []
    text_buffer = ""
    for _, row in chunked_document_df.iterrows():
        rows.append(row)
    for i, row in enumerate(rows):
        text_buffer += row["Text"]+"\n"
    
    return len(text_buffer)


if __name__ == "__main__":
    chunk_size=10000
    chunk_overlap=3
    table_prepend_k=3
    year = "2023"
    tickers = [
    # "UEC", 
    # "DAL", 
    "NKLA", 
    # "DJT", 
    # "SHW", 
    # "BA", 
    # "ONON", 
    # "WMT", 
    # "WTB",
    # "RCKT",

    ]
    dict_split_filing = {}
    for ticker in tickers:

        filing = load_sec(ticker, year)
        filing_object = filing.filing.obj()
        chunked_document = filing_object.chunked_document
        structure = filing_object.structure
        sec_chunker_size = sec_chunker_text_size(chunked_document)
        final_chunks = filing_splitter(chunked_document, structure, chunk_size, chunk_overlap, table_prepend_k)
        
        md_output = ""
        total_text = ""
        lengths = []
        tokens = []
        tc = TokenCount(model_name="gpt-4o-mini")
        for i, final_chunk in enumerate(final_chunks):
            metadata = final_chunk["metadata"]["chapter_description"]
            length = final_chunk["length"]
            lengths.append(length)
            chunk_text = final_chunk["text"]
            total_text += chunk_text + "\n"
            token_cnt = tc.num_tokens_from_string(chunk_text)
            tokens.append(token_cnt)
            md_output += f"# Chunk {i} Length {length}\n## Metadata: {metadata}\n## Length: {length}\n## Tokens: {token_cnt}\n## Text:\n{chunk_text}\n\n"

        total_tokens = tc.num_tokens_from_string(total_text)
        total_original_tokens = tc.num_tokens_from_string(filing.markdown)
        total_original_size = len(filing.markdown)
        total_size = len(total_text)
        avg_length = round(sum(lengths)/len(lengths))
        avg_tokens = round(sum(tokens)/len(tokens))
        md_output = f"# Overview\n## Filing: \n{ticker}-{year}\n## Config:\n- chunk_size={chunk_size}\n- chunk_overlap={chunk_overlap}\n- table_prepend_k={table_prepend_k}\n## Size stats:\n### Text size:\n- Original text size: {sec_chunker_size}\n- Splitter output text size: {total_size}\n### Total tokens:\n- Total original tokens: {total_original_tokens}\n- Total Embedding tokens: {total_tokens}\n### Chunk size stats:\n- Average length: {avg_length}\n- Average tokens: {avg_tokens}\n\n" + md_output
        with open(parent_dir + f"/filing_splitter_test_{ticker}-{year}.md", "w", encoding="utf-8") as f:
            f.write(md_output)



