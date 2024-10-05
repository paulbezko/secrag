
from dotenv import load_dotenv
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.callbacks.manager import get_openai_callback
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from langchain.globals import set_verbose, set_debug

from .llm_prompt_templates import *
from .json_utils import *
from .vectorstore_utils import vectorstore_manager, load_sec
from .debug import debug_print
from .sec_utils import *

from server import socketio

from flask_socketio import emit

# Get the current directory of the script
current_dir = str(os.path.dirname(os.path.abspath(__file__)))

load_dotenv(".env", override=True)

# set_debug(True)
set_verbose(True)

# Pydantic model for the Contextual Question LLM
class ContextualOutput(BaseModel):
    """Key words and Chapter descriptions"""
    keywords: str
    chapter_descriptions: list
    balance_sheet: bool
    income_statement: bool
    cash_flow_statement: bool
    statement_of_changes_in_equity: bool
    statement_of_comprehensive_income: bool


def generate_usage_meta(cb):
    """Fucntion to transform the callback object into a json-like dictionary"""
    usage_meta = {
        "total" : {
            "cost" : cb.total_cost,
            "tokens" : cb.total_tokens,
            "prompt_tokens" : cb.prompt_tokens,
            "completion_tokens" : cb.completion_tokens
        }
    }
    return usage_meta


def main_llm_chain(uid, session, prompt, callback_manager, ticker, file_year, chunk_size = 5000, chunk_overlap = 1000, k = 3, table_prepend_k = 3, ready_filing = None):
    """
    Main function to generate output from LLM given user prompt, SEC filing context, and chat history (STOPPED SUPPORT FOR CHAT HISTORY).

    Parameters
    ----------
    uid : str
        Unique identifier for the session
    session : str
        Session string
    prompt : str
        User's prompt
    callback_manager : CallbackManager
        Manager for OpenAI callbacks to track usage data
    ticker : str
        Ticker symbol of the company
    file_year : int
        Year of the filing
    chunk_size : int, optional
        Size of the chunks of text to process, by default 5000
    chunk_overlap : int, optional
        Amount of overlap between chunks of text, by default 1000
    k : int, optional
        Number of documents to retrieve from the vectorstore, by default 3
    table_prepend_k : int, optional
        Number of table rows to prepend to the output, by default 3
    ready_filing : dict, optional
        Pre-loaded filing, by default None

    Returns
    -------
    dict
        Dictionary containing the input, output, context, and usage metadata
    """

    # Load filing data from SEC
    if ready_filing:
        filing = ready_filing
    else: 
        filing = load_sec(ticker, file_year)
    
    # Disabled public agent and combinator
    public_db_agent_output = None
    combined_output = None

    # Callback for usage data retrieval
    with get_openai_callback() as cb:
        rag_output = rag_with_memory_and_docs(uid, session, prompt, callback_manager, filing, chunk_size, chunk_overlap, k, table_prepend_k)

    # Store as conversation memory
    append_message_to_json_file(uid, session, {"role": "user", "content": prompt})
    append_message_to_json_file(uid, session, {"role": "assistant", "content": rag_output["answer"]})  

    # Generate usage meta for performance assessment
    usage_meta = generate_usage_meta(cb) 

    if public_db_agent_output and combined_output:
        # CURRENTLY STOPPED SUPPORTING
        return {
            "input" : prompt,
            "rag_context" : rag_output["context"],
            "rag_output" : rag_output["answer"],
            "public_db_agent_output" : public_db_agent_output.content,
            "react_output" : combined_output.content,
            "usage_meta" : usage_meta
        }
    else:
        return {
            "input" : prompt,
            "rag_context" : rag_output["context"],
            "rag_output" : rag_output["answer"],
            "public_db_agent_output" : "",
            "react_output" : rag_output["answer"],
            "usage_meta" : usage_meta
        }        

  
