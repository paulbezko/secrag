from .vectorstore import get_vectorstore
from .secedgar import get_filing
from pydantic import BaseModel
from typing import Literal, List
from server import socketio, llm

system_prompt_reformulate = """
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
system_prompt_rag_needed = """
    You are an expert in financial documents, particularly SEC filings such as 10-K and 10-Q reports. \
    The user is referencing the filing ID: {filing_id}. \
    Based on the following message, determine if the user is asking for information related to financial documents \
    specifically associated with this filing ID. \
    This includes details like balance sheets, income statements, cash flow statements, and any other relevant financial data typically found in SEC filings.
    
    Message: {reformulated_prompt}
    """
system_prompt_keywords_filings_tables = """
    You are a helpful assistant. Your task is to analyze the user's prompt and derive any useful keywords that can be used to answer their question.
    If the user is asking about specific financial statements like a balance sheet, income statement, etc., return those financial statements. If the user asks for multiple financial statements, return all that are relevant.

    Only return a filing_table_selection if the user is asking for or implying financial data related to a specific financial report, like a balance sheet or income statement. If no financial statement is implied, leave filing_table_selection empty.

    The output should be structured as:
        keywords: str
        filing_table_selection: Optional[List[Literal["balance_sheet", "income_statement", "cash_flow_statement", "statement_of_changes_in_equity", "statement_of_comprehensive_income"]]] = None

    User prompt:
    {reformulated_prompt}
    """
system_prompt_rag = """
    You are a highly knowledgeable financial assistant who helps users with financial queries, especially related to SEC filings, financial statements, and corporate reports. \
    Your role is to provide clear, concise, and detailed answers to any financial questions the user may have. \
    Your goal is to provide relevant financial data related to the user's prompt. \
    The context provided is from the SEC filing for {filing.ticker} (ticker: {filing.ticker}, filing date: {filing.filing_date}). \
    The context is as follows: {list_context_chunks}

    User prompt: {reformulated_prompt}
    """
system_prompt_not_rag = """
    You are a highly knowledgeable financial assistant who helps users with financial queries, especially related to SEC filings, financial statements, and corporate reports. \
    Your role is to provide clear, concise, and detailed answers to any financial questions the user may have. \
    However, if the user asks a question unrelated to finance, your goal is to politely steer the conversation back to financial topics, gently reminding the user that you specialize in finance. \
    You may give a brief, polite response to the unrelated question, but then guide the user back to finance-related matters.

    User prompt: {reformulated_prompt}
    """

# Pydantic model for rag need
class RagNeeded(BaseModel):
    relevant: bool

# Pydantic model for the Contextual Question LLM
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

    chunk_size = 10000
    k = 3
    chunk_overlap = 3
    table_prepend_k = 3

    # Creating filing info object
    filing = get_filing(filing_id, filing_date)

    # Reformatting user message history and most recent message into a single prompt
    system_prompt = system_prompt_reformulate.format(filing_id=filing_id, user_prompt=user_prompt, message_history=message_history, user_email=user_email)
    reformulated_prompt = llm.invoke(system_prompt).content

    # Determining if RAG is needed for the answer
    system_prompt = system_prompt_rag_needed.format(filing_id=filing_id, reformulated_prompt=reformulated_prompt)
    bool_rag_needed = llm.with_structured_output(RagNeeded).invoke(system_prompt).relevant

    # Handle a case where the reformulated prompt is relevant to the filing
    if bool_rag_needed:
        
        # Get keywords and filing table selection
        system_prompt = system_prompt_keywords_filings_tables.format(reformulated_prompt=reformulated_prompt)
        prompt_keywords_and_filing_tables = llm.with_structured_output(KewordsFilingTables).invoke(system_prompt)

        # Getting vectorsore to get context chunks from
        vectorstore = get_vectorstore(filing, new_chat=False, chunk_size=chunk_size, chunk_overlap=chunk_overlap, table_prepend_k=table_prepend_k)

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
            
        system_prompt = system_prompt_rag.format(filing=filing, reformulated_prompt=reformulated_prompt, list_context_chunks=list_context_chunks)

        buffer = ""
        for chunk in llm.stream(system_prompt):
            buffer += chunk.content
            socketio.emit('llm_response', {'word': chunk.content}, to=socket_id)
        
    # Handle a case where the reformulated prompt is unrelated to the filing itself
    else:
        system_prompt = system_prompt_not_rag.format(reformulated_prompt=reformulated_prompt)
        buffer = ""

        for chunk in llm.stream(system_prompt):
            buffer += chunk.content
            socketio.emit('llm_response', {'word': chunk.content}, to=socket_id)

    # Finishing the response
    socketio.emit('llm_response_complete', to=socket_id)