from ...general.utils import log
from .vectorstore import vectorstore_manager
from .secedgar import get_filing
from ..shared import stop_signals
from pydantic import BaseModel
from typing import Literal, List
from server import socketio, llm

system_prompt_keywords = """
    You are an expert in financial documents, particularly SEC filings such as 10-K and 10-Q reports. You are presented with a current request and the latest chat messages from a human.
    
    Based on the following message, determine if the user is asking for information related to specific financial tables (e.g., balance sheet, income statement, cash flow statement) within this filing ID. This includes selecting relevant tables such as balance sheets, income statements, or cash flow statements, as well as identifying other key financial terms not directly tied to specific tables.
    
    When deciding, consider the following guidelines:
    
    - If the user is asking for specific financial documents (e.g., "show me the balance sheet"), populate the **filing_table_selection** field with the relevant tables such as 'balance_sheet', 'income_statement', or 'cash_flow_statement'.
    - If the user's message references financial data that could span multiple tables (e.g., "What do you think about their liquidity?"), add the specific table(s) related to that concept and populate the **keywords** field with other relevant financial terms (e.g., 'liquidity', 'assets').
    - Ensure precision in determining what the user is asking for, and only fill **filing_table_selection** with tables specifically related to the question. Use **keywords** for related terms not directly referencing specific tables.
    - If the question is unrelated to financial documents or tables, leave both **filing_table_selection** and **keywords** empty.
    
    Return the following:
    
    - Populate **filing_table_selection** with the relevant financial tables.
    - Populate **keywords** with other financial terms that are relevant but do not correspond to a specific table.

    Chat history: {message_history}
    Latest message: {user_prompt}
    Filing ID: {filing_id}
    """
system_prompt_rag = """
    You are a highly knowledgeable financial assistant who helps users with financial queries, especially related to SEC filings, financial statements, and corporate reports. \
    Your role is to provide clear, concise, and detailed answers to any financial questions the user may have. \
    Your goal is to provide relevant financial data related to the user's prompt. \
    The context provided is from the SEC filing for {filing.ticker} (ticker: {filing.ticker}, filing date: {filing.filing_date}). \
    The context is as follows: {list_context_chunks}

    Chat history: {message_history}
    Latest message: {user_prompt}
    """
system_prompt_not_rag = """
    You are a highly knowledgeable financial assistant who helps users with financial queries, especially related to SEC filings, financial statements, and corporate reports. \
    Your role is to provide clear, concise, and detailed answers to any financial questions the user may have. \
    However, if the user asks a question unrelated to finance, your goal is to politely steer the conversation back to financial topics, gently reminding the user that you specialize in finance. \
    You may give a brief, polite response to the unrelated question, but then guide the user back to finance-related matters.

    Chat history: {message_history}
    Latest message: {user_prompt}
    """


class Keywords(BaseModel):
    keywords: list[str] = []
    filing_table_selection: List[Literal[
        "balance_sheet", 
        "income_statement", 
        "cash_flow_statement", 
        "statement_of_changes_in_equity", 
        "statement_of_comprehensive_income"
    ]] = []

# Getting assistant response
def get_assistant_response(user_prompt, message_history, filing_id, socket_id, filing_date):

    print(f"Prompt: {user_prompt}")
    print(f"Message history: {message_history}")

    chunk_size = 10000
    k = 3
    chunk_overlap = 3
    table_prepend_k = 3

    # Creating filing info object
    filing = get_filing(filing_id, filing_date)

    system_prompt = system_prompt_keywords.format(filing_id=filing_id, user_prompt=user_prompt, message_history=message_history)
    prompt_keywords = llm.with_structured_output(Keywords).invoke(system_prompt)

    # Handle a case where rag is not needed
    if prompt_keywords.keywords == [] and prompt_keywords.filing_table_selection == []:
        system_prompt = system_prompt_not_rag.format(user_prompt=user_prompt, message_history=message_history)
        stream_response(system_prompt, socket_id)

    else:
        # Getting vectorsore to get context chunks from
        vectorstore = vectorstore_manager.vectorstore

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
        if len(prompt_keywords.filing_table_selection) > 0:
            for table in prompt_keywords.filing_table_selection:
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
            # "chunk_description": "",
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "table_prepend_k": table_prepend_k
        }

        keywords = " ".join(prompt_keywords.keywords)
        list_retrieved_chunks = vectorstore.similarity_search_with_score(keywords, k=k, filter=chunk_metadata_model, fetch_k=1000)
        for chunk in list_retrieved_chunks:
            if chunk[0].page_content not in list_context_chunks:
                list_context_chunks += chunk[0].page_content + "\n"
            
        system_prompt = system_prompt_rag.format(filing=filing, user_prompt=user_prompt, message_history=message_history, list_context_chunks=list_context_chunks)
        stream_response(system_prompt, socket_id)

    # Finishing the response
    socketio.emit('llm_response_complete', to=socket_id)


def stream_response(system_prompt, socket_id):

    buffer = ""
    for chunk in llm.stream(system_prompt):
        if stop_signals.get(socket_id): break
        buffer += chunk.content
        socketio.emit('llm_response', {'word': chunk.content}, to=socket_id)

    stop_signals.pop(socket_id, None)