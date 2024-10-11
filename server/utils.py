from email.mime.text import MIMEText
from psycopg2.extras import RealDictCursor
from datetime import datetime, timezone
from psycopg2 import OperationalError, InterfaceError
from flask import current_app

import psycopg2
import smtplib
import time
import jwt
import re
import os


def encode_token(payload):
    try: return jwt.encode(payload, current_app.config['JWT_SECRET'], algorithm="HS256")
    except Exception as error: return error


def decode_token(token):
    try: return jwt.decode(token, current_app.config['JWT_SECRET'], algorithms=["HS256"])
    except Exception as error: return error


def send_email_from_template(email, template, payload):
    
    if template == 'signUp':
        subject = 'Welcome to SkelTal!'
        body = f"Click the link below to verify your email address: {current_app.config['REDIRECT_URL']}/signup?token={payload}"

    elif template == 'resetPassword':
        subject = 'Reset Password'
        body = f"Click the link below to reset your password: {current_app.config['REDIRECT_URL']}/reset-password?token={payload}"

    elif template == 'changeEmail':
        subject = 'Change Email'
        body = f"Click the link below to confirm your email: {current_app.config['REDIRECT_URL']}/change-email?token={payload}"

    elif template == 'contact':
        subject = 'New contact request submitted.'
        body = payload

    else: return print('Error [Send Email]: Invalid email type')

    try:
        email_message = MIMEText(body)
        email_message['Subject'] = subject
        email_message['From'] = current_app.config['MAIL_SENDER_USER']
        email_message['To'] = email
        print(email)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(current_app.config['MAIL_SENDER_USER'], current_app.config['MAIL_SENDER_PASS'])
            smtp_server.send_message(email_message)

    except Exception as error:
        print('Error [Send Email]:', error)


def get_user_data(email, retries=3):

    attempt = 0
    while attempt < retries:
        try:
            connection = current_app.config['DB_CONNECTION']
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                return cursor.fetchone()
        
        except (OperationalError, InterfaceError) as conn_error:
            print(f"Connection error [Attempt {attempt + 1}/{retries}]: {conn_error}")
            attempt += 1
            reconnect_to_db()
            time.sleep(2)  # Optional delay before retrying
        
        except Exception as error:
            print('Error [Get User Data]:', error)
            break
    
    print("Failed to retrieve user data after multiple attempts.")
    return None


def get_user_data_stripe(stripe_user_id, retries=3):

    attempt = 0
    while attempt < retries:
        try:
            connection = current_app.config['DB_CONNECTION']
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE stripe_user_id = %s", (stripe_user_id,))
                return cursor.fetchone()
        
        except (OperationalError, InterfaceError) as conn_error:
            print(f"Connection error [Attempt {attempt + 1}/{retries}]: {conn_error}")
            attempt += 1
            reconnect_to_db()
            time.sleep(2)  # Optional delay before retrying
        
        except Exception as error:
            print('Error [Get User Data]:', error)
            break
    
    print("Failed to retrieve user data after multiple attempts.")
    return None


def execute_query(query, params, retries=3):
    attempt = 0
    while attempt < retries:
        try:
            connection = current_app.config['DB_CONNECTION']
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                connection.commit()
            return  # Exit function after successful execution
        
        except (OperationalError, InterfaceError) as conn_error:
            print(f"Connection error [Attempt {attempt + 1}/{retries}]: {conn_error}")
            attempt += 1
            reconnect_to_db()
            time.sleep(2)  # Optional delay before retrying
        
        except Exception as error:
            print('Error [Execute Query]:', error)
            break  # Exit loop on unexpected exceptions

    print("Failed to execute query after multiple attempts.")


def reconnect_to_db():
    try:
        connection = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            cursor_factory=RealDictCursor
        )
        current_app.config['DB_CONNECTION'] = connection
        print("Reconnected to the database.")
    except OperationalError as error:
        print("Error [Reconnect DB]:", error)


def check_timestamp(timestamp):

    if datetime.now(timezone.utc) > datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc): return False
    else: return True





# Dashboard util section
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel
from . import socketio
from typing import Literal
from edgar.core import set_identity
from edgar.entities import Company
from edgar.financials import Financials
from langchain_core.documents import Document
import pandas as pd
from edgar.htmltools import TableBlock


# Creating a class for filing information
class FilingObject():
    def __init__(self, ticker, filing_date, filing_type, filing_year) -> None:
        self.ticker = ticker
        self.filing_date = filing_date
        self.filing_type = filing_type
        self.filing_year = filing_year


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
    
    def get_documents(self, chunk_size = 10000, chunk_overlap = 3, table_prepend_k = 3):
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
        list_chunks = filing_splitter(self, self.get_financials(), chunk_size, chunk_overlap, table_prepend_k)
        list_documents = []
        for chunk in list_chunks:
            list_documents.append(Document(
                page_content=chunk["text"],
                metadata=chunk["metadata"]
            ))
        return list_documents


