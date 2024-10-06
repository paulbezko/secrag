
import warnings

warnings.filterwarnings("ignore")
from langchain_core import globals as langchain_config
langchain_config.set_verbose(False)

langchain_config.set_debug(False)

from dotenv import load_dotenv
from flask import Blueprint, Flask, request
from flask_socketio import SocketIO
from langchain.callbacks.manager import CallbackManager
from langchain_community.llms import OpenAI
from langchain.memory import *
from .utils.json_utils import *
from .utils.llm import main_llm_chain
from .utils.sec_utils import FilingInfo

dashboard_llm_bp = Blueprint('dashboard_llm', __name__, template_folder='templates')

app = Flask(__name__)

app.config["SECRET_KEY"] = "test_secret"
socketio = SocketIO(app, cors_allowed_origins="*")

app.config['OPENAI_API_KEY'] = ''

load_dotenv(".env", override=True)

from .utils.custom_streaming_callback_handler import CustomStreamingCallbackHandler, streaming_call_bp

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
    
    return ask_(prompt, uid, conversation_id, socket_id, ticker, filing)    



def ask_(prompt, uid, conversation_id, socket_id, filing_date, filing_type, chunk_size = 10000, chunk_overlap = 3, k = 8, table_prepend_k = 3, ready_filing = None):

    print(socket_id)

    # We do not know what document is the request for if there is no ticker, filing, and conversation ID
    if (not ticker or not filing_date or not filing_type):
        res_dict = {"error": "Missing Ticker or Filing Year or Filing Type"}
        return res_dict
    
    filing_type = "10-K"
    supported_filing_forms = ["10K", "10Q"]
    ticker, filing_year, conversation_id_filing_form = conversation_id.split("-")
    if conversation_id_filing_form in supported_filing_forms:
        if conversation_id_filing_form == "10K": filing_type = "10-K"
        elif conversation_id_filing_form == "10Q": filing_type = "10-Q"
    else:
        raise Exception(f"Unsupported filing type {conversation_id_filing_form}")
    
    filing_info = FilingInfo(ticker=ticker, filing_date=filing_date, filing_type=filing_type, filing_year=filing_year)
  
    
    # Ask the question to the custom RAG
    answer = main_llm_chain(uid, conversation_id, prompt, filing_info, socket_id, chunk_size, chunk_overlap, k, table_prepend_k, ready_filing)

    return answer

if __name__ == '__main__':
    
    prompt = "What is the market segmentation"
    uid = "planetchars@gmail.com"
    conversation_id = "AAPL-2016-10K"
    filing_date = "2016-10-26"
    socket_id = None

    # Return error on LoadSEC
    ask_(prompt, uid, conversation_id, filing_date)
    # socketio.run(app=app, host='0.0.0.0', debug=True, port=5000) # The variable can be used cause you imported definitions??
