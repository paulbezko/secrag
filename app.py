
import warnings

warnings.filterwarnings("ignore")
from langchain_core import globals as langchain_config
langchain_config.set_verbose(False)

langchain_config.set_debug(False)

from dotenv import load_dotenv
from flask import Flask, request
import json
from flask_socketio import SocketIO
from flask import Response
from langchain.callbacks.manager import CallbackManager
from langchain_community.llms import OpenAI
from langchain.memory import *
from langchain_community.document_loaders import TextLoader, JSONLoader
from langchain_openai import OpenAIEmbeddings

from langchain_text_splitters import CharacterTextSplitter
from utils.json_utils import *
from rag import rag_with_memory_and_docs






app = Flask(__name__)

app.config["SECRET_KEY"] = "test_secret"
socketio = SocketIO(app, cors_allowed_origins="*")

app.config['OPENAI_API_KEY'] = ''

load_dotenv(".env", override=True)
# loader = TextLoader("documents/new_doc.txt")
# documents = loader.load()
# text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
# docs = text_splitter.split_documents(documents)
# embeddings = OpenAIEmbeddings()
memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True,  output_key='answer')

from utils.custom_streaming_callback_handler import CustomStreamingCallbackHandler, streaming_call_bp

app.register_blueprint(streaming_call_bp)
 

@app.route('/ask')
def ask():
    
    # Retrieve GET args:
    prompt = request.args.get('prompt')
    uid = request.args.get('uid')
    conversation_id = request.args.get('cid')
    socket_id = request.args.get('socket_id')
    ticker = request.args.get('ticker')
    filing = request.args.get('filing')

    # We do not know what document is the request for if there is no ticker, filing, and conversation ID
    if (ticker == None and filing == None) and conversation_id == None:
        res_dict = {"error": "Missing Ticker or Filing for conversation initialization"}
        return res_dict
        
    # Get ticker information from the memory if conversation ID is known
    elif (ticker == None and filing == None) and conversation_id != None:
        ticker, filing = retrieve_conversation_filing_info(uid, conversation_id)
        
    # Load most recent filing if only ticker information is supplied
    if ticker and not filing:
        sec_filing = load_sec(ticker)
        filing = sec_filing.file_number

    # All logic for handling conversations (new or existing) is outsourced to its own function
    # The output is the conversation ID
    conversation_id = conversation_handler_json(uid, conversation_id, prompt, ticker, filing)

    # Some useful in the future code from examples
        # projectId = request.args.get('projectId', default="0")
        # sender = request.args.get('ip', default='00000')  
        # collection_name = "collection-" + str(1)
    
    # Load conversation memory file
    # USELESS???
    _, conversation_id = init_load_json_file_memory(uid, conversation_id, prompt, ticker, filing)
    
    # Define callback manager for output tokens
    callback_manager = CallbackManager([CustomStreamingCallbackHandler(id=socket_id)])
    
    # Ask the question to the custom RAG
    answer = rag_with_memory_and_docs(uid, conversation_id, prompt, callback_manager, ticker, filing)
    
    # Format output
    res_dict = {
        "question": prompt,
        "answer": answer,
    }

    return res_dict      


if __name__ == '__main__':
    
    socketio.run(app=app, host='0.0.0.0', debug=True, port=5000) # The variable can be used cause you imported definitions??
