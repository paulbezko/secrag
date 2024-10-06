
import warnings

from .utils.sec_utils import FilingInfo

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



def ask_(
        prompt, 
        human_prompts_history,
        uid, 
        conversation_id, 
        socket_id, 
        filing_date, 
        
        # Optional args
        chunk_size = 10000, 
        chunk_overlap = 3, 
        k = 8, 
        table_prepend_k = 3, 
        ready_filing = None
        ):

    print(socket_id)

    # We do not know what document is the request for if there is no ticker, filing, and conversation ID
    # if (not ticker or not filing_date or not filing_type):
    #     res_dict = {"error": "Missing Ticker or Filing Year or Filing Type"}
    #     return res_dict
    
    filing_type = "10-K"

    filing_info = create_filing_info_for_new_chat(conversation_id, filing_date)
  
    
    # Ask the question to the custom RAG
    answer = main_llm_chain(uid, conversation_id, prompt, human_prompts_history, filing_info, socket_id, chunk_size, chunk_overlap, k, table_prepend_k, ready_filing)



    return answer


def create_filing_info_for_new_chat(conversation_id, filing_date) -> FilingInfo:

    ticker, filing_year, conversation_id_filing_form = conversation_id.split("-")
    if conversation_id_filing_form == "10K": filing_type = "10-K"
    elif "10Q" in conversation_id_filing_form: filing_type = "10-Q"
    else: raise Exception(f"Unsupported filing type {conversation_id_filing_form}")
    
    filing_info = FilingInfo(ticker=ticker, filing_date=filing_date, filing_type=filing_type, filing_year=filing_year) 
    return filing_info  

if __name__ == '__main__':
    
    prompt = "What is the market segmentation"
    uid = "planetchars@gmail.com"
    conversation_id = "AAPL-2016-10K"
    filing_date = "2016-10-26"
    socket_id = None

    # Return error on LoadSEC
    ask_(
        prompt = prompt,
        uid = uid,
        conversation_id = conversation_id, 
        filing_date = filing_date
    )
    # socketio.run(app=app, host='0.0.0.0', debug=True, port=5000) # The variable can be used cause you imported definitions??

