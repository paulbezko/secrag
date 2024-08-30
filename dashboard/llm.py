import json
from dotenv import load_dotenv
from langchain.chains import create_history_aware_retriever, create_retrieval_chain, LLMChain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.document_loaders import WebBaseLoader, JSONLoader
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain.globals import set_verbose
from llm_prompt_templates import *
from utils.json_utils import *
from utils.vectorstore_utils import vectorstore_manager, load_sec
from utils.debug import debug_print
# from utils.json_utils import json_memory_loader

load_dotenv(".env", override=True)


set_verbose(True)


def main_llm_chain(uid, session, prompt, callback_manager, ticker, file_number):
    # Load filing data from SEC
    filing = load_sec(ticker, file_number)
    
    # Improve: ensure running in parallel
    rag_output = rag_with_memory_and_docs(uid, session, prompt, callback_manager, filing)
    public_db_agent_output = public_db_agent(uid, session, prompt, filing.company_name, callback_manager)
    
    combined_output = combine_output(uid, session, prompt, rag_output, public_db_agent_output, callback_manager)


    return {
        "input" : prompt,
        "rag_context" : rag_output["context"],
        "rag_output" : rag_output["answer"],
        "public_db_agent_output" : public_db_agent_output.content,
        "react_output" : combined_output.content,
    }

  
def rag_with_memory_and_docs(uid, session, prompt, callback_manager, filing):
    print("\n-----------RAG AGENT------------")
    # Initialize LLM
    # llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=1, openai_api_key='', streaming=True, callback_manager=callback_manager)
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=1, openai_api_key='')

    
    # Pass filing data to vectorstore manager
    #
    # It will load saved vectorstore if the filing was already embedded
    # It will create and save new vectorstore if the filing was not embedded yet
    vectorstore = vectorstore_manager(filing)

    # Set up a retriever 
    retriever = vectorstore.as_retriever(similarity_search_with_score=True, k=3)

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
        {"input": " The context is from the following SEC filing: (ticker: "+filing.ticker+", filing: "+filing.file_number+")"+prompt},
        # Configuration for retrieving memory
        config={
            "configurable": {"session_id": str(session)+id_separator+uid, },
            
        },
    )
    
    # append_message_to_json_file(uid, session, {"role": "user", "content": prompt})
    # append_message_to_json_file(uid, session, {"role": "assistant", "content": answer["answer"]})
    print("-----------------------------------")    

    return answer

def public_db_agent(uid, session, prompt, company_name, callback_manager):
    print("\n-----------PUBLIC AGENT------------")
    # Initialize LLM
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=1, openai_api_key='')

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
        {"input": "Company: "+company_name+"\n"+ prompt}, # Pass some info on the company the prompt is for
        # Configuration for retrieving memory
        config={
            "configurable": {"session_id": str(session)+id_separator+uid, },
            
        },
    )
    
    print("\n")
    print(answer.content)
    print("-----------------------------------")
    
    return answer
    

def combine_output(uid, session, input_prompt, llm_public_output, llm_private_output, callback_manager):
    
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=1, openai_api_key='', streaming=True, callback_manager=callback_manager)

    combinator_chain = react_combinator_prompt | llm   
    
    output = combinator_chain.invoke(
        {
           "input_prompt": input_prompt,
           "llm_public_context": llm_public_output,
           "llm_private_context": llm_private_output, 
        }
    )
    
    append_message_to_json_file(uid, session, {"role": "user", "content": input_prompt})
    append_message_to_json_file(uid, session, {"role": "assistant", "content": output.content})  
    
    return output
    
       
    

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
      
    return store[conversation_id]