def rag_with_memory_and_docs(uid, session, prompt, callback_manager, filing : CustomCompanyFiling, chunk_size = 5000, chunk_overlap = 1000, k = 3, table_prepend_k = 3):
    """
    This function implements the RAG agent with memory and documents. It takes a user prompt and generates an answer
    based on the context of the SEC filing with the given ticker and year. The context is retrieved in chunks and
    filtered based on the keywords extracted from the user's prompt. The output is a JSON object containing the final
    context objects and the answer string.

    Parameters:
        uid (str): The user ID
        session (str): The session ID
        prompt (str): The user's prompt
        callback_manager (CallbackManager): The callback manager for streaming the output to the client
        filing (CustomCompanyFiling): The SEC filing object
        chunk_size (int): The size of each chunk of text retrieved from the filing
        chunk_overlap (int): The overlap between chunks
        k (int): The number of context pieces to retrieve
        table_prepend_k (int): The number of table headers to prepend to the context

    Returns:
        dict: A dictionary containing the final context string and the answer string
    """
    print("\n-----------RAG AGENT------------")

    # Initialize metadata model for retrieving context for particular filing
    metadata_model = {
        "ticker": filing.ticker, 
        "year": filing.filing_year,
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        "table_prepend_k": table_prepend_k
    }

    # Initialize LLM
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0, openai_api_key='')

    # Integrated Pydantic
    llm_contextual = contextualize_q_prompt | llm.with_structured_output(ContextualOutput)

    # Chain for generating retriever input
    contextual_answer = llm_contextual.invoke({
        "prompt" : prompt,
        "chapter_descriptions_list" : tenK_descriptions # Currently only supports 10-k
    })

    # The answer will contain booleans for financial statements needs
    need_for_financials = [contextual_answer.balance_sheet, contextual_answer.cash_flow_statement, contextual_answer.income_statement, contextual_answer.statement_of_changes_in_equity, contextual_answer.statement_of_comprehensive_income]

    # Integrated new SEC splitter 
    vectorstore = vectorstore_manager(filing, chunk_size=chunk_size, chunk_overlap=chunk_overlap, k=k, table_prepend_k=table_prepend_k)
    
    # Intialize final contexts string to be used by the QA
    final_contexts = ""

    # Returns financials contexts according to needs of the prompt
    financials_contexts = process_need_for_financials(vectorstore, need_for_financials, metadata_model)
    print("Retrieved financials number:", len(financials_contexts))

    # Initialized for returning separate context objects (Documents) for debugging
    contexts_as_objects = financials_contexts

    # Add financials contexts to final_contexts
    for i in financials_contexts:
        final_contexts += i.page_content + "\n"

    # Retrieve regular contexts
    contexts = vectorstore.similarity_search_with_score(contextual_answer.keywords, k=k, filter=metadata_model, fetch_k=1000)
        
    print(f"Retrieved context number for {contextual_answer.keywords}:",len(contexts))

    # Add as objects for debugging
    contexts_as_objects += [c[0] for c in contexts]
    
    # Add to final context string
    for piece in contexts:
            # Add only unique contexts
            if piece[0].page_content not in final_contexts:
                final_contexts += piece[0].page_content + "\n"


    # Added a callback manager to stream the output to the client
    qa_llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0, openai_api_key='')
    
    # Initialize the QA chain 
    question_answer_chain = qa_prompt | qa_llm
    
    debug_print(session, id_separator, uid)

    # Grand-finale
    buffer = ''
    socket_id = callback_manager
    for chunk in question_answer_chain.stream({"input": prompt, "ticker": filing.ticker, "filing": filing.file_number, "context": final_contexts}):
        buffer += chunk.content
        socketio.emit('llm_response', {'word': chunk.content}, to=socket_id)
        

    return {
        "context": contexts_as_objects,
        "answer": buffer
    }


def process_need_for_financials(vectorstore, need_for_financials, metadata_model):
    """
    Returns financials contexts according to needs of the prompt:

    supported financials: [
        "balance_sheet", 
        "cash_flow_statement", 
        "income_statement", 
        "statement_of_changes_in_equity", 
        "statement_of_comprehensive_income"
    ]

    The list of booleans should be in the same order as the supported financials

    If an item in the list is true this is considered as a request
    to retrieve a financial corresponging to the ID of an item

    Args:
        vectorstore (VectorStore): vectorstore object
        need_for_financials (list): list of booleans indicating
            whether the corresponding financial statement is needed
        metadata_model (dict): metadata model for the vectorstore

    Returns:
        list: list of Document objects of the retrieved financials
    """
    # the metadata model requires a chapter description
    metadata_model_w_chapter_description = {
        "ticker": metadata_model["ticker"], 
        "year": metadata_model["year"],
        "chunk_size": metadata_model["chunk_size"],
        "chunk_overlap": metadata_model["chunk_overlap"],
        "table_prepend_k": metadata_model["table_prepend_k"],
        "chapter_description": ""
    }

    supported_financials = ["balance_sheet", "cash_flow_statement", "income_statement", "statement_of_changes_in_equity", "statement_of_comprehensive_income"]
    contexts = []
    
    # Returns financials contexts according to needs of the prompt
    #
    # The list of booleans should be in the same order as the supported_financials
    #
    # If an item in the list is true this is considered as a request
    # to retrieve a financial corresponging to the ID of an item
    for i, state in enumerate(need_for_financials):

        if state is True:
            metadata_model_w_chapter_description["chapter_description"] = supported_financials[i]
            statement = vectorstore.similarity_search("", k=1, filter=metadata_model_w_chapter_description, fetch_k=1000)
            if len(statement) > 0:
                print("got context for", supported_financials[i])
            contexts += statement
    
    return contexts


# CURRENTLY STOPPED SUPPORTING
#
def public_db_agent(uid, session, prompt, company_name, callback_manager, file_year):
    print("\n-----------PUBLIC AGENT------------")
    # Initialize LLM
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=1, openai_api_key='')

    # Initialize Chain
    conversation_chain = public_db_agent_prompt | llm
    
    # Create runnable
    runnable = RunnableWithMessageHistory(
        conversation_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )
    answer = runnable.invoke(
        {"input": f"Company: {company_name}\nDo not use information after and including the year {file_year}\n" + prompt}, # Pass some info on the company the prompt is for
        # Configuration for retrieving memory
        config={
            "configurable": {"session_id": str(session)+id_separator+uid, },
            
        },
    )
    
    return answer
    
# CURRENTLY STOPPED SUPPORTING
#
def combine_output(uid, session, input_prompt, llm_public_output, llm_private_output, callback_manager):
    
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=1, openai_api_key='', streaming=True, callback_manager=callback_manager)

    combinator_chain = react_combinator_prompt | llm   

    output = combinator_chain.invoke(
        {
        "input_prompt": input_prompt,
        "llm_public_context": llm_public_output,
        "llm_private_context": llm_private_output, 
        }
    )

    return output
    
          
# CURRENTLY STOPPED SUPPORTING
#
# Function used by chains to retrieve relevant history
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    store = {}
    # We pass identifiers as one string with a separator since the function only allows one "session_id" input
    # Therefore we derive identifiers from session identifier
    conversation_id, user_id = session_id.split(id_separator)
    
    # initialize new Chat message history if conversation is not recognized
    if conversation_id not in store:
        store[conversation_id] = ChatMessageHistory()
    store[conversation_id].clear()

    # Load conversation history from json file
    json_memory_loader(user_id, conversation_id, store[conversation_id])  
    store[conversation_id].clear()
    return store[conversation_id]



