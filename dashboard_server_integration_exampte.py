
import warnings

from dotenv import load_dotenv
from flask import Flask, request
from flask_socketio import SocketIO
from dashboard.dashboard_routes import dashboard_llm_bp


app = Flask(__name__)

socketio = SocketIO(app, cors_allowed_origins="*")

load_dotenv(".env", override=True)


app.register_blueprint(dashboard_llm_bp)
 

if __name__ == '__main__':
    
    socketio.run(app=app, host='0.0.0.0', debug=True, port=5000) # The variable can be used cause you imported definitions??
