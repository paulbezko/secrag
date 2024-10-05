from langchain.callbacks.manager import CallbackManager
from langchain.memory import *
from flask import Response, request, stream_with_context, Blueprint
import sys
from langchain_community.llms import OpenAI
from typing import Any
from flask_socketio import emit
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains.llm import LLMChain

streaming_call_bp = Blueprint('streaming_call', __name__, template_folder='templates')

class CustomStreamingCallbackHandler(StreamingStdOutCallbackHandler):
    def __init__(self, id):
        self.socket_id = id

    def get_socket_id(self):
        return self.socket_id
        
    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:

        if self.socket_id != None:
            emit('llm_response', {'word': token}, to=self.socket_id)

    @streaming_call_bp.route('/streaming/call')
    def stream_chat_gpt():

        prompt = request.args.get('prompt')
        projectId = request.args.get('projectId')
        sender = request.args.get('ip', default='00000')

        response = Response(stream_with_context(chat_gpt_helper(prompt, projectId, sender)),
                            mimetype='text/event-stream')
        response.headers['Cache-Control'] = 'no-cache'

        return response
    
def chat_gpt_helper(prompt, projectId, sender):
    try:
        custom_callback_handler = CustomStreamingCallbackHandler() # Instantiate the callback handler

        llm_chain = LLMChain(
            llm=OpenAI(model_name="gpt-3.5-turbo", temperature=0.3, streaming=True, callbacks=[custom_callback_handler]),
            prompt=prompt,
            verbose=True,
            memory="",
        )

        result = llm_chain.run(prompt)

    except Exception as e:
        print(e)
        return str(e)