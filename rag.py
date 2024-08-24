import json
from dotenv import load_dotenv
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.document_loaders import WebBaseLoader, JSONLoader
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.globals import set_verbose
from rag_prompt_templates import *
from utils.json_utils import *
from utils.vectorstore_utils import vectorstore_manager, load_sec
from utils.debug import debug_print
# from utils.json_utils import json_memory_loader

load_dotenv(".env", override=True)


set_verbose(True)

### Custom RAG chain ###
def rag_with_memory_and_docs(uid, session, prompt, callback_manager, ticker, file_number):
    
    # Initialize LLM
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=1, openai_api_key='', streaming=True, callback_manager=callback_manager)

    # Load filing data from SEC
    filing = load_sec(ticker, file_number)
    
    # Pass filing data to vectorstore manager
    #
    # It will load saved vectorstore if the filing was already embedded
    # It will create and save new vectorstore if the filing was not embedded yet
    vectorstore = vectorstore_manager(filing)

    # Set up a retriever 
    retriever = vectorstore.as_retriever(similarity_search_with_score=True, k=5)

    # Create a history-aware retriever 
    #
    # This will work with conversation memory to rephrase a prompt to include an answer 
    # if it is provided in the memory
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )

    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    # Create a RAG chain
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    # Set up a RAG chain runnable
    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )
    
    debug_print(session, id_separator, uid)
    
    answer = conversational_rag_chain.invoke(
        {"input": prompt+" (ticker: "+ticker+", filing: "+file_number+")"},
        # Configuration for retrieving memory
        config={
            "configurable": {"session_id": str(session)+id_separator+uid, },
            
        },
    )
    
    append_message_to_json_file(uid, session, {"role": "user", "content": prompt})
    append_message_to_json_file(uid, session, {"role": "assistant", "content": answer["answer"]})

    return answer

# Function used by RAG chain to retrieve relevant history
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
      
    return store[conversation_id]
