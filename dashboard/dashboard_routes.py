
import warnings

warnings.filterwarnings("ignore")
from langchain_core import globals as langchain_config
langchain_config.set_verbose(False)

langchain_config.set_debug(False)

from dotenv import load_dotenv
from flask import Blueprint, Flask, jsonify, request
from flask_socketio import SocketIO
from langchain.callbacks.manager import CallbackManager
from langchain_community.llms import OpenAI
from langchain.memory import *
from .utils.json_utils import *
from .utils.llm import main_llm_chain

dashboard_llm_bp = Blueprint('dashboard_llm', __name__, template_folder='templates')

load_dotenv(".env", override=True)

from .utils.custom_streaming_callback_handler import CustomStreamingCallbackHandler, streaming_call_bp

dashboard_llm_bp.register_blueprint(streaming_call_bp)

@dashboard_llm_bp.route('/ask')
def ask():
    
    # Retrieve GET args:
    prompt = request.args.get('prompt')
    uid = request.args.get('uid')
    conversation_id = request.args.get('cid')
    socket_id = request.args.get('socket_id')
    ticker = request.args.get('ticker')
    filing = request.args.get('filing')
    
    
    answer = ask_(prompt, uid, conversation_id, socket_id, ticker, filing)    
    context_list = []
    for i in answer["rag_context"]:
        context_list.append(
            {
                "page_content" : i.page_content,
                "metadata" : i.metadata
            }
        )
    answer["rag_context"] = context_list
    return jsonify({'message': 'OK'}), 200



def ask_(prompt, uid, conversation_id, socket_id, ticker, filing_year, chunk_size = 10000, chunk_overlap = 3, k = 8, table_prepend_k = 3, ready_filing = None):

    # We do not know what document is the request for if there is no ticker, filing, and conversation ID
    if (not ticker or not filing_year):
        res_dict = {"error": "Missing Ticker or Filing Year"}
        return res_dict
        
    conversation_id = "{}-{}".format(ticker.upper(), str(filing_year))    
    
    # Define callback manager for output tokens
    callback_manager = CallbackManager([CustomStreamingCallbackHandler(id=socket_id)])
    
    # Ask the question to the custom RAG
    answer = main_llm_chain(uid, conversation_id, prompt, callback_manager, ticker, filing_year, chunk_size, chunk_overlap, k, table_prepend_k, ready_filing)

    return answer  