# Creating a class for rag needed pydantic boolean
class RagNeeded(BaseModel):
    relevant: bool

# Pydantic model for the Contextual Question LLM
from typing import List, Optional, Literal
class KewordsFilingTables(BaseModel):
    keywords: str
    filing_table_selection: List[Literal[
        "balance_sheet", 
        "income_statement", 
        "cash_flow_statement", 
        "statement_of_changes_in_equity", 
        "statement_of_comprehensive_income"
    ]] = []


# Getting assistant response
def get_assistant_response(user_prompt, message_history, user_email, filing_id, socket_id, filing_date):

    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0, openai_api_key='sk-proj-0U1etEdNPyfN0tEvklyVT3BlbkFJ0899XXITmyGhvlsfA7eS')
    chunk_size = 10000
    k = 3
    chunk_overlap = 3
    table_prepend_k = 3

    # Creating filing info object
    filing = get_filing(filing_id, filing_date)

    # Reformatting user message history and most recent message into a single prompt
    system_prompt = f"""
    You are presented with a current request and the latest chat messages from a human. Your task is to assess whether the current request is a follow-up to one of the latest chat messages.

    To determine if the current request is a follow-up, consider the following:

    - It qualifies as a follow-up if it implicitly or explicitly asks for further detail about the previous topic, requests additional formatting (e.g., "return as markdown"), or seeks clarification on a specific aspect of the last prompt.
    - If the current request relates to previous messages and pertains specifically to SEC filings or financial statements, it may be relevant to the filing ID: {filing_id}. Reformulate it to include relevant context only if necessary.
    - **If the current request is about general financial concepts (e.g., explaining what a balance sheet is or the significance of a 10-Q), do not include historical context in the reformulation.**
    - Do not classify it as a follow-up if the request addresses a different financial statement, topic, or request that doesn’t build upon the previous requests.

    If the current request qualifies as a follow-up, reformulate it to clearly state what information is being requested, ensuring that no irrelevant historical context is included if the question is general.
    If the current request does not qualify as a follow-up, return it as is. Return nothing else but the request.

    Latest chat messages: {message_history}
    Request: {user_prompt}
    """
    reformulated_prompt = llm.invoke(system_prompt).content

    # Determining if RAG is needed for the answer
    system_prompt = f"""
    You are an expert in financial documents, particularly SEC filings such as 10-K and 10-Q reports. \
    The user is referencing the filing ID: {filing_id}. \
    Based on the following message, determine if the user is asking for information related to financial documents \
    specifically associated with this filing ID. \
    This includes details like balance sheets, income statements, cash flow statements, and any other relevant financial data typically found in SEC filings.
    
    Message: {reformulated_prompt}
    """
    bool_rag_needed = llm.with_structured_output(RagNeeded).invoke(system_prompt).relevant

    # Handle a case where the reformulated prompt is relevant to the filing
    if bool_rag_needed:
        
        # Get keywords and filing table selection
        system_prompt = f"""
            You are a helpful assistant. Your task is to analyze the user's prompt and derive any useful keywords that can be used to answer their question.
            If the user is asking about specific financial statements like a balance sheet, income statement, etc., return those financial statements. If the user asks for multiple financial statements, return all that are relevant.

            Only return a filing_table_selection if the user is asking for or implying financial data related to a specific financial report, like a balance sheet or income statement. If no financial statement is implied, leave filing_table_selection empty.

            The output should be structured as:
                keywords: str
                filing_table_selection: Optional[List[Literal["balance_sheet", "income_statement", "cash_flow_statement", "statement_of_changes_in_equity", "statement_of_comprehensive_income"]]] = None

            User prompt:
            {reformulated_prompt}
            """
        prompt_keywords_and_filing_tables = llm.with_structured_output(KewordsFilingTables).invoke(system_prompt)

        # Getting vectorsore to get context chunks from
        vectorstore = get_vectorstore(filing, new_chat=False, chunk_size=chunk_size, chunk_overlap=chunk_overlap, k=1, table_prepend_k=table_prepend_k)

        # Initializing metadata model
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

        # Initializing empty context string
        list_context_chunks = ""

        # Fetching filing tables for context
        if len(prompt_keywords_and_filing_tables.filing_table_selection) > 0:
            for table in prompt_keywords_and_filing_tables.filing_table_selection:
                chunk_metadata_model = {
                    "ticker": chunk_metadata_model["ticker"], 
                    "year": chunk_metadata_model["year"],
                    "chunk_size": chunk_metadata_model["chunk_size"],
                    "chunk_overlap": chunk_metadata_model["chunk_overlap"],
                    "table_prepend_k": chunk_metadata_model["table_prepend_k"],
                    "chunk_description": table,
                }

                list_retrieved_chunks = vectorstore.similarity_search("", k=1, fetch_k=1000, filter=chunk_metadata_model)
                for chunk in list_retrieved_chunks:
                    list_context_chunks += chunk.page_content + "\n"
        
        # Fetching regular contexts from keywords
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

        list_retrieved_chunks = vectorstore.similarity_search_with_score(prompt_keywords_and_filing_tables.keywords, k=k, filter=chunk_metadata_model, fetch_k=1000)
        for chunk in list_retrieved_chunks:
            if chunk[0].page_content not in list_context_chunks:
                list_context_chunks += chunk.page_content + "\n"
            
        system_prompt = f"""
        You are a highly knowledgeable financial assistant who helps users with financial queries, especially related to SEC filings, financial statements, and corporate reports. \
        Your role is to provide clear, concise, and detailed answers to any financial questions the user may have. \
        Your goal is to provide relevant financial data related to the user's prompt. \
        The context provided is from the SEC filing for {filing.ticker} (ticker: {filing.ticker}, filing date: {filing.filing_date}). \
        The context is as follows: {list_context_chunks}

        User prompt: {reformulated_prompt}
        """

        buffer = ""
        for chunk in llm.stream(system_prompt):
            buffer += chunk.content
            socketio.emit('llm_response', {'word': chunk.content}, to=socket_id)


    # Handle a case where the reformulated prompt is unrelated to the filing itself
    else:

        system_prompt = f"""
        You are a highly knowledgeable financial assistant who helps users with financial queries, especially related to SEC filings, financial statements, and corporate reports. \
        Your role is to provide clear, concise, and detailed answers to any financial questions the user may have. \
        However, if the user asks a question unrelated to finance, your goal is to politely steer the conversation back to financial topics, gently reminding the user that you specialize in finance. \
        You may give a brief, polite response to the unrelated question, but then guide the user back to finance-related matters.

        User prompt: {reformulated_prompt}
        """
        buffer = ""

        for chunk in llm.stream(system_prompt):
            buffer += chunk.content
            socketio.emit('llm_response', {'word': chunk.content}, to=socket_id)



def get_vectorstore(
        filing : FilingObject, 
        new_chat : bool,

        # Optional args
        
        chunk_size = 10000, 
        chunk_overlap = 3, 
        k = 1, 
        table_prepend_k = 3, 
        splitter_mode = "edgartools"
    ):
    """
    Manages vectorstore for a given filing and configuration.

    Args:
        filing (CustomCompanyFiling): The filing object to be converted.
        chunk_size (int, optional): The maximum size of each chunk. Defaults to 5000.
        chunk_overlap (int, optional): The number of rows to overlap between chunks. Defaults to 1000.
        k (int, optional): The number of similar documents to return. Defaults to 1.
        table_prepend_k (int, optional): The number of rows to prepend to each table chunk. Defaults to 3.
        splitter_mode (str, optional): The text splitter to use. Defaults to "edgartools".

    Returns:
        FAISS: The vectorstore object.
    """

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

    print(chunk_metadata_model)

    vectorstore_dir = "server/memory/vectorstore"
    embeddings = OpenAIEmbeddings()

    # Check if vectorstore exists
    if os.path.exists(vectorstore_dir):

        # Load vectorstore
        vectorstore = FAISS.load_local(vectorstore_dir, embeddings=embeddings, allow_dangerous_deserialization=True)

        # Check if embedding already exists for a given filing and embedding config
        if new_chat:
            check_for_existing_embeddings = vectorstore.similarity_search("", k=3, filter=chunk_metadata_model)
            # Case when embedding does not exist
            if len(check_for_existing_embeddings) == 0:
                sec_filing_object = get_sec_filing_object(filing)
                chunks = sec_filing_object.get_documents(chunk_size, chunk_overlap, table_prepend_k)
                vectorstore.add_documents(chunks)
                vectorstore.save_local(vectorstore_dir)
                print(f"Updated Vectorstore for {filing.ticker}-{filing.filing_date}, {chunk_size}, {chunk_overlap}, {table_prepend_k}")
            # Case when embedding already exists       
            else:
                print(f"Embedding already exists for {filing.ticker}-{filing.filing_date}, {chunk_size}, {chunk_overlap}, {table_prepend_k}")

    # Create vectorstore if it doesn't exist
    else:
        # Create new embedding and vectorstore, and save the vectorstore 
        sec_filing_object = get_sec_filing_object(filing)
        chunks = sec_filing_object.get_documents(chunk_size, chunk_overlap, table_prepend_k)
        vectorstore = FAISS.from_documents(chunks, embedding=embeddings)
        vectorstore.save_local(vectorstore_dir)
        print(f"Created Vectorstore, added {filing.ticker}-{filing.filing_date}, {chunk_size}, {chunk_overlap}, {table_prepend_k}")

    return vectorstore




import threading
class RateLimiter:
    def __init__(self, rate_limit):
        self.rate_limit = rate_limit  # Maximum number of calls per second
        self.semaphore = threading.Semaphore(rate_limit)
        self.lock = threading.Lock()
        self.reset_time = time.time() + 1

    def current_time(self):
        """Helper function to get current time in yyyy-mm-dd : hh-mm-ss.ms format."""
        return datetime.now().strftime('%Y-%m-%d : %H-%M-%S.%f')[:-3]

    def acquire(self):
        with self.lock:
            current_time = time.time()
            if current_time >= self.reset_time:
                # Reset the semaphore and reset_time every second
                self.semaphore = threading.Semaphore(self.rate_limit)
                self.reset_time = current_time + 1

        # Check if semaphore is already exhausted
        if self.semaphore._value == 0:
            print(f"Rate limit exceeded at {self.current_time()} - waiting for capacity")

        # Block until semaphore is acquired (no timeout, it will wait)
        self.semaphore.acquire()
        # print(f"Semaphore acquired at {self.current_time()}")

    def release(self):
        self.semaphore.release()


def try_except(func, default=None, expected_exc=(Exception,)):
    """
    Tries to execute a given function, and if it fails with one of the specified
    exceptions, returns a default value instead.

    :param func: The function to try to execute
    :param default: The value to return if an exception is raised
    :param expected_exc: A tuple of exception types that are expected to be raised
    :return: The result of the function, or the default value if an exception was
             raised
    """
    try: return func()
    except expected_exc: return default






def get_sec_filing_object(filing_info : FilingObject):
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

    rate_limiter = RateLimiter(rate_limit=2)
    rate_limiter.acquire()
    try:

        set_identity("{} {}".format("SECRag", "secrag.info@gmail.com"))
        sec_filing = Company(filing_info.ticker).get_filings(form=filing_info.filing_type, date=filing_info.filing_date)[0]

        # Try retrieving financials. If it fails, return None    
        financials = try_except(lambda: Financials(sec_filing.xbrl()))
        balance_sheet = try_except(lambda: financials.get_balance_sheet().get_dataframe())
        income_statement = try_except(lambda: financials.get_income_statement().get_dataframe())
        cash_flow_statement = try_except(lambda: financials.get_cash_flow_statement().get_dataframe())
        statement_of_changes_in_equity = try_except(lambda: financials.get_statement_of_changes_in_equity().get_dataframe())
        statement_of_comprehensive_income = try_except(lambda: financials.get_statement_of_comprehensive_income().get_dataframe())

        # Initialize the CustomCompanyFiling object to return
        sec_filing_object = SECFilingObject(
            filing = sec_filing,
            file_number=sec_filing.file_number, 
            filing_html = "",
            markdown = sec_filing.markdown(),
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

        return sec_filing_object

    finally:
        rate_limiter.release()   


def get_filing(filing_id, filing_date) -> FilingObject:

    ticker, filing_year, filing_type = filing_id.split("-")
    if filing_type == "10K": filing_type = "10-K"
    elif "10Q" in filing_type: filing_type = "10-Q"
    else: raise Exception(f"Unsupported filing type {filing_type}")
    filing = FilingObject(ticker=ticker, filing_date=filing_date, filing_type=filing_type, filing_year=filing_year)
    return filing 


def filing_splitter(filing : SECFilingObject, fin_statements, chunk_size = 10000, chunk_overlap = 3, table_prepend_k = 3, verbose = False):
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
    intro_chunks = [] # Intro chunks list
    intro_chunk_buffer = "" 
    outro_chunks = ""
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
                    intro_chunks.append(intro_chunk_buffer)
                    # Empty the buffer
                    intro_chunk_buffer = ""
                    # Prepend certain number of last EDGARTOOLS chunk of the created intro chunk
                    # to the buffer for creating an overlap between chunks 
                    for prep in range(chunk_overlap):
                        if i - (chunk_overlap - prep) > 0:
                            intro_chunk_buffer += rows[i - (chunk_overlap - prep)]["Text"]+"\n"
            # Flag is raised, therfore we are processing outro
            else:    
                outro_chunks += row["Text"] + "\n"
        # We got to the first chunk that was identified to be a part of a filing's item
        else: 
            # Append the intro chunk buffer for the last time
            if not intro_complete: 
                intro_chunks.append(intro_chunk_buffer)
                intro_chunk_buffer = ""   
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
        chunk_metadata_model["chunk_description"] = "Overview_of_the_document"
        intro_chunk = {
                "metadata": dict(chunk_metadata_model),
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
        # Ended processing EDGARTOOLS chunks for Item 
        # Reset buffer 
        data = []

    return final_chunks